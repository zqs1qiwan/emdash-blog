#!/usr/bin/env python3
"""配图系统 v4：HTML 画布 1600x1000（正文）/ 1600x1200（封面），内容满宽不留空白。"""
import os

OUT = "/opt/data/news/figures/v4"
os.makedirs(OUT, exist_ok=True)

CSS = """
@font-face{font-family:SC;src:url('file:///opt/data/home/.local/share/fonts/NotoSansCJKsc-Regular.otf');font-weight:400}
@font-face{font-family:SC;src:url('file:///opt/data/home/.local/share/fonts/NotoSansCJKsc-Bold.otf');font-weight:700}
@font-face{font-family:M;src:url('file:///usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf');font-weight:400}
@font-face{font-family:M;src:url('file:///usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf');font-weight:700}
:root{--bg:#0B0C0E;--ink:#F2F2F0;--dim:#8A9099;--hair:#23282E;--acc:#FF5A1F;--acc2:#57B0A0;--panel:#121518}
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:var(--bg);color:var(--ink);font-family:SC;overflow:hidden;-webkit-font-smoothing:antialiased}
.f{width:1600px;height:1000px;padding:80px 100px 64px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:baseline;
  font:400 19px/1 M;letter-spacing:.14em;color:#5F6870;text-transform:uppercase}
h1{margin-top:30px;font:700 56px/1.18 SC;letter-spacing:-.012em}
h1 b{color:var(--acc);font-weight:700}
.sub{margin-top:18px;font:400 23px/1.55 SC;color:var(--dim);max-width:1300px}
.rule{margin-top:28px;height:1px;background:var(--hair);flex:none}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;padding-top:6px}
.foot{margin-top:auto;padding-top:22px;display:flex;justify-content:space-between;gap:48px;
  font:400 18px/1.55 M;color:#6B7480;letter-spacing:.01em}
.foot .r{color:#4E565E;white-space:nowrap}
"""

def page(body, h=1000, cls="f"):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="{cls}" style="height:{h}px">{body}</div></body></html>"""

def head(kick, title, sub=None, num=None):
    top = f'<div class="top"><div>{kick}</div><div>{num or ""}</div></div>'
    s = f'<div class="sub">{sub}</div>' if sub else ''
    return f'{top}<h1>{title}</h1>{s}<div class="rule"></div>'

def foot(left, right=""):
    return f'<div class="foot"><div>{left}</div><div class="r">{right}</div></div>'

# ---------------------------------------------------------------- W44 图1
def w44_f1():
    rows = [
        ("Gemini 4 Carbon", "59", "—", "—", False),
        ("Claude Opus 5.5", "58", "58", "58", False),
        ("Kimi K3.1 Pro", "—", "55", "55", False),
        ("GPT-6 Astra", "57", "53", "—", True),
        ("Gemini 4 Argon", "50", "53", "—", True),
        ("Claude Fable 5.1", "49", "53", "—", True),
    ]
    tr = []
    for name, a, b, c, diff in rows:
        cells = []
        for i, v in enumerate((a, b, c)):
            if v == "—":
                cells.append('<td class="na">—</td>')
            elif diff and i == 1:
                cells.append(f'<td class="df">{v}</td>')
            else:
                cells.append(f'<td>{v}</td>')
        tr.append(f'<tr><th>{name}</th>{"".join(cells)}</tr>')
    body = f"""
    <div class="tbl"><table>
      <thead><tr><th>模型</th><th>Google 发布表</th><th>AA 榜（媒体转述）</th><th>AA 站现状</th></tr></thead>
      <tbody>{"".join(tr)}</tbody></table></div>"""
    extra = """
    <style>
    .tbl{margin-top:6px}
    table{width:100%;border-collapse:collapse;font-family:M}
    thead th{font:400 19px/1 SC;color:#6B7480;text-align:right;padding:0 0 14px;letter-spacing:.04em}
    thead th:first-child{text-align:left}
    tbody th{font:400 30px/1 SC;color:var(--ink);text-align:left;padding:26px 0;border-top:1px solid var(--hair)}
    tbody td{font:700 44px/1 M;text-align:right;padding:26px 0;border-top:1px solid var(--hair);color:#D7DADE}
    tbody td.df{color:var(--acc)}
    tbody td.na{color:#3E454D;font-weight:400}
    </style>"""
    body = head("2026-W44 · AA INTELLIGENCE INDEX", "同一个指数，三个来源，<b>三套分数</b>",
                "橙色 = 两套口径之间差 3 分以上；破折号 = 该来源没有给出这个模型的分数", "图 1") + \
        f'<div class="body">{body}</div>{extra}' + \
        foot("Google DeepMind 发布页（10-28）· Simon Willison（10-23）· artificialanalysis.ai（10-30 抓取）",
             "AA Intelligence Index")
    return "w44-f1.html", body

# ---------------------------------------------------------------- W44 图2
def w44_f2():
    cols = [
        ("找", "SEC-bench Pro", "在真实软件里定位漏洞",
         [("Gemini 4 Carbon", 88.2, 1), ("GPT-6 Astra", 85.4, 0), ("Gemini 4 Argon", 83.4, 0)]),
        ("验", "ExploitGym", "验证漏洞是否可利用",
         [("Gemini 4 Carbon", 54.8, 1), ("GPT-6 Astra", 42.4, 0), ("Gemini 4 Argon", 42.0, 0), ("Claude Opus 5.5", 34.5, 0)]),
        ("修", "CWE-bench", "从根因生成补丁",
         [("Gemini 4 Carbon", 71.0, 1), ("GPT-6 Astra", 68.0, 0), ("Gemini 4 Argon", 68.0, 0),
          ("Claude Opus 5.5", 67.0, 0), ("Claude Fable 5.1", 58.0, 0)]),
    ]
    html = ['<style>.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:56px;width:100%}'
            '.c h3{font:700 26px/1 SC}.c h3 u{text-decoration:none;color:#6B7480;font:400 19px/1 M;margin-left:12px}'
            '.c .cap{margin-top:10px;font:400 18px/1.4 SC;color:#6B7480}'
            '.c .rows{margin-top:26px}'
            '.r{margin-bottom:30px}'
            '.r .nm{display:flex;justify-content:space-between;font:400 20px/1 SC;color:#C9CED3}'
            '.r .nm em{font:700 26px/1 M;font-style:normal}'
            '.r .tr{margin-top:12px;height:14px;background:#1A1E23}'
            '.r .tr i{display:block;height:14px;background:#454D57}'
            '.r.a .tr i{background:var(--acc)}'
            '.r.a .nm em{color:var(--acc)}'
            '</style>']
    for k, bench, cap, items in cols:
        rows = "".join(
            f'<div class="r{" a" if hot else ""}"><div class="nm"><span>{nm}</span><em>{v:.1f}</em></div>'
            f'<div class="tr"><i style="width:{v}%"></i></div></div>' for nm, v, hot in items)
        html.append(f'<div class="c"><h3>{k}<u>{bench}</u></h3><div class="cap">{cap}</div>'
                    f'<div class="rows">{rows}</div></div>')
    body = head("2026-W44 · CYBERSECURITY BENCHMARKS", "差距搬到了攻防链的<b>三段</b>",
                "同一张官方评测表内，已公开模型的最高与最低分差：找 4.8、验 20.3、修 13 个点", "图 2") + \
        f'<div class="body"><div class="cols">{"".join(html[1:])}</div>{html[0]}</div>' + \
        foot("Gemini 4 Carbon 官方评测表（2026-10-28）· 口径 evaluated without guardrails", "单位：通过率 %")
    return "w44-f2.html", body

# ---------------------------------------------------------------- W44 图3 / 图5：截图 + 侧栏
def shot(name, kick, title, sub, img, notes, foot_l, foot_r, num, img_w=860):
    li = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in notes)
    body = head(kick, title, sub, num) + f"""
    <div class="body"><div class="shot">
      <div class="ph"><img src="{img}"></div>
      <ul class="nt">{li}</ul>
    </div></div>
    <style>
    .shot{{display:grid;grid-template-columns:{img_w}px 1fr;gap:56px;align-items:center;width:100%;margin-top:4px}}
    .ph{{background:#0F1215;border:1px solid var(--hair);display:flex;align-items:center;justify-content:center;padding:14px}}
    .ph img{{max-width:{img_w - 28}px;max-height:672px;display:block}}
    .nt{{list-style:none}}
    .nt li{{border-top:1px solid var(--hair);padding:22px 0}}
    .nt li:first-child{{border-top:none;padding-top:0}}
    .nt b{{display:block;font:700 25px/1.35 SC;color:var(--ink)}}
    .nt span{{display:block;margin-top:10px;font:400 19px/1.6 SC;color:#8A9099}}
    </style>""" + foot(foot_l, foot_r)
    return name, body

# ---------------------------------------------------------------- W44 图4
def w44_f4():
    body = head("2026-W44 · PHP2SHELL · CVE-2026-109618 / 109619", "两千多万个靶子，<b>零次成功</b>",
                "左边是暴露面，右边是结果；两份数据来自两家机构，不能互相校验", "图 4") + """
    <div class="body"><div class="stat">
      <div class="box">
        <div class="k">暴露实例</div>
        <div class="v">2260<span>万</span></div>
        <div class="n">CVSS 4.0 均为 9.2；至少一个欧洲政府预防性下线站点</div>
      </div>
      <div class="box">
        <div class="k">走完整条利用链</div>
        <div class="v a">0<span>次</span></div>
        <div class="n">捕获到的尝试全部来自开源 exploit kit，两代链条均失败</div>
      </div>
    </div>
    <div class="bar"><div class="t"></div><div class="d">老链条撞 <em>post_max_size</em> 限制；新链条能稳定打爆内存，但拿不到后续阶段需要的地址泄露</div></div>
    </div>
    <style>
    .stat{display:grid;grid-template-columns:1fr 1fr;gap:72px;width:100%}
    .box{border-top:3px solid var(--hair);padding-top:26px}
    .box:first-child{border-top-color:#454D57}
    .box:last-child{border-top-color:var(--acc)}
    .k{font:400 22px/1 SC;color:#8A9099;letter-spacing:.02em}
    .v{margin-top:24px;font:700 168px/.9 M;letter-spacing:-.02em}
    .v span{font:700 46px/1 SC;margin-left:16px;color:#6B7480}
    .v.a{color:var(--acc)}
    .v.a span{color:#8A5040}
    .n{margin-top:26px;font:400 21px/1.6 SC;color:#8A9099;max-width:640px}
    .bar{margin-top:52px;display:flex;gap:28px;align-items:flex-start;border-left:3px solid #2A3038;padding-left:26px}
    .bar .t{font:700 21px/1.5 SC;color:var(--ink);white-space:nowrap}
    .bar .d{font:400 21px/1.6 SC;color:#8A9099}
    .bar em{font-family:M;font-style:normal;color:#C9CED3}
    </style>""" + foot("Unit 42（暴露面遥测）· Wiz（利用跟踪，作者自述趋势数据不可归因单一手段）", "两个数字不可互相校验")
    return "w44-f4.html", body

# ---------------------------------------------------------------- W44 图6
def w44_f6():
    steps = [
        ("01", "美国政府前沿模型预发布测试", "自愿程序，先测"),
        ("02", "a subset of cyber defenders", "首发只给防守方"),
        ("03", "Fairwind Program", "逐步扩到受信任伙伴"),
        ("04", "开发者 / 企业 / 消费者", "护栏迭代完成后"),
    ]
    rows = "".join(
        f'<div class="s{" hot" if t == "01" else ""}"><div class="tag">{t}</div>'
        f'<div class="tx"><b>{n}</b><span>{d}</span></div></div>' for t, n, d in steps)
    body = head("2026-W44 · GEMINI 4 CARBON 放量节奏", "能力最强的版本，<b>先给防守方</b>",
                "四段放量，自上而下推进；这不是漏斗，四段是顺序关系", "图 6") + f"""
    <div class="body"><div class="steps">{rows}</div></div>
    <style>
    .steps{{width:100%}}
    .s{{display:grid;grid-template-columns:96px 1fr;align-items:center;border-top:1px solid var(--hair);padding:28px 0}}
    .s:last-child{{border-bottom:1px solid var(--hair)}}
    .tag{{font:700 34px/1 M;color:#3E454D}}
    .s.hot .tag{{color:var(--acc)}}
    .tx b{{display:block;font:700 30px/1.3 SC}}
    .tx span{{display:block;margin-top:8px;font:400 20px/1.4 SC;color:#8A9099}}
    </style>""" + foot("Gemini 4 Carbon 发布页（2026-10-28）", "顺序：政府 → 防守方 → 伙伴 → 公众")
    return "w44-f6.html", body

# ---------------------------------------------------------------- W44 封面 4:3
def w44_cover():
    body = """
    <div class="cv">
      <div class="top"><div>2026-W44 · AI 周回顾</div><div>blog.laobaitv.net</div></div>
      <h1>AA 分数都在 53，<br>差距搬到了 <b>CWE-bench</b></h1>
      <div class="nums">
        <div class="n"><b>53</b><i>Fable 5.1</i></div>
        <div class="n"><b>53</b><i>Astra</i></div>
        <div class="n"><b>53</b><i>Argon</i></div>
        <div class="n"><b>55</b><i>Kimi K3.1</i></div>
        <div class="n"><b>58</b><i>Opus 5.5</i></div>
        <div class="n hot"><b>59</b><i>Carbon</i></div>
      </div>
      <div class="rule"></div>
      <div class="concl">同一个指数，三个来源给出三套分数。通用能力挤进窄带之后，区分度落在了找漏洞、验利用、修补丁三项基准上。</div>
    </div>
    <style>
    .cv{width:1600px;height:1200px;padding:96px 120px 88px;display:flex;flex-direction:column}
    .cv h1{margin-top:52px;font:700 82px/1.16 SC;letter-spacing:-.02em;max-width:1300px}
    .cv h1 b{color:var(--acc)}
    .nums{margin-top:auto;display:grid;grid-template-columns:repeat(6,1fr);gap:24px}
    .n b{display:block;font:700 112px/1 M;letter-spacing:-.03em;color:#3E454D}
    .n i{display:block;margin-top:14px;font:400 19px/1.3 SC;color:#6B7480;font-style:normal}
    .n.hot b{color:var(--acc)}
    .n.hot i{color:#8A5040}
    .rule{margin-top:56px;height:1px;background:var(--hair)}
    .concl{margin-top:36px;font:400 26px/1.65 SC;color:#9AA1A9;max-width:1240px}
    </style>"""
    return page(body, h=1200, cls="cv")


FIG_W44 = [w44_f1, w44_f2, w44_f4, w44_f6]

if __name__ == "__main__":
    import re
    for fn in FIG_W44:
        name, html = fn()
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(page(html))
        print("wrote", name)
    open(os.path.join(OUT, "w44-cover.html"), "w", encoding="utf-8").write(w44_cover())
    print("wrote w44-cover.html")
