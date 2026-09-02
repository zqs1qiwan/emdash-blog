# EmDash Blog

基于 [EmDash CMS](https://github.com/emdash-cms/emdash) 的个人博客，部署在 Cloudflare Workers，中英双语（中文为主，英文 `/en/` 前缀）。

[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/zqs1qiwan/emdash-blog)

## 架构

```
浏览器 → Cloudflare 边缘 → Worker (Astro SSR)
                          ├─ D1  (内容 + FTS5 全文搜索)
                          ├─ R2  (图片媒体)
                          ├─ KV  (会话)
                          └─ Worker Loader (插件沙箱)
```

- **前端**：Astro 6 SSR，主题即 Astro 项目（搜索、RSS、标签、明暗模式、目录模板自带）
- **内容格式**：Portable Text（结构化 JSON），不是 HTML 富文本
- **i18n**：中文无 URL 前缀，英文带 `/en/`，sitemap 自动 hreflang；全站 UI 文案在 `src/utils/i18n.ts`
- **插件**：表单 + webhook 通知（跑在沙箱 isolate 里，只能用 manifest 声明的能力）

## 页面路由

| 页面 | 路由 |
|---|---|
| 首页 | `/` |
| 全部文章 | `/posts` |
| 单篇文章 | `/posts/:slug`（英文翻译 `/en/posts/:slug`） |
| 分类/标签 | `/category/:slug`、`/tag/:slug` |
| 搜索 | `/search` |
| 独立页面 | `/pages/:slug` |

## 部署

### 方式一：Workers Builds（Git 集成，推荐）

1. Fork 本仓库
2. Cloudflare Dashboard → Workers & Pages → Create → 连接 Git 仓库
3. 构建配置：Build command `npx astro build`，Deploy command `npx wrangler deploy`
4. 首次部署自动创建 `wrangler.jsonc` 里声明的 D1/R2/KV 资源（无需手动 database_id）
5. 之后 push 即自动部署

> **坑**：`astro build` 会把资源配置烘焙进 `dist/server/wrangler.json`，`wrangler deploy` 优先读它。改过 `wrangler.jsonc` 或 `astro.config.mjs` 的资源名后**必须重新 build**，否则部署会绑到旧资源。

### 方式二：本地手动部署

```bash
npm install --legacy-peer-deps   # 模板 workers-types pin 与新版 wrangler 有 peer 冲突

npx wrangler d1 create my-emdash-blog-db     # 把返回的 database_id 填进 wrangler.jsonc
npx wrangler r2 bucket create my-emdash-blog-media

npx astro build
npx wrangler deploy
# 首次访问 Worker 域名 → /admin/setup 引导：站点信息 → 管理员 → Passkey
```

自定义域名：取消 `wrangler.jsonc` 中 `routes` 的注释，填你的域名（需托管在同账号 CF）。

> `worker_loaders`（插件沙箱）需要付费计划的 Dynamic Workers；免费计划注释掉该块，其余功能不受影响。

## 内容更新

- **写文章**：`/admin` 后台写作，发布即生效，**无需重新部署**（内容在 D1）
- **改代码/主题**：push（Workers Builds）或 `npx wrangler deploy`
- **翻译**：文章编辑器右侧栏 Translations → Translate；站点语言在 `astro.config.mjs` 的 `i18n` 块配置

## 目录结构

```
src/
├── layouts/Base.astro      # 全局布局（导航/页脚/语言切换/主题）
├── pages/                  # 路由（index/posts/pages/search/tag/category/404）
├── components/PostCard.astro
├── utils/
│   ├── i18n.ts             # 全站 UI 文案（zh/en）+ locale 日期格式
│   ├── reading-time.ts     # 阅读时长（中英文分别计算）
│   └── site-identity.ts
└── styles/                 # tokens.css（设计令牌）+ theme.css
seed/seed.json              # 初始 schema + 示例内容（setup 向导导入）
wrangler.jsonc              # 部署配置（Workers Builds 直接可用）
```

## 本地开发

```bash
npm install --legacy-peer-deps
npx astro dev     # http://localhost:4321
```

## License

MIT
