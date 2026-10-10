# AGENTS.md

给 AI agent（Claude Code / Codex / MCP 等）操作这个仓库的工作说明。

## 项目概要

EmDash CMS 博客，Astro SSR + Cloudflare Workers（D1/R2/KV/Worker Loader）。**单语言中文站**（2026-10 移除了 i18n 与 /en/ 路由）。内容存 D1，**写文章不需要部署**；只有改代码才需要。

## 常用命令

```bash
npm install                      # 安装（workers-types v5 后已无 peer 冲突）
npx astro dev                    # 本地开发 (localhost:4321)
npx astro build                  # 构建 → dist/
npx wrangler deploy              # 部署（会优先读 dist/server/wrangler.json）
# 或 git push 到 main：Workers Builds 自动 build+deploy
npx wrangler tail                # 看线上实时日志（调试 500 必备）
npx wrangler d1 execute <db> --remote --command "SQL"   # 查线上数据
```

## 关键约定

- **部署链路陷阱**：`astro build` 把资源配置（worker 名/D1/R2 绑定）烘焙进 `dist/server/wrangler.json`，`wrangler deploy` 优先读它而非根目录 `wrangler.jsonc`。改过任何资源名/配置后必须重新 build 再 deploy。
- **UI 文案**：集中在 `src/utils/i18n.ts`（导出 `ui` 常量与 `formatDate(date)`）。新增页面禁止硬编码文案，一律引用 `ui.xxx`。
- **LiveSearch**：加载/无结果文案用 slot 覆盖（`<fragment slot="loading">`），组件默认是英文。
- **内容查询**：用 `getEmDashCollection`（支持 orderBy/where/limit），标签批量查询用 `getTermsForEntries`（避免 N+1）。
- ** Portable Text**：内容是结构化 JSON（block/code/table 类型），不是 HTML。渲染用 `<PortableText value={...} />`。
- **样式**：CSS 设计令牌在 `src/styles/tokens.css`（颜色/字号/间距变量），改主题色改那里，别在组件里写死色值。

## 代码结构

```
src/
├── layouts/Base.astro          # 全局布局：导航、页脚、主题切换
├── pages/
│   ├── index.astro             # 首页（featured + 6 宫格）
│   ├── posts/[slug].astro      # 文章详情（TOC/作者/相关文章）
│   ├── pages/[slug].astro      # 独立页面（about 等）
│   ├── search.astro            # 搜索页（FTS5）
│   ├── category/[slug].astro   # 分类归档
│   ├── tag/[slug].astro        # 标签归档
│   ├── rss.xml.ts              # RSS（language=zh）
│   └── 404.astro
├── components/PostCard.astro
└── utils/{i18n,reading-time,site-identity}.ts
wrangler.jsonc                  # 部署配置（开源版，无账号信息）
astro.config.mjs                # 集成/插件配置
seed/seed.json                  # 初始 schema + 示例内容
```

## 已知问题与修复记录

- ~~getTranslations 返回对象~~（i18n 已移除，此问题不存在了）
- EmDash admin 有前端缓存，改后端后看不到新功能先硬刷新
- D1 里内容表有 `ec_` 前缀（ec_posts/ec_pages），options 表存 `site:title` 等 K-V（JSON 字符串值）

## 数据库操作注意

直接改 D1 数据（如修 locale）用：
```bash
npx wrangler d1 execute my-emdash-blog-db --remote --command "UPDATE ..."
```
改完内容相关的数据后，站点有 object cache（KV），如果前台没生效，等 cache TTL 过期或清 KV 中 settings/collection 相关 key。

## 不要做

- 不要在开源文件里提交真实账号 ID/域名（account_id、routes.zone_name 等留在本地配置）
- 不要直接改 `dist/` 下的产物
- 不要在免费计划账号上保留 `worker_loaders`（Dynamic Workers 付费功能，deploy 会失败）
