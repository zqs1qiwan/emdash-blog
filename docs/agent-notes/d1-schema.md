# laobaiblog D1 速查（laobaiblog-db）

## 表结构前缀
- 内容集合表：`ec_<collection>`（ec_posts、ec_pages）。列含 slug, locale, title, excerpt, content(Portable Text JSON), updated_at
- 系统表：`_emdash_*`（migrations、menus、seo、comments、media_usage、rate_limits、fts 等）
- **站点设置不在 ec_settings 也不在 _emdash_\***：在 `options` 表，key 形如 `site:title`、`emdash:site_url`
- 查表清单：`SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;`

## 已确认的 options 键（2026-10）
- `site:title` = "老白的博客"（全局单值，不随 locale 变 → /en/ 页面外壳英文但标题是中文的原因）
- `site:tagline`
- `emdash:site_url` = https://blog.laobaitv.net
- `emdash:exclusive_hook:comment:moderate`
- `emdash:setup_complete`、`system:scheduler:last_completed_at`

## 内容现状（2026-10）
- ec_posts：zh 2 篇（wordpress-to-emdash、cloudflare-birthday-week-2026-reasearch——用户拼写如此）+ en 1 篇（wordpress-to-emdash 的翻译）
- ec_pages：zh about 1 篇

## 查询工作流（避免 shell 引号地狱）
带双引号的 SQL 不要内联进 `bash -c '...'`（嵌套引号必然炸）。写 .sh 脚本文件再执行：

```bash
#!/bin/bash
# /opt/data/tmp/d1_pull.sh
cd /home/hermes/projects/laobaiblog
set -a; source /opt/data/.env; set +a
npx wrangler d1 execute laobaiblog-db --remote --json --command "SELECT ..." > /opt/data/tmp/out.json
```

## 解析 JSON 输出的坑
- 成功：`data[0]['results']` 是行数组
- 失败（如表不存在）：顶层是 `{'error': {...}}`，直接取 `[0]['results']` 会 KeyError——先判型
- 拉全文 content（数千字符 Portable Text）用 --command 可行，输出存文件再 python 解析

## 写入
- UPDATE 语句存 .sql 文件：`npx wrangler d1 execute laobaiblog-db --remote --file x.sql -y`
- SQLite 字符串字面量只转义单引号（`'`→`''`），反斜杠保持原样
- **写入后必须 curl 线上验证内容真的变了**——曾出现 SQL 文件生成成功但执行的是旧文件、线上仍是旧版的情况
