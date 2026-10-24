# EmDash 升级手册（laobaiblog）

## 版本检查
- 声明版本：package.json dependencies（emdash、@emdash-cms/cloudflare 等，^ 前缀）
- **实装版本：node_modules/<pkg>/package.json 的 "version"**（声明 ^0.36.0 但锁死 0.36.0，声明≠实装）
- 最新版：`npm view emdash version`、`npm view @emdash-cms/cloudflare version`
- 状态（2026-10-10）：本地 0.36.0，上游 1.2.0，跨越 0.37 / 1.0 / 1.1 / 1.2 四个版本

## upgrade-emdash CLI（1.2 新增）
```
npx upgrade-emdash@latest --dry-run   # 先看计划，不改文件
npx upgrade-emdash@latest             # 装包 + 写 .emdash/UPGRADE.md 工单
```
- 解析所有直接 emdash / @emdash-cms/* 依赖，保留 ^/~ 前缀风格；任一步失败自动还原
- 需要 emdash >= 0.35；不支持 Yarn PnP；选项 --json / --yes
- dry-run 实测输出（2026-10-10）：emdash 0.36.0→1.2.0、@emdash-cms/cloudflare 0.36.0→1.2.0、plugin-forms 0.2.5→0.2.9、plugin-webhook-notifier 0.2.0→0.2.3（365 条 release entries）

## 升级前必查的破坏性变更（1.2 upgrade notes，未标 breaking 但会咬人）
1. **entry.id 带 locale 前缀**（#3922）：多 locale + Cloudflare DB（D1/DO/Hyperdrive）站点上 entry.id 恒为 `zh/xxx` 形式。laobaiblog 有多处用 `post.id` 拼 `/posts/${post.id}` 链接（posts/index.astro、category/[slug].astro、tag/[slug].astro、rss.xml.ts、posts/[slug].astro 相关文章）→ 升级前改成 `entry.data.slug`（search.astro 已在用 slug）
2. **plugin:install/activate 钩子**（#3785）：升级后首次启动会对 admin 里从未启用/禁用/改过 MCP 权限的插件执行一次。检查 forms、webhook-notifier 钩子幂等；钩子抛错会禁用插件（Plugins 页可重新启用）
3. **Site URL 行为**（#3744）：未配 siteUrl/EMDASH_SITE_URL 环境变量时，邮件链接改用 Settings>General 的 Site URL。本站 options 表 `emdash:site_url` 已 = https://blog.laobaitv.net，安全；seed 若含 settings.url 需删
4. sitemap 分片 2000 条/片（本站文章少，无影响）
5. 视频 block 需求（本站未用，无影响）

## 本站相关的修复收益（升级动机）
- webhook-notifier 0.2.3：sandboxed 插件设置页恢复加载（#3362）、comment:afterCreate 后台写不再被 Worker 截断（#3631）——本站 webhook-notifier 正是 sandboxed 运行
- 后台写走 waitUntil：redirect 计数、404 日志、API token 最后使用时间不再丢
- D1 `too many SQL variables`：标签 >~30 个不再炸（#3889）
- 冷启动加快（startup 检查并行化）；`admin.locales` 可裁剪 ~220KB JS
- 0.37 的 registry 校验（checksum/签名/provenance）是供应链加固

## 升级步骤
1. `wrangler d1 export` 备份
2. 完成代码前置（entry.id→data.slug）
3. `npx upgrade-emdash@latest`，按 .emdash/UPGRADE.md 工单走
4. `npm run deploy`
5. 验证：首页、文章页、RSS、后台登录、评论 webhook、语言切换（若保留多语言）
