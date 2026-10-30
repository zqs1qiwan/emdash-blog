#!/usr/bin/env python3
"""继续 v4：W44 图3/图5（截图+侧栏）、identity 五图与封面、重做 W44 封面。"""
import os, sys
sys.path.insert(0, "/opt/data/news/figures/v4")
from build import page, head, foot

OUT = "/opt/data/news/figures/v4"
SRC = "/opt/data/news/weekly/src"

def shot(name, kick, title, sub, img, notes, fl, fr, num, img_w=830):
    li = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in notes)
    body = head(kick, title, sub, num) + f"""
    <div class="body"><div class="shot">
      <div class="ph"><img src="{img}"></div>
      <ul class="nt">{li}</ul>
    </div></div>
    <style>
    .shot{{display:grid;grid-template-columns:{img_w}px 1fr;gap:52px;align-items:center;width:100%}}
    .ph{{background:#0F1215;border:1px solid var(--hair);padding:12px;display:flex;justify-content:center}}
    .ph img{{max-width:{img_w - 24}px;max-height:648px;display:block}}
    .nt{{list-style:none}}
    .nt li{{border-top:1px solid var(--hair);padding:18px 0}}
    .nt li:first-child{{border-top:none;padding-top:0}}
    .nt b{{display:block;font:700 24px/1.35 SC}}
    .nt span{{display:block;margin-top:8px;font:400 18px/1.55 SC;color:#8A9099}}
    </style>""" + foot(fl, fr)
    return name, body

# ---------------------------------------------------------------- W44 图3 / 图5
_, b = shot("w44-f3.html", "2026-W44 · GOOGLE 官方评测表", "官方表里能读到的<b>三件事</b>",
    "先把这张表看完，再决定要不要相信那句「第一」",
    f"file://{SRC}/dm_evals.webp",
    [("竞品也在同一张表里", "Carbon 与 Argon、Astra、Opus 5.5、Fable 5.1 并排，安全三项的分差可以直接读出来。"),
     ("十七行里只有三行是安全", "其余是通用能力、编码、电脑操作、知识工作与长上下文。安全是这套评测的新卖点，不是主体。"),
     ("口径写在小字里", "表底标注 methodology 链接，写明无护栏评测；发布稿的标题只写「最强」。")],
    "图片来源：Google DeepMind 发布页（2026-10-28）", "表内数据未做二次加工", "图 3")
open(f"{OUT}/w44-f3.html", "w", encoding="utf-8").write(page(b))

_, b = shot("w44-f5.html", "2026-W44 · WIZ · PHP2SHELL 跟踪", "一周之内，受影响组织<b>少了 47.9%</b>",
    "这是相对数量的曲线，不是绝对组织数；读数前先看基准日",
    f"file://{SRC}/wiz_php_affected.png",
    [("基准是 10 月 22 日", "100% 指「当天至少有一台暴露且有漏洞的机器」的组织数，不是全行业。"),
     ("10 月 24 日没有点", "该日数据仍在审核被排除，曲线中段是插值，不是观测。"),
     ("下降不归因单一手段", "Wiz 自己写明这是总体趋势，打补丁、下线、扫描各自权重无法拆分。")],
    "图片来源：Wiz（2026-10）", "相对数量，基准日 = 100%", "图 5")
open(f"{OUT}/w44-f5.html", "w", encoding="utf-8").write(page(b))

# ---------------------------------------------------------------- W44 封面 v2
COVER = """
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
  <div class="strip">
    <div class="s"><u>找</u><b>88.2%</b><span>SEC-bench Pro</span></div>
    <div class="s"><u>验</u><b>54.8%</b><span>ExploitGym</span></div>
    <div class="s"><u>修</u><b>71.0%</b><span>CWE-bench</span></div>
    <div class="s txt"><span>统一指数挤进窄带之后，区分度落在攻防链的三段上。</span></div>
  </div>
</div>
<style>
.cv{width:1600px;height:1200px;padding:88px 110px 76px;display:flex;flex-direction:column}
.cv h1{margin-top:44px;font:700 84px/1.15 SC;letter-spacing:-.022em;max-width:1340px}
.cv h1 b{color:var(--acc)}
.nums{margin-top:76px;display:grid;grid-template-columns:repeat(6,1fr);gap:20px}
.n b{display:block;font:700 104px/1 M;letter-spacing:-.03em;color:#3E454D}
.n i{display:block;margin-top:10px;font:400 20px/1.3 SC;color:#6B7480;font-style:normal}
.n.hot b{color:var(--acc)}
.n.hot i{color:#8A5040}
.strip{margin-top:auto;display:grid;grid-template-columns:repeat(3,1fr) 1.4fr;gap:24px;
  border-top:1px solid var(--hair);padding-top:34px;align-items:end}
.s u{display:block;text-decoration:none;font:700 22px/1 SC;color:#6B7480}
.s b{display:block;margin-top:12px;font:700 52px/1 M;letter-spacing:-.02em}
.s span{display:block;margin-top:10px;font:400 18px/1.4 M;color:#5F6870}
.s.txt{border-left:1px solid var(--hair);padding-left:26px}
.s.txt span{font:400 23px/1.6 SC;color:#9AA1A9;margin-top:0}
</style>"""
open(f"{OUT}/w44-cover.html", "w", encoding="utf-8").write(page(COVER, h=1200, cls="cv"))

# ================================================================ identity 五图
def id1():
    rows = [("信息安全总支出", "Gartner · 2026 全年预测", 100, "2440 亿美元", "#454D57", False),
            ("其中「保护 AI」", "Gartner · 2026 全年预测", 1.16, "28.35 亿 · 1.16%", "var(--acc)", True),
            ("对照：一笔交易对价", "Palo Alto 收购 CyberArk", 10.2, "250 亿 · 10.2%", "#7A848F", False)]
    tr = "".join(
        f'<div class="r{" a" if hot else ""}"><div class="k">{n}<i>{s}</i></div>'
        f'<div class="bar"><u style="width:{max(w,0.6)}%"></u></div>'
        f'<div class="v">{v}</div></div>' for n, s, w, v, c, hot in rows)
    body = head("2026 · 网络安全支出结构", "被挂在嘴边一年的「AI 安全」，<br>实际只占整个市场的 <b>1.16%</b>",
                "同一张尺子上，一笔已完成交易的对价是这个科目一年规模的 8.8 倍", "图 1") + f"""
    <div class="body"><div class="ch">{tr}</div></div>
    <style>
    .ch{{width:100%}}
    .r{{display:grid;grid-template-columns:340px 1fr 360px;align-items:center;gap:28px;padding:30px 0;
      border-top:1px solid var(--hair)}}
    .r:last-child{{border-bottom:1px solid var(--hair)}}
    .k{{font:400 24px/1.4 SC;color:#C9CED3}}
    .k i{{display:block;margin-top:8px;font:400 17px/1.3 M;color:#5F6870;font-style:normal}}
    .bar{{height:34px;background:#171B20}}
    .bar u{{display:block;height:34px;text-decoration:none;background:#454D57}}
    .r:nth-child(2) .bar u{{background:var(--acc)}}
    .r:nth-child(3) .bar u{{background:#7A848F}}
    .v{{font:700 31px/1 M;text-align:right;color:#D7DADE;white-space:nowrap}}
    .r.a .v{{color:var(--acc)}}
    </style>""" + foot("年度市场规模为预测值，交易对价为已完成交易；性质不同，只标量级，相加没有意义", "单位：美元")
    return "id-f1.html", body

def id2():
    body = head("2026 · 250 亿美元的会计后果", "同一份财报，两个净利润，<br>中间差了 <b>11.35 亿</b>",
                "Palo Alto Networks FY26 第四季度；差额主要来自 250 亿对价带来的摊销与整合支出", "图 2") + """
    <div class="body"><div class="two">
      <div class="c">
        <div class="k">GAAP 净亏损</div>
        <div class="v neg">−2.82</div>
        <div class="bar"><u style="height:34%"></u></div>
        <div class="n">按会计准则计入摊销、减值与整合成本</div>
      </div>
      <div class="c">
        <div class="k">non-GAAP 净利润</div>
        <div class="v">+8.53</div>
        <div class="bar"><u class="pos" style="height:100%"></u></div>
        <div class="n">剔除摊销等项目后的口径，两家相差 11.35 亿</div>
      </div>
    </div></div>
    <style>
    .two{display:grid;grid-template-columns:1fr 1fr;gap:90px;width:100%}
    .c{border-top:3px solid #454D57;padding-top:26px}
    .c:first-child{border-top-color:#8A5040}
    .k{font:400 23px/1 SC;color:#8A9099}
    .v{margin-top:22px;font:700 110px/1 M;letter-spacing:-.03em}
    .v.neg{color:#C9CED3}
    .bar{margin-top:26px;height:220px;display:flex;align-items:flex-end}
    .bar u{display:block;width:120px;background:#8A5040;text-decoration:none}
    .bar u.pos{background:var(--acc)}
    .n{margin-top:24px;font:400 20px/1.6 SC;color:#8A9099;max-width:520px}
    </style>""" + foot("Palo Alto Networks FY26 Q4；并购的价钱不体现在收购当年，体现在此后每一季的利润表上", "单位：亿美元")
    return "id-f2.html", body

def id3():
    def col(co, big, cap, sub, hot):
        return f"""<div class="col"><div class="co">{co}</div>
        <div class="big{' o' if hot else ''}">{big}<u>%</u></div>
        <div class="cap">{cap}</div><div class="sub">{sub}</div></div>"""
    body = head("2026 · 两种不并购的活法", "一个卖硬件，一个卖<b>结算权</b>",
                "两家都没有买 AI 安全公司，路径完全不同", "图 3") + f"""
    <div class="body"><div class="cols">
      {col("FORTINET", "+41", "硬件产品收入增速", "季度收入 <b>20.48 亿</b> · 同比 <b>+25.6%</b><br>AI 集群的东西向流量带动换机", False)}
      {col("CLOUDFLARE", "+36", "季度收入增速 · 六家最快", "GAAP 运营亏损 <b>2.06 亿</b> · 占收入 <b>30%</b><br>主动用毛利换基础设施位置", True)}
    </div></div>
    <style>
    .cols{{display:grid;grid-template-columns:1fr 1fr;gap:88px;width:100%}}
    .col{{border-top:1px solid var(--hair);padding-top:30px}}
    .co{{font:400 20px/1 M;letter-spacing:.16em;color:#6B7480}}
    .big{{margin-top:26px;font:700 150px/.95 M;letter-spacing:-.04em}}
    .big.o{{color:var(--acc)}}
    .big u{{text-decoration:none;font-size:56px;margin-left:8px;color:#6B7480}}
    .cap{{margin-top:18px;font:400 24px/1.3 SC;color:#C9CED3}}
    .sub{{margin-top:18px;font:400 20px/1.7 SC;color:#8A9099}}
    .sub b{{color:#E6E8EA;font-weight:700}}
    </style>""" + foot("口径：均为 2026 年第二季度（自然年）财报", "增速：同比")
    return "id-f3.html", body

def id4():
    rows = [("Red Canary", "托管检测响应", 4.8, 4.8, "4.8×"),
            ("Permiso", "云身份威胁检测", 8, 5, "8–13×"),
            ("Chronosphere", "可观测性", 15, 1.8, "15–16×"),
            ("Oasis", "非人类身份", 47, 3, "约 50×")]
    tr = "".join(
        f'<div class="r{" hot" if i == 3 else ""}"><div class="co">{n}<i>{s}</i></div>'
        f'<div class="tk"><u style="left:{a/50*100:.2f}%;width:{max(w/50*100,0.7):.2f}%"></u></div>'
        f'<div class="num">{v}</div></div>' for i, (n, s, a, w, v) in enumerate(rows))
    ticks = "".join(f'<span style="left:{t/50*100:.2f}%">{t}×</span>' for t in (0, 10, 20, 30, 40, 50))
    body = head("2026 · 估值倍数", "身份资产的定价，<br>是托管服务的 <b>十倍</b>",
                "对价 ÷ 交易时披露或报道的 ARR；同一波 AI 叙事下，四条赛道的定价差了十倍", "图 4") + f"""
    <div class="body"><div class="ch"><div class="gl">{''.join(f'<i style="left:{t/50*100:.2f}%"></i>' for t in (0,10,20,30,40,50))}</div>{tr}<div class="axis">{ticks}</div></div></div>
    <style>
    .ch{{width:100%;position:relative}}
    .gl{{position:absolute;left:358px;right:178px;top:0;bottom:54px;pointer-events:none}}
    .gl i{{position:absolute;top:0;bottom:0;width:1px;background:#1A1F25}}
    .r{{display:grid;grid-template-columns:330px 1fr 150px;align-items:center;gap:28px;padding:26px 0}}
    .co{{font:400 24px/1.3 SC;color:#C9CED3}}
    .co i{{display:block;margin-top:7px;font:400 17px/1.3 M;color:#5F6870;font-style:normal}}
    .tk{{position:relative;height:18px;background:#171B20}}
    .tk u{{position:absolute;top:0;height:18px;background:#5A6470;text-decoration:none}}
    .r.hot .tk u{{background:var(--acc)}}
    .num{{font:700 30px/1 M;text-align:right;color:#D7DADE}}
    .r.hot .num{{color:var(--acc)}}
    .axis{{position:relative;height:30px;margin-left:358px;border-top:1px solid var(--hair)}}
    .axis span{{position:absolute;top:8px;transform:translateX(-50%);font:400 16px/1 M;color:#5F6870}}
    </style>""" + foot("区间表示下限至上限；Oasis 为 10 亿美元对约 2000 万 ARR 的报道值", "单位：倍")
    return "id-f4.html", body

def id5():
    # left/width 按 12 个月的真实比例：起点月 / 跨 3 个月
    rows = [("CrowdStrike", "FY27 Q2", 4 / 12 * 100, 3 / 12 * 100, "5 月 — 7 月", True),
            ("Palo Alto + Zscaler", "FY26 Q4", 4 / 12 * 100, 3 / 12 * 100, "5 月 — 7 月", True),
            ("Microsoft", "FY26 Q4", 3 / 12 * 100, 3 / 12 * 100, "4 月 — 6 月", False),
            ("Cloudflare + Fortinet", "2026 Q2", 3 / 12 * 100, 3 / 12 * 100, "4 月 — 6 月", False)]
    tr = "".join(
        f'<div class="r"><div class="co">{n}<i>{s}</i></div>'
        f'<div class="tk"><u class="{"o" if hot else "g"}" style="left:{a:.1f}%;width:{w:.1f}%"></u></div>'
        f'<div class="rg">{r}</div></div>' for n, s, a, w, r, hot in rows)
    months = "".join(f'<span style="left:{p}%">{m}</span>' for m, p in
                     (("1 月", 0), ("4 月", 3 / 12 * 100), ("7 月", 6 / 12 * 100),
                      ("10 月", 9 / 12 * 100), ("12 月", 11 / 12 * 100)))
    body = head("2026 · 财报口径", "同叫「最新一季」，<br>覆盖的日历窗口差了<b>一个月</b>",
                "把这几家的增速、ARR 放进同一张表，等于把不同月份的市场混在一起比", "图 5") + f"""
    <div class="body"><div class="ch"><div class="gl">{''.join(f'<i style="left:{p:.2f}%"></i>' for p in (0, 25, 50, 75, 91.67))}</div>{tr}<div class="axis">{months}</div>
    <div class="lg"><span><i style="background:var(--acc)"></i>5–7 月</span>
    <span><i style="background:#5A6470"></i>4–6 月</span></div></div></div>
    <style>
    .ch{{width:100%;position:relative}}
    .gl{{position:absolute;left:358px;right:200px;top:0;bottom:78px;pointer-events:none}}
    .gl i{{position:absolute;top:0;bottom:0;width:1px;background:#1A1F25}}
    .r{{display:grid;grid-template-columns:330px 1fr 200px;align-items:center;gap:28px;padding:24px 0}}
    .co{{font:400 24px/1.3 SC;color:#C9CED3}}
    .co i{{display:block;margin-top:7px;font:400 17px/1.3 M;color:#5F6870;font-style:normal}}
    .tk{{position:relative;height:18px;background:#171B20}}
    .tk u{{position:absolute;top:0;height:18px;text-decoration:none;background:#5A6470}}
    .tk u.o{{background:var(--acc)}}
    .rg{{font:400 21px/1 M;color:#8A9099;text-align:right}}
    .axis{{position:relative;height:28px;margin-left:358px;border-top:1px solid var(--hair)}}
    .axis span{{position:absolute;top:8px;transform:translateX(-50%);font:400 16px/1 M;color:#5F6870}}
    .lg{{display:flex;gap:36px;margin-top:26px;font:400 18px/1 SC;color:#8A9099}}
    .lg i{{display:inline-block;width:14px;height:14px;margin-right:10px;vertical-align:-2px}}
    </style>""" + foot("财年终点从 1 月底排到 12 月底；窗口不同，横向比较增速时要先对齐月份", "口径：各公司财报披露")
    return "id-f5.html", body

ID_COVER = """
<div class="cv">
  <div class="top"><div>2026 · 网络安全并购观察</div><div>blog.laobaitv.net</div></div>
  <h1>2026 年最大的几笔并购，<br>没有一笔是为了<b>「AI 安全」</b></h1>
  <div class="row">
    <div class="cell"><b>250<u> 亿</u></b><span>一笔交易的对价</span></div>
    <div class="eq">8.8×</div>
    <div class="cell"><b>28.35<u> 亿</u></b><span>「保护 AI」全年市场规模</span></div>
  </div>
  <div class="concl"><div class="bar"></div>
    <p>钱流向 AI 撕开的三道口子：身份、遥测、运行时。真正被买的是时间。</p>
    <span>口径：左为已完成交易对价（Palo Alto / CyberArk），右为 Gartner 2026 年预测，性质不同，仅作量级对照</span>
  </div>
</div>
<style>
.cv{width:1600px;height:1200px;padding:88px 110px 76px;display:flex;flex-direction:column}
.cv h1{margin-top:44px;font:700 80px/1.18 SC;letter-spacing:-.022em;max-width:1400px}
.cv h1 b{color:var(--acc)}
.row{margin-top:84px;display:grid;grid-template-columns:1fr auto 1fr;gap:36px;align-items:end}
.cell b{display:block;font:700 132px/1 M;letter-spacing:-.035em}
.cell span{display:block;margin-top:14px;font:400 21px/1.4 SC;color:#6B7480}
.cell u{text-decoration:none;font-size:44px;color:#6B7480;margin-left:6px}
.eq{font:700 56px/1 M;color:#6B7480;padding-bottom:26px}
.concl{margin-top:auto;border-top:1px solid var(--hair);padding-top:34px}
.concl p{font:400 30px/1.6 SC;color:#C9CED3;max-width:1200px}
.concl span{display:block;margin-top:20px;font:400 18px/1.55 M;color:#5F6870;max-width:1250px}
</style>"""

for fn in (id1, id2, id3, id4, id5):
    n, b = fn()
    open(f"{OUT}/{n}", "w", encoding="utf-8").write(page(b))
open(f"{OUT}/id-cover.html", "w", encoding="utf-8").write(page(ID_COVER, h=1200, cls="cv"))
print("built: w44-f3, w44-f5, w44-cover, id-f1..f5, id-cover")
