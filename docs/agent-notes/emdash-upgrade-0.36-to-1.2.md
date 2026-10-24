# EmDash 升级：0.36.0 → 1.2.0（2026-10-09 调研，未执行）

laobaiblog 当前 emdash / @emdash-cms/cloudflare 均为 0.36.0，上游最新 1.2.0。中间跨 0.37（registry 验证、`_rev` 并发）、1.0（stable + 插件 registry）、1.1（发布日历、Microsoft 登录）、1.2（编辑器重做、视频块、域名迁移）四个版本、365 条 changelog。**已跑通 `upgrade-emdash --dry-run`（4 包升级计划正常），尚未执行实际升级。**

## 升级工具

```bash
npx -y upgrade-emdash@latest --dry-run   # 只看计划，不改文件
npx -y upgrade-emdash@latest             # 实际升级，写 .emdash/UPGRADE.md 工单
```

- 自动解析全部直接依赖 `emdash` / `@emdash-com-CMS-placeholder`（应为 `@emdash-cms/*`），保留 ^/~ 版本风格，更新 pnpm catalog，跑包管理器，失败自动还原
- 工单 `.emdash/UPGRADE.md` 含跨越版本的完整 changelog + migration 对比；有 migration 时要求 build 通过 + 可恢复备份后才准部署
- 要求已装 emdash ≥ 0.35；Yarn PnP 不支持

## 对 laobaiblog 的断点（按影响排序）

1. **`entry.id` 将始终带 locale 前缀**（#3922，多 locale + D1 站点）——升级后 `post.id` 变 `zh/<ulid>` 形式，模板里 `/posts/${post.id}` 建的链接全断。**受影响调用点（6 处）**：`posts/index.astro:51`、`category/[slug].astro:64`、`tag/[slug].astro:64`、`rss.xml.ts:20`、`posts/[slug].astro:266`（related posts）；`search.astro:56` 已用 `result.slug ?? result.id` 无需改。**正解：改用 `entry.data.slug`**（0.36 上已存在，可先改先验证，不必等升级）。
2. **`plugin:install`/`plugin:activate` hook 首次启动会跑一次**（#3785）——对从未在后台启用/禁用/改过 MCP 权限的插件。我们 config 里装了 forms + webhook-notifier(sandboxed)。hook 抛异常 → 插件被自动禁用并记日志，需到后台重新启用。
3. **Site URL / 邮件链接行为变化**（#3744）——未配置 `EMDASH_SITE_URL` 时邮件链接改用后台 Settings > General 的 Site URL 字段。升级后检查该字段指向 blog.laobaitv.net；`seed/seed.json` 若含 `settings.url` 要删。
4. **sitemap 分页**（#3806）：每 `/sitemap-{collection}.xml` 最多 2000 条续页。我们文章少，无影响。
5. **`_rev` 并发**（0.37）：admin 过期写入返回 409——正常行为；我们直接写 D1 绕过 API 不受影响。
6. **视频块**（#3827）：未使用，无影响。
7. **DB migration**：1.1.0→1.2.0 无 schema 变更；0.37→1.1 之间是否有 migration 以 UPGRADE.md 对比结果为准。

## 升级收益（我们直接受益的）

- **webhook-notifier 0.2.3**：sandboxed 插件设置页恢复加载（#3362）+ `comment:afterCreate` hook 走 `waitUntil` 不再被 Worker 截断（#3631）
- 后台写入统一走 `waitUntil`：redirect 计数、404 日志不再丢失
- D1 `too many SQL variables` 修复（#3889）：标签 >~30 个不再失败
- 冷启动更快（startup 并行化）；`admin.locales` 可裁剪语言包省 ~220KB JS
- 1.2 编辑器重做、集合分页、后台直接改域名

## 执行清单（待用户确认后走）

1. 先改 6 处 `post.id` → `post.data.slug`，0.36 上 build + deploy 验证链接不变
2. D1 备份：`npx wrangler d1 export laobaiblog-db --remote --output /opt/data/tmp/laobaiblog-backup-<date>.sql`
3. 走标准本地部署节奏（cp wrangler.local.jsonc → build → 核对 dist/server/wrangler.json → deploy → git checkout）
4. `npx -y upgrade-emdash@latest` → 按 `.emdash/UPGRADE.md` 工单逐条过
5. `npm run deploy`
6. 部署后验证：首页 200、`/en/posts/wordpress-to-emdash` 英文渲染、文章页（新 slug）、RSS `<language>zh</language>`、admin 登录（passkey）、评论提交 + webhook、Plugins 页两个插件未被禁用
7. 检查 Settings > General 的 Site URL；观察 `wrangler tail laobaiblog` 首启动日志有无 plugin hook 异常
