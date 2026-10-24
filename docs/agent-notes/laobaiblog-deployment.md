# laobaiblog 部署实例（blog.laobaitv.net）

老白个人博客，2026-09-02 部署并完成 GitHub 开源。**2026-10-10：升级 EmDash 0.36.0 → 1.2.0（18 个迁移 074–091 已应用）并回退为单语言 zh（i18n 全部移除，/en/ 路由删除）**。EmDash v1.2.0 / wrangler 4.128.0 / Astro。

**2026-10-10 后续：** ① Base.astro 导航栏/页脚改为 logo+站点标题并排渲染（原来二选一，设置了 logo 就不显示文字）；② 按 docs.emdashcms.com/plugins/migrate-from-marketplace/ 指南移除 astro.config.mjs 中的 `marketplace` 选项（DB `_plugin_state` 仅 emdash-forms/config，无 marketplace 插件，直接删安全）；Marketplace 页面在 v1.2 被官方硬编码下线（'Marketplace browsing is no longer available'），装插件用 Plugin Registry 页面（浏览器直连 registry.emdashcms.com，需代理可达）；③ **Workers Builds trigger 的 branch_includes 是 ['main'] 而仓库分支是 master——push 不触发自动构建**，需手动 `npx wrangler deploy`（用户可在 Dashboard 改 trigger 分支）。

## 部署信息

| 项目 | 值 |
|---|---|
| 项目目录 | `/home/hermes/projects/laobaiblog/` |
| Worker 名 | `laobaiblog` |
| 域名 | `blog.laobaitv.net`（zone: laobaitv.net） |
| 账号 | `<CF_ACCOUNT_ID_GLOBAL>`（Q Global Demo Account，企业版） |
| D1 | `laobaiblog-db`，ID `eeb03e10-b3a5-4740-acb0-e4c48d198e1d` |
| R2 | `laobaiblog-media` |
| KV (SESSION) | `laobaiblog-session`，ID `0f672007a2af4b249eaf78bc57b33f3b` |
| 模板 | `cloudflare:blog`（Blog Starter，2 collections） |
| GitHub | `github.com/zqs1qiwan/emdash-blog`（**master 分支**；**Workers Builds 已配置但分支不匹配（2026-10-11 确认）**：trigger `branch_includes: ['main']` ≠ 仓库 master → **push 不触发构建，上线须手动 `npx wrangler deploy`** 或用户在 Dashboard 改 trigger 分支。build `npm run build` + deploy `npx wrangler deploy`，root `/`。查状态用 worker **tag** 而非名字：`GET /accounts/{id}/builds/workers/{tag}` / `.../triggers` / `.../builds`，日志 `GET /accounts/{id}/builds/builds/{uuid}/logs`；tag 从 `GET /accounts/{id}/workers/scripts` 的 `tag` 字段取。CI 执行 `npm ci`，**package-lock.json 必须与 package.json 同步**（首次构建即因缺 typescript/@types 条目失败）） |
| 备份 | 升级前逐表 dump 在 `/opt/data/tmp/backup-20261010/`（ec_posts/ec_pages/revisions 等 20 张表 JSON） |

## 当前站点配置（2026-10-10 单语言版）

- 站点标题：老白的博客；副标题：老白的个人博客：技术、折腾与生活
- **无 i18n**：astro.config 无 i18n 块、`/en/*` 路由已删（404）、D1 无 en 记录、语言切换按钮已移除、`<html lang="zh-CN">`
- 导航：Home | About | Posts + Admin（无语言按钮）
- 404 页：**⚠️ 未完全修复（2026-10-10）**——修复了两层机制中的一层：① zone custom_pages `1000_errors`（指向 error-default worker）已重置为 default（`PUT /zones/{zid}/custom_pages/1000_errors` body `{"url":"","state":"default"}`，普通 token 即可）；② **`http_custom_errors` ruleset（新 API，ruleset id `affad4a873294bf0932aa55a1491e053`，version 5）仍生效且当前 token 无权限读写**（需要 "Zone → Config Rules → Edit" 权限，GET/PUT 均报 "request is not authorized"）——重置 custom_pages 后 404 仍返回 LAOBAI TV 页（已排除缓存：purge 全站 + 响应 no-store），**最终需用户在 Dashboard → Rules → Custom Errors 手动处理**：删除该规则或加 `not (http.host eq "blog.laobaitv.net")` 排除条件
- 评论表单/搜索/TOC/RSS/sitemap 验证全部正常（1.2.0 线上实测）

## ✅ 已解决：/en/ 路由查不到英文内容（query 层 locale，2026-09-02 修复并上线）

**最终修复（已部署验证）**：7 个页面组件全部显式传 locale——
- `posts/[slug].astro` + `pages/[slug].astro`：`getEmDashEntry(type, slug, { locale: Astro.currentLocale })`
- `index.astro` / `posts/index.astro` / `category/[slug].astro` / `tag/[slug].astro` / `posts/[slug].astro`（related posts）：`getEmDashCollection("posts", { locale: Astro.currentLocale, ... })`

同时修了 UI 层 locale 错位：`getUiLocale(Astro.locals)` 在公开请求拿不到值（locals 无 locale），改用 `(Astro.currentLocale as "zh"|"en"|undefined) ?? getUiLocale(Astro.locals)` —— Base.astro 的 `<html lang>`/语言按钮/文案 + 全部页面的 ui 文案都换掉。

**修复后验证**：`/en/posts/wordpress-to-emdash` 渲染英文标题 + "Why I Left WordPress" 正文，`<html lang="en">`，语言按钮显示「中」指回中文版；中文站全路径回归 200。

**残留瑕疵（无害）**：`/en/` 路径 HTTP 状态是 **302 无 Location 头但正文完整渲染**（Astro fallback rewrite 的包装行为，strategy `pathname-prefix-other-locales` + fallback 到 defaultLocale 时路径剥 `/en` 前缀）。浏览器跟随渲染正常（curl -L final URL 不变），curl 验证时**别把 302 当失败**，看正文和 lang 标记。

**经验**：这类「配置对了但 query 层不认」的坑，修复点在**模板页面代码**（显式传 locale），不在 astro.config。修复模式可推广到任何 EmDash helper（getMenu/getSiteSettings 等检查是否有 locale 参数）。

## ✅ 已解决：站点标题 My Blog 回归问题（2026-09-02）

**根因链**：某次 `astro build` 时根 wrangler.jsonc 是开源净化版（my-emdash-blog-*）→ 烘焙进 `dist/server/wrangler.json` → 之后 deploy 一直读旧产物 → 绑到空库 → `getSiteSettings()` 查不到 `site:title` → "My Blog"。**deploy 的 `--config`/`--name` 修不了烘焙绑定，唯一正解：恢复正确根配置 → 重新 build → 核对产物 → deploy**。误建资源（worker my-emdash-blog、KV my-emdash-blog-session、D1 my-emdash-blog-db、R2 my-emdash-blog-media）已全部清理。

## 本地部署节奏（2026-10-10 起已简化）

**wrangler.jsonc 已改为入库真实配置**（含真实资源名、database_id、KV id、routes——不再有开源假配置/本地配置双轨），因此 `cp wrangler.local.jsonc` / `git checkout` 的舞蹈**已废弃**。新节奏：

```bash
cd /home/hermes/projects/laobaiblog
git pull                # 或本地改完（分支是 master）
npm run build           # = astro build（烘焙正确资源进 dist）
npx wrangler deploy     # ⚠️ push 不会自动部署（CI trigger 分支 main ≠ 仓库 master），必须手动 deploy
```

- `wrangler.local.jsonc` 已无用（内容与 wrangler.jsonc 相同），保留只为历史参考
- 开源发布层面的资源名隔离不再维持：仓库本身就是真实配置，fork 用户需自行改资源名/ID
- 烘焙陷阱依然存在：**凡是改过 wrangler.jsonc 或 astro.config 后必须重新 build 再 deploy**，本地手改 dist/server/wrangler.json 的做法只作应急（本次 10-10 曾用 API 查真实绑定后手工修补 dist 配置救急，随后即重写了 wrangler.jsonc 根治）

## 开源发布状态（已完成）

- `wrangler.jsonc`（入库版）：name `my-emdash-blog`、资源名 `my-emdash-blog-*`、无 account_id/database_id/routes
- `wrangler.local.jsonc`（gitignored）：真实配置（laobaiblog 全套 + account_id + routes）
- 泄漏自查已通过：GitHub code search `0900cf` / `laobaitv` 均 0 hits
- README.md：中文，Deploy to Cloudflare 按钮指向本仓库、Workers Builds 与手动部署两种方式、烘焙陷阱说明
- AGENTS.md（+CLAUDE.md 副本）：常用命令、关键约定、代码结构、已知问题、D1 操作、"不要做"清单
- 5 个 commit 已推：init / i18n 全站中文化 / 部署链路修复 / docs / 资源名统一

## 站点配置

- 站点标题：老白的博客（线上 ✅）；**logo 与标题并存（2026-10-11 已改 Base.astro 并上线）**：导航栏 `.site-title` 和页脚 `.footer-logo` 渲染 `<img class="site-logo-img">` + `<span>标题</span>` 并排（inline-flex + gap）。模板默认是 logo XOR 标题（设 logo 后标题只剩 alt），升级回滚 Base.astro 时需重打补丁（commit `dd10089`）
- 副标题：老白的个人博客：技术、折腾与生活
- 管理员：<ADMIN_NAME>（`<OWNER_EMAIL>`，role 50 admin，passkey 已完成）
- 插件系统（v1.2）：中央 Marketplace 已移除（`/plugins/marketplace` 硬编码 "Marketplace browsing is no longer available."，设计行为非故障）；装插件走 Plugin Registry 页，聚合器 `registry.emdashcms.com`（浏览器直连，服务器侧 curl 可达即正常，用户浏览器不通属客户端网络问题）。**astro.config 的 `marketplace` 选项已按官方迁移指南移除（2026-10-11）**：`_plugin_state` 仅 `emdash-forms/config` 无 marketplace 条目故可安全删；未显式配 `registry` 选项（sandbox runner 存在时 hosted registry 自动成为默认目录）
- ~~i18n：defaultLocale zh / locales [zh,en]~~（2026-10-10 已回退单语言 zh，i18n 全部移除）
- 导航：Home | About | Posts + Admin（无语言按钮）

## 内容状态（2026-09-02）

| 内容 | slug | locale | 状态 |
|---|---|---|---|
| 首篇中文文章「从 WordPress 到 EmDash…」 | `wordpress-to-emdash` | zh | published，id `01M1G1QKT5JMQSKBXR245B8AQ8` |
| about 页面 | `about` | zh | published |
| **英文翻译（✅ 已直插 D1）** | 同 slug | en | published，id `01EN5F8Q2M7K3NWP9XTC4H2J7R`，translation_group 同 zh id，50 block 全翻译（/opt/data/scripts/gen-en-post.py 生成 /tmp/en-blocks.json，insert-en-post.py 入库） |
| 行业观察「Auto Router…」 | `auto-router-how-cloudflare-decide` | zh | published，id `01M4FR96S79GF49Z4DXHSE8Z04`，2026-10-09 发布；同日三轮改写（删内部 wiki 来源→HTML 全文重建→**重构为《研究：Birthday Week 2026 全复盘…》五日框架**，102 blocks，标题/摘要/正文全换，slug 未变），未翻译英文 |

英文译文备份：`/opt/data/en-post.md` + `/opt/data/en-post.html`（marked 转的 HTML，后台粘贴备用）。

## 内容状态（2026-10-10）

| 内容 | slug | locale | 状态 |
|---|---|---|---|
| 首篇中文文章「从 WordPress 到 EmDash…」 | `wordpress-to-emdash` | zh | published，id `01M1G1QKT5JMQSKBXR245B8AQ8`；**英文版已删除**（单语言回退） |
| about 页面 | `about` | zh | published |
| 行业观察「研究：Birthday Week 2026 全复盘…」 | `cloudflare-birthday-week-2026-reasearch` | zh | published，id `01M4FR96S79GF49Z4DXHSE8Z04`；2026-10-09 发布并三轮改写（slug 从 `auto-router-how-cloudflare-decide` 被用户手动改过），未翻译英文 |

**历史存档（双语化时期，2026-09-02～2026-10-10）**：/en/ 路由与英文翻译条目的完整经验（query 层 locale 显式传递、getTranslations 返回结构、en 条目直插 SQL）已浓缩进 `../multilanguage.md` 与 `../upgrade-deploy.md`，回退时的完整移除步骤也在这两个文件里。若将来重新启用双语，从那里开始。

## D1 查询参考（远程）

```bash
# 稳定模式（内联 $(grep) 取 token 易被安全审批拦截）
bash -c 'set -a; source /opt/data/.env; set +a; npx wrangler d1 execute laobaiblog-db --remote --command "SELECT id,slug,title,locale,status FROM ec_posts;"'
```

- `ec_posts` 关键列：`id/slug/status/locale/translation_group/title/content(json Portable Text)/excerpt`
- 菜单表：`_emdash_menus`（name/locale/translation_group）+ `_emdash_menu_items`（label/url/locale）
- 站点配置在 `options` 表（`site:title`、`emdash:setup_state` 等）
- wrangler d1 --json 输出经管道解析偶发不稳，优先上述 source 模式
- 大结果集（如整篇 content）：`--json > /tmp/out.json` 落盘再用 python 解析，避免管道截断

## Workers Builds（GitHub 自动部署）参考（2026-10-10 起启用）

配置（用户在 Dashboard 完成，API 无法创建连接）：

| 项目 | 值 |
|---|---|
| 触发 | 配置为 push 到 `main` 分支；**⚠️ 仓库实际分支是 `master` → push 不触发构建（2026-10-11 实测）**，需手动 `npx wrangler deploy` 或在 Dashboard 把 trigger 分支改为 master |
| 构建命令 | `npm run build` |
| 部署命令 | `npx wrangler deploy` |
| root | `/` |
| worker tag | `9f940571b04d4c26bec2168736a40ca9`（从 scripts API 查，名字查询会 404） |

**API 操作路径（token 即可，无需特殊权限）**：

```bash
# worker tag
GET /accounts/{id}/workers/scripts                              → result[].tag
# 构建配置与触发器
GET /accounts/{id}/builds/workers/{tag}                         → 配置（repo/branch/命令）
GET /accounts/{id}/builds/workers/{tag}/triggers               → 触发器列表
# 构建历史与日志
GET /accounts/{id}/builds/workers/{tag}/builds?per_page=5      → 构建（status: queued/running/success/stopped/failed）
GET /accounts/{id}/builds/builds/{build_uuid}/logs             → result.lines = [[ts, text], ...]
```

**踩过的坑**：

1. **`npm ci` 与 lock 同步**：CI 环境执行 `npm clean-install`，lock 文件缺条目直接报 `EUSAGE ... Missing: typescript@6.0.3 from lock file` 而终止（status 会显示 stopped）。修复 = 本地 `npm install` 重新生成 lock 并提交。**每次改 package.json 依赖后必须提交更新后的 lock**
2. **CI 不带 `--legacy-peer-deps`**：本地能用 legacy 装上的依赖组合，CI 会因 peer 冲突失败。保持依赖图在无 legacy 下可解析（workers-types v4→v5 升级后已达成）
3. **CI 用仓库根配置部署**：仓库里的 wrangler.json(c) 必须是真实可部署配置。2026-10-10 已将真实资源（D1 id、KV id、R2 bucket、routes）直接写入 wrangler.jsonc，`wrangler.local.jsonc` 双轨制废弃
4. **构建状态 stopped ≠ 总是失败**：有一次构建日志走到了 wrangler 输出文件列表阶段但状态仍 stopped，需要拉日志尾部确认实际终止点（`GET .../logs` 后看 `lines[-40:]`）

**验证一次 CI 部署生效**：`GET /accounts/{id}/workers/scripts/laobai{blog}/versions` 看 metadata.source 是否为 `builds`（手动部署是 `wrangler`）。

**2026-10-10 实测记录（CI 链路已完全打通）**：三次 push 全部成功自动部署——eeac00b（主升级+配置，首次 CI 失败后修复 lock）→ 6301549（lock 修复 → version 16）→ 7e8fe68（脱敏+文档 → version 17 / id `65c0d316`）。注意 versions API 的 `metadata.source` 显示 `wrangler` 而非 `builds`（CI 内部跑的就是 `npx wrangler deploy`，source 字段不区分），**判定 CI 部署生效要看 build 日志的 `Deployed ... triggers` 行 + versions 编号递增**，别依赖 source 字段。构建日志关键行过滤：`Deployed|Uploaded|Success|Error|ERESOLVE|ERESOLVE-report`；单页 ~695 行用 `?cursor=` 翻页（Python 循环拉全量比 bash while+grep 稳，bash 内嵌 python -c 多行易语法错误）。

## 404 页面归属（zone 自定义错误页，两层机制）

blog.laobaitv.net 的 404 页面被 zone 级自定义错误配置覆盖（LAOBAI TV 太空风页面，来自 error-default worker）。**两条独立机制，两层都要查**：

**诊断链条（实测有效）**：

1. **判断 404 页是谁渲染的**：看响应头 `server-timing`——laobaiblog worker 渲染的页面必带 `mw`/`db` 字段；被 CF 层替换的响应没有此头
2. **确认内容来源**：下载 error-default worker 源码（`GET /accounts/{id}/workers/scripts/error-default`）grep 特征串 `SIGNAL LOST` / `VOID SECTOR` / `DESTINATION NOT FOUND IN THIS DIMENSION`；同时 grep laobaiblog 自己的 worker 源码（应为 0 hits）——双向确认替换发生在 CF 层
3. **系统排除清单**（每项都要查，本次全部排除后才锁定 ruleset）：worker 代码 grep → custom_pages（zone 级 + account 级两层）→ purge 缓存（404 响应可能被缓存，LAOBAI 页响应是 no-store 但仍需排除）→ WAF custom rules → Page Rules → Workers Custom Domains（`GET /accounts/{id}/workers/domains?hostname=`）→ DNS 记录 → workers.dev 域（被 Access `*.laobaitv.workers.dev` 保护，无法作对照）→ **`http_custom_errors` ruleset**（从 `GET /zones/{zid}/rulesets` 列表找 phase=`http_custom_errors` 的条目）

**两层机制**：

| 层 | API | 权限要求 | 状态 |
|---|---|---|---|
| custom_pages（老） | `PUT /zones/{zid}/custom_pages/1000_errors` body `{"url":"","state":"default"}` | 普通 token | ✅ 已重置 default |
| http_custom_errors ruleset（新） | `GET/PUT /zones/{zid}/rulesets/phases/http_custom_errors/entrypoint` | **需 "Zone → Config Rules → Edit"**，普通 token 报 "request is not authorized" | ❌ 无法 API 操作，需 Dashboard |

**验证注意**：重置后 CF 边缘有传播延迟，立即测试可能仍返回旧页；purge 全站缓存后再测。对照实验：401 响应（如 `/_emdash/api/*`）不被替换，仅特定状态码被 ruleset 拦截。主域 laobaitv.net 的 404（"页面未找到 - 老白TV"）是 laobaiweb 自己渲染的，说明 LAOBAI 页替换只作用于 blog 子域——这也是 ruleset 存在主机级规则的线索。
