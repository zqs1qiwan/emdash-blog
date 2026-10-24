# EmDash 多语言机制 & laobaiblog 单语言回退

## 三层架构（0.36 实测）
1. **数据层（EmDash 管）**：条目带 locale 字段，每种语言一条独立 D1 记录，靠 slug 关联（同一 slug 在 ec_posts 里 zh/en 各一行）。`getTranslations(collection, id)` 返回其他语言版本（slug + status）。查询必须显式传 locale（getEmDashEntry/getEmDashCollection 的 locale 参数）——**公开请求不会自动注入 locale**，不传时 fallback 到 default locale（项目 commit 5b19936 修的就是这个）
2. **路由层（Astro i18n）**：astro.config.mjs 的 i18n 块。defaultLocale zh + `prefixDefaultLocale: false` → zh 无前缀；en 生成 /en/*；`fallback: {en: zh}` + `fallbackType: rewrite` → en 找不到内容时内部改写为 zh 内容（URL 保持 /en/，内容中文）
3. **UI 文案层（站点自建，与 EmDash 无关）**：src/utils/i18n.ts strings 表 + formatDate locale 感知，按 Astro.currentLocale / Astro.locals.locale 取。是模板层实现，删掉不影响 EmDash 数据

## 站点标题不随语言变
`site:title` 在 D1 options 表，全局单值。/en/ 页面外壳是英文但站点标题仍是"老白的博客"——数据层全局设置所致，非 bug

## 内容现状（2026-10-10 回退后）

zh 2 篇（wordpress-to-emdash、cloudflare-birthday-week-2026-reasearch），**en 记录已全部删除**，/en/ 路由已移除。回退详情见下方步骤。

## 回退到单语言 zh（✅ 已执行 2026-10-10）

1. astro.config.mjs 删 i18n 块
2. src/utils/i18n.ts 重写为 zh-only：`export const ui = {...}` 常量对象 + `formatDate(date)` 单签名（无 locale 参数）
3. Base.astro 删语言切换按钮（nav-lang，含 3 处 CSS 规则：主样式/hover/移动端 grid 定位）+ getTranslations 逻辑 + `<html lang>` 固定 `"zh-CN"`；LiveSearch slot 直接引用 `ui.searching` / `ui.searching` / `ui.searchNoResults`
4. 8 个页面/组件（index、posts/index、posts/[slug]、pages/[slug]、category、tag、404、PostCard、search）：`uiT(locale)` → `ui`、`formatDate(x, locale)` → `formatDate(x)`、删 `locale: Astro.currentLocale` 查询参数、删 `locale === "zh" ? ... : ...` 三元改纯中文。**regex 批量替换后必须检查 import 路径**（`../utils/i` vs `../../utils/i` 因目录深度不同，批量脚本会把深层页面的路径改错，posts/index.astro 踩过）
5. D1 删 en 记录：`DELETE FROM ec_posts WHERE locale='en';`（先备份：`wrangler d1 export` 撞 FTS5 会失败，用逐表 `SELECT * --json` dump 到 /opt/data/tmp/backup-*/）
6. 部署后验证：`/en/*` 全部 404、首页 grep 无 `nav-lang`/`Switch language`、`lang="zh-CN"`
- 本站无外链保护需求，未做 /en/ 302 兜底；如需保留改为 rewrite 到 /
- 回退后升级 1.2.0：entry.id locale 前缀问题消失（单语言下 id 无前缀），模板 `/posts/${post.id}` 链接无需改造

## 升级 1.2.0 时的 i18n 相关变化（0.36 时代的坑不再适用）

- `entry.id` 在多语言 + D1 下现在**总是**带 locale 前缀（#3922）；模板自拼链接应改用 `entry.data.slug`（单语言站 id 无前缀，可暂不改）
- `getTranslations` 相关逻辑 1.2 仍存在；本站回退单语言后已全部移除
