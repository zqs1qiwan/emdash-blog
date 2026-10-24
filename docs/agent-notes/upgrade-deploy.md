# EmDash 升级与部署工作流

实测 2026-10-10：laobaiblog 0.36.0 → 1.2.0，同时移除 i18n 改单语言。完整流程与三个大坑。

## 升级流程（按序）

1. **备份 D1**（破坏性操作前必做）。`wrangler d1 export` 会直接失败：`cannot export databases with virtual tables (like FTS5)`（库里有 `_emdash_fts_*` 表）。替代方案：逐表 dump 成 JSON：
   ```bash
   for t in ec_posts ec_pages media revisions taxonomies content_taxonomies users options \
            _emdash_migrations _emdash_collections _emdash_fields _emdash_menus _emdash_menu_items \
            _emdash_taxonomy_defs _emdash_content_bylines _emdash_widget_areas _emdash_widgets; do
     wrangler d1 execute laobaiblog-db --remote --json --command "SELECT * FROM $t" > backup/$t.json
   done
   ```
   先拿全表清单：`SELECT name FROM sqlite_master WHERE type='table'`。
2. **数据清理**（按需）：删某语言记录 `DELETE FROM ec_posts WHERE locale='en'`（ec_pages 同理）。
3. **依赖升级**：首选 `npx upgrade-emdash@latest --yes`（1.2 新增 CLI，写 `.emdash/UPGRADE.md` 工作单）。坑：它内部跑 npm install 会撞 peer 冲突失败并回滚——先手动把 package.json 里 `@cloudflare/workers-types` 从 v4 pin 升到 `^5`，再 `npm install --legacy-peer-deps`，然后重跑 upgrade-emdash（此时它检测到已到位直接完成）。
4. **Migrations**：`npx emdash migrate --status --d1 <database_uuid>`。**必须传 `--d1 <uuid 或真实库名>`**——`--db binding=DB` / `--d1 DB`（binding 名）/ `--wrangler <config>` 都解析失败（报 "D1 migrations require an explicit database selector" 或 "No D1 database named DB exists"）。uuid 用 `wrangler d1 list` 查。应用时带 status 输出的 fingerprint：
   ```bash
   npx emdash migrate --d1 <uuid> --expected-target-fingerprint <fp> --yes
   ```
   实测 0.36→1.2 跨 18 个迁移（074_content_deleted_scheduled_index … 091_redirect_artifacts）。
5. **构建验证**：`npm run build`。`npx astro check` 需要装 @astrojs/check，在同样的 peer 冲突下装不上——直接用 build 当验证。
6. **部署**：见下一节。

## dist/server/wrangler.json 资源烘焙（最大坑）

`astro build` 把**开源假配置 wrangler.jsonc** 烘焙进 `dist/server/wrangler.json`——里面的 D1 database_id、R2 bucket、KV id 全是假值（`my-emdash-blog-db` 等不存在）。仓库根目录跑 `wrangler deploy` 优先读 `.wrangler/deploy/config.json` → `dist/server/wrangler.json`，直接部署报 `7404 database could not be found`。

部署三步：
1. **查线上 worker 真实绑定**（用 API，本地假配置不可信）：
   ```
   GET /accounts/{account_id}/workers/scripts/{worker_name}/settings
   ```
   从 bindings 读出 D1 id、R2 bucket_name、KV SESSION 的 namespace_id（假 config 里 KV 连 id 都没有）。
2. **修补 dist/server/wrangler.json**：换上真实 database_name/database_id/bucket_name/kv id；worker name、account_id、routes 从 wrangler.local.jsonc（私有配置，不入库）取值填入。
3. 仓库根目录 `npx wrangler deploy`。

**不要** `wrangler deploy --config wrangler.local.jsonc`：那会从源码打包，报 21 个 unresolved imports（astro:content、virtual:* 模块解析不到）。必须部署 build 产物。也不要 `cd dist/server && npx wrangler deploy`：会同时撞见 user config 和 deploy config 两个文件冲突。

## 部署后验证与 404 页陷阱

**全路径验证清单**：`/`、`/posts`、`/posts/<slug>`×2、`/pages/about`、`/rss.xml`、`/sitemap.xml`、`/search`、`/_emdash/admin`（期望 302→login）、`/_emdash/api/settings`（期望 401）、已删除路由（期望 404）。首页 grep `href="/posts/` 确认链接无 locale 前缀；`lang="zh-CN"`；语言切换按钮无残留。

**⚠️ laobaitv.net zone 的 404 页曾覆盖我们的模板（✅ 已修复 2026-10-10）**：zone custom_pages 的 `1000_errors` 曾指向 `error-default` worker（LAOBAI TV 太空风页面，含 Orbitron 字体/🌌 emoji/"SIGNAL LOST · VOID SECTOR"），worker 返回 404 时 CF 替换响应体。识别特征：响应头**无 `server-timing`**（正常 worker 渲染必带 mw/db 字段）、页面含 `cf-error-details`/`cf-wrapper` class。**修复**：`PUT /zones/{zid}/custom_pages/1000_errors` body `{"url":"","state":"default"}`（普通 token 可操作；注意 custom_pages 的 GET/PUT 可用，但 `http_custom_errors` ruleset 读取需要额外权限，token 常报 "request is not authorized"）。重置后 CF 边缘有传播延迟，立即验证可能仍见旧页

## Workers Builds（GitHub 自动部署）✅ 已配置（2026-10-10）

用户已在 Dashboard 连接 `zqs1qiwan/emdash-blog`（main 分支，build `npm run build` / deploy `npx wrangler deploy`）。API 实操要点：

- **查询必须用 worker tag 不是名字**：tag 从 `GET /accounts/{id}/workers/scripts` 的 `tag` 字段取（laobaiblog = `9f940571b04d4c26bec2168736a40ca9`），然后 `GET /accounts/{id}/builds/workers/{tag}`（配置）、`.../triggers`（触发器）、`.../builds`（历史）。用名字查报 12040/12000
- **构建日志**：`GET /accounts/{id}/builds/builds/{build_uuid}/logs` → `result.lines` 是 `[timestamp, text]` 数组
- **坑1：CI 跑 `npm ci`**，package-lock.json 必须与 package.json 严格同步（首次构建因 lock 缺 typescript/@types 条目报 `EUSAGE` 失败，status 显示 stopped）。改依赖后必须提交新 lock
- **坑2：CI 不带 `--legacy-peer-deps`**——依赖图必须无 legacy 可解析
- **坑3：CI 用仓库根 wrangler.json(c) 部署**，仓库配置必须真实可部署（本仓 2026-10-10 已改为真实配置入库，双轨制废除）
- 验证部署来源：`GET /accounts/{id}/workers/scripts/{name}/versions` 看 metadata.source = `builds`（CI）vs `wrangler`（手动）

历史查证方法（未配置时期）：`builds/workers/{name}` 报 no build configuration、builds 历史为空、versions 的 source 全为 `wrangler`、无专属 build token。Git 连接创建无 API 端点（workers-sdk#12058），只能 Dashboard 操作。

## 单语言简化 checklist（移除 i18n）

- `astro.config.mjs`：删 i18n 块
- D1：删非默认 locale 记录（ec_posts / ec_pages）
- `src/utils/i18n.ts`：字符串表改为单语常量对象 + 单签名 formatDate（去掉 locale 参数）
- `Base.astro`：删语言切换按钮、getTranslations、en/zh 三元判断；`<html lang="zh-CN">`
- 各页面/组件：`uiT(locale)` → `ui`；`formatDate(x, locale)` → `formatDate(x)`；删查询里的 `locale: Astro.currentLocale`
- **导入路径**：`pages/<子目录>/*.astro` 用 `../../utils/i18n` 不是 `../`——批量替换后必须 build 验证（实测漏了一处，build 报 Module not found）

## EmDash 多语言机制（0.36–1.2）

- **数据层**：每个 entry 有 locale 字段；多语言 = 同 slug 多条独立 D1 记录；`getTranslations(collection, id)` 返回其他语言版本（注意返回 `{translationGroup, translations[]}` 对象不是数组，直接 `.find()` 会 500）
- **查询层**：getEm* 需显式传 locale 过滤；公开侧不传时 fallback 到默认 locale（不自动注入——这是 2026-09-02 那次 fix 的根因）
- **路由层**：astro i18n 块控制 `/en/` 前缀与 fallback rewrite
- **站点标题/tagline** 存 options 表（`site:title`），不 per-locale——所以 /en/ 页面标题还是中文
- 1.2.0 起多 locale + D1 站点 `entry.id` 恒含 locale 前缀（#3922）；模板里拼链接应改用 `entry.data.slug`。单语言站点无此问题
