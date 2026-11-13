"""Build the v3.1 stress-test PDF. Predictions were already scored after the run."""
from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "outputs"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
DOCS = ROOT / "docs"
WORKSPACE_PDF = Path("/workspace/stress_test_v3.1.pdf")
REPO_PDF = DOCS / "stress_test_v3.1.pdf"

NAVY = colors.HexColor("#1f4e79")
GOLD = colors.HexColor("#c47b17")
SLATE = colors.HexColor("#5b6770")
PALE = colors.HexColor("#f4f6f8")
LINE = colors.HexColor("#d0d5da")
WHITE = colors.white
GREEN = colors.HexColor("#1b6b4a")
RUST = colors.HexColor("#9b3d1f")
INK = colors.HexColor("#1a1a1a")
ROBUST_BG = colors.HexColor("#dceee6")
FRAGILE_BG = colors.HexColor("#f8ecd4")
ASSUMP_BG = colors.HexColor("#f3ddd5")

pdfmetrics.registerFont(TTFont("Lib", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LibBd", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LibIt", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("LibBI", "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"))

S = None


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CoverTitle", fontName="LibBd", fontSize=20, leading=24, textColor=NAVY, spaceAfter=4))
    s.add(ParagraphStyle("CoverSub", fontName="Lib", fontSize=10.5, leading=14, textColor=SLATE, spaceAfter=6))
    s.add(ParagraphStyle("H1", fontName="LibBd", fontSize=13, leading=16, textColor=NAVY, spaceBefore=8, spaceAfter=4))
    s.add(ParagraphStyle("H2", fontName="LibBd", fontSize=10.5, leading=13.5, textColor=NAVY, spaceBefore=6, spaceAfter=3))
    s.add(ParagraphStyle("Body", fontName="Lib", fontSize=8.6, leading=11.6, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=5))
    s.add(ParagraphStyle("BulletBody", fontName="Lib", fontSize=8.6, leading=11.6, textColor=INK, leftIndent=10, spaceAfter=2.5, bulletIndent=0))
    s.add(ParagraphStyle("Caption", fontName="LibIt", fontSize=7.5, leading=10, textColor=SLATE, spaceAfter=6))
    s.add(ParagraphStyle("BoxTitle", fontName="LibBd", fontSize=9, leading=12, textColor=NAVY, spaceAfter=2))
    s.add(ParagraphStyle("BoxBody", fontName="Lib", fontSize=7.6, leading=10.2, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=2))
    s.add(ParagraphStyle("Th", fontName="LibBd", fontSize=6.6, leading=8.4, textColor=WHITE, alignment=TA_CENTER))
    s.add(ParagraphStyle("ThL", fontName="LibBd", fontSize=6.6, leading=8.4, textColor=WHITE, alignment=TA_LEFT))
    s.add(ParagraphStyle("Td", fontName="Lib", fontSize=6.6, leading=8.4, textColor=INK, alignment=TA_LEFT))
    s.add(ParagraphStyle("TdC", fontName="Lib", fontSize=6.6, leading=8.4, textColor=INK, alignment=TA_CENTER))
    s.add(ParagraphStyle("TdBd", fontName="LibBd", fontSize=6.6, leading=8.4, textColor=INK, alignment=TA_LEFT))
    s.add(ParagraphStyle("TdR", fontName="Lib", fontSize=6.6, leading=8.4, textColor=INK, alignment=TA_RIGHT))
    s.add(ParagraphStyle("Footer", fontName="Lib", fontSize=7.5, leading=9, textColor=SLATE, alignment=TA_CENTER))
    s.add(ParagraphStyle("Small", fontName="Lib", fontSize=7.6, leading=10.2, textColor=INK, alignment=TA_LEFT, spaceAfter=3))
    s.add(ParagraphStyle("Safe", fontName="Lib", fontSize=8, leading=10.8, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3))
    s.add(ParagraphStyle("Unsafe", fontName="Lib", fontSize=8, leading=10.8, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=3))
    s.add(ParagraphStyle("LeftBody", fontName="Lib", fontSize=8.2, leading=11.2, textColor=INK, alignment=TA_LEFT, spaceAfter=4))
    s.add(ParagraphStyle("SourceItem", fontName="Lib", fontSize=7.6, leading=10.4, textColor=INK, alignment=TA_LEFT, leftIndent=10, spaceAfter=2.5))
    s.add(ParagraphStyle("Tag", fontName="LibBd", fontSize=7, leading=9, textColor=WHITE, alignment=TA_CENTER))
    return s


def P(text, style="Body"):
    return Paragraph(str(text), S[style])


def footer_header(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 10 * mm, w, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Lib", 8)
    canvas.drawString(16 * mm, h - 6.5 * mm, "Stress test of v3.1  ·  own stock vs marketplace listing")
    canvas.drawRightString(w - 16 * mm, h - 6.5 * mm, "Decision support, not Joybuy's actual numbers")
    canvas.setFillColor(PALE)
    canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(SLATE)
    canvas.setFont("Lib", 7.5)
    canvas.drawString(16 * mm, 5 * mm, "Made by Ami Sata  ·  Portfolio project")
    canvas.drawCentredString(w / 2, 5 * mm, f"Page {doc.page}")
    canvas.drawRightString(w - 16 * mm, 5 * mm, "Amazon UK fees as a labelled stand-in")
    canvas.restoreState()


def styled_table(data, col_widths, header=True):
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY if header else PALE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE if header else NAVY),
        ("FONTNAME", (0, 0), (-1, 0), "LibBd"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.6),
        ("LEADING", (0, 0), (-1, -1), 8.4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
    ]
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle(style))
    return t


def box(title, body, width=178 * mm, tint=PALE, border=NAVY):
    inner = [P(title, "BoxTitle"), P(body, "BoxBody")]
    t = Table([[inner]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tint),
        ("BOX", (0, 0), (-1, -1), 1, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def verdict_tag(label):
    colour = {
        "ROBUST": GREEN,
        "FRAGILE": GOLD,
        "ASSUMPTION-DRIVEN": RUST,
        "DIRECTION ONLY": SLATE,
    }.get(label, SLATE)
    t = Table([[P(label, "Tag")]], colWidths=[38 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colour),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def tornado_chart(tornado: pd.DataFrame, path: Path) -> Path:
    a = tornado[tornado.side == "A"].set_index("param")
    b = tornado[tornado.side == "B"].set_index("param")
    short = {
        "seller_coverage": "Coverage (evidence 0-10% at A; 50-95% at B)",
        "seller_coverage_beyond": "Coverage 0-100% (beyond evidence, A only)",
        "spillover_pct": "Basket / traffic spillover 0-20%",
        "gm_haircut_entrant": "1P margin haircut 0-25% (inert at B)",
        "fulfilment_variable_share": "Fulfilment variable share 50-90% (inert at B)",
        "intro_commission": "Introductory commission 5-15% (inert at B)",
        "ad_take": "Advertising take 0-5%",
        "hurdle_rate": "GMROI hurdle 10-35%",
        "fulfilment_delta": "Fulfilment rate, +/-5 percentage points",
    }
    order = [
        "fulfilment_delta",
        "seller_coverage",
        "seller_coverage_beyond",
        "ad_take",
        "spillover_pct",
        "gm_haircut_entrant",
        "fulfilment_variable_share",
        "intro_commission",
        "hurdle_rate",
    ]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    y = list(range(len(order)))[::-1]
    a_n = [int(a.loc[p, "n_flip_operating"]) if p in a.index else 0 for p in order]
    b_n = [int(b.loc[p, "n_flip_operating"]) if p in b.index else 0 for p in order]
    a_u = [int(a.loc[p, "n_flip_unit"]) if p in a.index else 0 for p in order]
    height = 0.36
    ax.barh([yi + 0.2 for yi in y], a_n, height=height, color="#1f4e79", label="A, operating flips")
    ax.barh([yi - 0.2 for yi in y], b_n, height=height, color="#c47b17", label="B, operating flips")
    for yi, ao, au in zip(y, a_n, a_u):
        if au > ao:
            ax.plot([au], [yi + 0.2], marker="D", color="#1f4e79", markersize=5, zorder=5)
            ax.text(au + 0.25, yi + 0.2, f"A unit {au}", va="center", fontsize=6.5, color="#1f4e79")
    for yi, av, bv in zip(y, a_n, b_n):
        if av:
            ax.text(av + 0.15, yi + 0.2, str(av), va="center", fontsize=7, color="#1f4e79")
        if bv:
            ax.text(bv + 0.15, yi - 0.2, str(bv), va="center", fontsize=7, color="#c47b17")
    ax.set_yticks(y)
    ax.set_yticklabels([short[p] for p in order], fontsize=7.5)
    ax.set_xlabel("Operating verdicts that flip inside the stated range (of 20)")
    ax.set_xlim(0, 20)
    ax.set_title("Tornado: operating flips, one parameter at a time", loc="left", color="#1f4e79", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#e6e6e6")
    ax.plot([], [], marker="D", color="#1f4e79", linestyle="None", label="A, unit flips (when higher)")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, frameon=False, fontsize=7.5, loc="lower right")
    fig.subplots_adjust(left=0.46, right=0.97, top=0.88, bottom=0.16)
    fig.savefig(path, dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return path


def break_chart(brk: pd.DataFrame, path: Path) -> Path:
    op = brk[brk.layer == "operating"].copy().sort_values("spillover")
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.plot(op["spillover"] * 100, op["coverage_at_break"] * 100, color="#1f4e79", linewidth=2.2, label="First mid-band flip (Pushchairs)")
    ax.axhline(50, color="#c47b17", linestyle="--", linewidth=1, label="Strategic threshold, 50% (Assumption)")
    ax.axhline(10, color="#5b6770", linestyle=":", linewidth=1.2, label="Evidence-informed coverage ceiling, 10%")
    ax.scatter([8], [72.3141], s=40, color="#c47b17", zorder=5)
    ax.annotate("Default 8% spillover:\n72.3% coverage", xy=(8, 72.3141), xytext=(11, 62),
                fontsize=7.5, color="#1f4e79",
                arrowprops=dict(arrowstyle="->", color="#1f4e79", lw=0.8))
    ax.scatter([0], [56.4023], s=30, color="#1f4e79", zorder=5)
    ax.annotate("0% spillover: 56.4%", xy=(0, 56.4023), xytext=(2, 48),
                fontsize=7, color="#1f4e79",
                arrowprops=dict(arrowstyle="->", color="#1f4e79", lw=0.7))
    ax.set_xlabel("Basket spillover, %")
    ax.set_ylabel("Seller coverage at the first 100% 1P break, %")
    ax.set_xlim(-0.5, 20.5)
    ax.set_ylim(0, 100)
    ax.set_title("Where Entrant A leaves 100% mid-band 1P  (operating and unit coincide)", loc="left",
                 color="#1f4e79", fontsize=10.5, fontweight="bold")
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6")
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor="white")
    plt.close(fig)
    return path


RANGES_A = (
    "Entrant A Monte Carlo ranges (10,000 draws, seed 20261113, uniform): "
    "seller coverage 0-10% (Task 0 evidence-informed range, not the brief's 0-30%); "
    "spillover 0-20%; 1P haircut 0-25%; fulfilment variable share 50-90%; "
    "introductory commission 5-15%; advertising take 0-5%; GMROI hurdle 10-35%; "
    "fulfilment rate +/-5 percentage points."
)
RANGES_B = (
    "Established B Monte Carlo ranges (10,000 draws, seed 20261113, uniform): "
    "seller coverage 50-95%; spillover 0-20%; advertising take 0-5%; "
    "GMROI hurdle 10-35%; fulfilment rate +/-5 percentage points. "
    "Haircut, variable share and introductory commission are inert at B "
    "by construction and were not drawn."
)


def build(story):
    story.append(P("Stress test of the 1P vs 3P model, v3.1", "CoverTitle"))
    story.append(P(
        "Entrant A and Established B, mid-band, 20 sub-categories. "
        "13 November 2026 (Asia/Calcutta). Predictions were written at 10:48 Asia/Calcutta (05:18 UTC), "
        "before any new model run. No v3.1 default was changed. "
        "This is a stress test, not a defence of the published mix.",
        "CoverSub",
    ))

    story.append(P("1. One-page executive summary", "H1"))
    story.append(P(
        "v3.1's mid-band defaults are unchanged: Entrant A recommends Bring in-house "
        "on all 20 sub-categories (100% of modelled mid-band sales). Established B "
        "recommends Bring in-house on five (beauty four and baby care), Test as 3P first "
        "on three (outerwear, footwear, baby clothing), and Keep 3P on twelve. "
        "That is 25% of sub-categories and 5.6% of modelled mid-band sales as 1P, "
        "and 15 A-to-B flips. The operating recommendation is what the model would run."
    ))
    story.append(P(
        "<b>Task 0 (Joybuy marketplace, web search only, 13 November 2026).</b> "
        "0% seller coverage is still the only evidenced launch-day value. Joybuy launched "
        "in March 2026 as a first-party retailer (The Grocer, 9 June 2026; ChannelX, "
        "15 June 2026: &#8220;Currently everything for sale on JoyBuy is sold by JoyBuy.&#8221;). "
        "A spokesperson told The Grocer the firm was &#8220;working with trusted brands to test "
        "a curated marketplace in the second half of 2026.&#8221; Operator One (published and "
        "updated 24 September 2026) says a test started and describes itself as an "
        "invitation-only partner; it is not a published listing count. LockerRules "
        "(updated 6 October 2026) says that as of September 2026 Joybuy is a retailer, "
        "with &#8220;no third-party listings.&#8221; No November 2026 source gives a live 3P share, "
        "and no seller fee card is published. Circulating 5-10% USD fee figures are "
        "<b>UNVERIFIED</b>. The evidence-informed coverage range used here is <b>0-10%</b> "
        "(10% is a generous Assumption upper bound for an invitation-only test, not a "
        "published figure). The brief's 0-30% is beyond that evidence and is used only "
        "in a separate 0-100% search to locate the exact 100% 1P break."
    ))

    bullets = [
        "<b>Entrant A's operating 100% 1P is robust</b> inside the evidence range and "
        "in all 10,000 Monte Carlo draws (ranges below). The strategic layer keeps "
        "ranging the core while coverage is below 50%. The first mid-band flip, "
        "operating and unit together, is at <b>72.3% coverage</b> with the default 8% "
        "spillover (Pushchairs, to Test as 3P first), and at 56.4% coverage if spillover "
        "is 0%. Both are far above 10%.",
        "<b>Entrant A's unit 100% 1P is fragile</b> once contribution is stressed. "
        "The first haircut break is <b>13.52%</b> (Pushchairs, to Do not range). "
        "Peripherals, office and car seats follow at 14.87%. A fulfilment increase of "
        "<b>2.37 percentage points</b>, or a variable-cost share of 83.8%, does the same "
        "for Pushchairs. Operating stays 20/20 Bring in every one of those cases. "
        "In the Monte Carlo, only Pushchairs is fragile on the unit layer (58.62% Bring).",
        "<b>Established B's 25% / 5.6% 1P headline is assumption-driven.</b> "
        "A 5-point cut on the published THG Beauty (39.3%) and Zalando (39.9%) gross "
        "margins, which the brief asked for because those businesses are own-brand and "
        "DTC-heavy, turns all five B 1P lines to Test as 3P first. Mid-band 1P at B "
        "becomes 0 of 20 and 0% of modelled sales. Fulfilment up 2.75 percentage points "
        "does the same for beauty. This is the most important finding of the stress test.",
        "<b>Everyday clothing and sportswear at B are Monte Carlo fragile</b> "
        "(maximum share 42.3% and 52.3%). The three default Test lines (outerwear, "
        "footwear, baby clothing) are not fragile by the brief's 60% rule: they are "
        "more often Bring in-house in the draws (73.9%, 64.4%, 77.4%). The default Test "
        "sits off the centre of the uncertainty range.",
        "<b>None of the 15 A-to-B flips is driven by the 25% GMROI hurdle.</b> "
        "Attribution uses all five tests (contribution versus the 3P take, inventory "
        "liquidity, GMROI, demand predictability, and the strategic tilt). Every flip's "
        "primary cause is the availability-adjusted contribution comparison.",
        "<b>Versus Amazon's 61% third-party worldwide paid units</b> (Q4 2025 earnings, "
        "excluding Whole Foods): B is 1P-light in direction, for these five UK categories "
        "measured by assumed sales. That is not a hard miscalibration. The comparison is "
        "of unlike things (geography, units versus sales, and category mix).",
        "<b>Tornado, top three, operating verdicts.</b> (1) Established fulfilment "
        "+/-5 percentage points: 15 of 20 flip at B. (2) Seller coverage: 10 at B "
        "(50-95%); 10 at A only when coverage is taken beyond the evidence, first at "
        "72.3%. (3) Advertising take 0-5%: 5 clothing lines at B. Haircut is the "
        "third-ranked stress for A's unit layer (10 durables).",
    ]
    for b in bullets:
        story.append(P("&#8226;  " + b, "BulletBody"))

    story.append(P(
        "<b>What survives every attack in this test.</b> At A, all 20 operating mid-band "
        "Bring verdicts. At A's unit layer, the four beauty lines and baby care. At B, "
        "five Keep 3P lines (compact appliances, peripherals, office equipment, "
        "pushchairs, car seats). Beauty 1P at B does not survive a 5-point gross-margin cut."
    ))
    story.append(P(
        "<b>Prediction score:</b> 16 hits, 3 partial, 2 misses, on 21 scored claims "
        "(17.5 / 21, 83%). The two misses are the ones a stress test is for: which B "
        "clothing lines are fragile (the Keep lines, not the Test lines), and that B's "
        "beauty 1P does not survive a 5-point cut. Task 6 (price-band distributions, "
        "SKU curves, new categories) is v3.2 work and is kept out of these v3.1 tables."
    ))
    story.append(P(RANGES_A, "Caption"))
    story.append(P(RANGES_B, "Caption"))

    story.append(KeepTogether([
    P("2. Robust, fragile, and assumption-driven", "H1"),
    P(
        "Labels follow the brief. <b>ROBUST</b> means the default mid-band verdict "
        "holds inside the stated ranges, is not Monte Carlo fragile (no verdict at or "
        "under 60%), and survives the Task 5 attacks. <b>FRAGILE</b> means a verdict "
        "flips inside a documented range, or no single verdict exceeds 60% of draws. "
        "<b>ASSUMPTION-DRIVEN</b> means the result is implied by a labelled Assumption "
        "that, if moved a short way, changes the headline. Exact thresholds are in the "
        "tables that follow. The 60% cut is the brief's, and it is sharp: laundry at B "
        "is 60.29% Keep (not fragile) and Pushchairs at A's unit layer is 58.62% Bring (fragile)."
    ),
    ]))

    def vt(label, claim, threshold, why):
        return [
            verdict_tag(label),
            P(claim, "Td"),
            P(threshold, "Td"),
            P(why, "Td"),
        ]

    hdr = [P("Label", "Th"), P("Verdict", "ThL"), P("Exact threshold or range", "ThL"), P("Why", "ThL")]
    rows = [hdr]
    rows.append(vt(
        "ROBUST",
        "A, operating, all 20 mid-band Bring in-house (100% of modelled sales).",
        "Holds at coverage 0-10% (0 flips); holds in 10,000/10,000 Monte Carlo draws; holds through every Task 5 attack, including a 25% haircut and the combined adverse case. First flip only at 72.31% coverage (8% spillover) or 56.40% (0% spillover).",
        "The strategic layer ranges the core while coverage is below 50%. That layer, plus 0% default coverage, is what makes operating 100% 1P so stable. It is a design result, not a surprise.",
    ))
    rows.append(vt(
        "FRAGILE",
        "A, unit layer, 100% mid-band 1P, and specifically Pushchairs.",
        "First haircut break: Pushchairs at 13.52%, then peripherals, office and car seats at 14.87%, cooking and compact at 16.22%, laundry, refrigeration, laptops and tablets at 17.57%. Fulfilment +2.37pp (Pushchairs) to +3.49pp (laundry group). Variable share 83.83% (Pushchairs) to 88.19% (cooking, compact). Monte Carlo: Pushchairs 58.62% Bring, 41.38% Do not range (the only A fragile).",
        "Unit contribution on durables is thin after the Currys 18.3% proxy and a 5% haircut. Operating still ranges them. The 5% default haircut sits below the first break; it was not searched to keep unit 1P intact.",
    ))
    rows.append(vt(
        "ASSUMPTION-DRIVEN",
        "B, 5 Bring in-house (beauty four and baby care): 25% of sub-categories, 5.6% of modelled mid-band sales.",
        "A 5-point cut on THG / Zalando established gross margins: 0 Bring, 5 Test, 15 Keep; 0% of sales. A 10-point cut: 0 Bring, 0 Test, 20 Keep. Fulfilment +2.75pp (makeup, fragrance) or +2.96pp (skincare, haircare, baby care): beauty and baby care leave 1P. Monte Carlo (ranges in section 4): those five stay Bring in 95.3-95.8% of draws, so they are not MC-fragile inside those ranges. They fail the Task 5b attack the brief asked for.",
        "THG Beauty FY2025 39.3% and Zalando FY2025 39.9% are published filings, used as if they were the margin on third-party brand resale in a UK 1P programme. They may overstate it. The established 1P mix hangs on that Assumption.",
    ))
    rows.append(vt(
        "FRAGILE",
        "B, Everyday clothing (default Keep) and Sportswear (default Keep).",
        "Monte Carlo: Everyday clothing Bring 42.29%, Test 32.47%, Keep 25.24% (max 42.29%). Sportswear Bring 52.28%, Test 30.85%, Keep 16.87% (max 52.28%). Spillover flips: footwear at 1.06% (Test to Keep), sportswear at 10.36% (Keep to Test), everyday at 18.29% (Keep to Test). Ad take flips five clothing lines between 0.59% and 4.63%. Coverage 50-95% flips ten lines.",
        "These are close cases. The default Keep is not the centre of the uniform range: both are more often Bring than Keep in the draws, yet no verdict clears 60%.",
    ))
    rows.append(vt(
        "FRAGILE",
        "B default Test on outerwear, footwear and baby clothing, as a statement that Test is the typical outcome.",
        "Monte Carlo: Outerwear Bring 73.92%, Footwear Bring 64.43%, Baby clothing Bring 77.35%. None is fragile by the 60% rule. They are more often Bring than Test. Fulfilment down 1.35-3.56pp, or coverage up to 77-85%, moves them to Bring.",
        "The published default sits off the centre of the uncertainty range. Calling them a stable Test mid-tail is weaker than the default table suggests. (The pre-run prediction that they would be Monte Carlo fragile was a miss; the direction, that they are close, was right.)",
    ))
    rows.append(vt(
        "ROBUST",
        "B, five Keep 3P lines: compact appliances, peripherals, office, pushchairs, car seats.",
        "Monte Carlo Keep 90.0-91.5%. They do not flip on +/-5pp fulfilment (the other ten of the 15 fulfilment flips are elsewhere). They survive every Task 5 attack (they stay Keep). Coverage 50-95% does not move them.",
        "Fully loaded contribution on these lines is not competitive with a rich 3P take at 90% coverage, and that comparison is not close.",
    ))
    rows.append(vt(
        "FRAGILE",
        "B, laundry, refrigeration, laptops, tablets (Keep, 60.29%) and cooking (Keep, 62.20%).",
        "Coverage: cooking Keep to Test at 57.00%; laundry, refrigeration, laptops, tablets at 64.54%. Fulfilment down 4.56-4.85pp: Keep to Test. They sit on the brief's 60% knife-edge.",
        "Default Keep is a slim majority inside the stated ranges. Not a headline flip, but not a result to lean on.",
    ))
    rows.append(vt(
        "ROBUST",
        "The 15 A-to-B flips are contribution versus the 3P take, not the 25% hurdle.",
        "hurdle_driven is False for every sub-category. Setting the hurdle to 0 at B leaves every recommendation unchanged. Mid-tail and strategic isolations do not undo the 15.",
        "The GMROI hurdle is not doing the work the 15-flip table might be thought to rest on.",
    ))
    rows.append(vt(
        "DIRECTION ONLY",
        "B is 1P-light relative to Amazon's 61% 3P worldwide paid-unit mix, for these five UK categories.",
        "Naive gap: 39% implied 1P units versus 5.6% modelled mid-band sales (33.4 percentage points). Price-mix illustration (Assumption, not an Amazon disclosure): equal average prices would make 39% of units 39% of sales; half the 3P average price, 24.2% of sales; twice, 56.1%. The model's own 1P lines sit in lower-priced beauty and baby care.",
        "Unlike comparison: worldwide versus UK, all categories versus five, units versus assumed sales. This stress test does not treat the gap as a hard miscalibration and does not tune B toward 39%.",
    ))

    col_w = [32 * mm, 42 * mm, 54 * mm, 50 * mm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("BACKGROUND", (0, 1), (0, 1), ROBUST_BG),
        ("BACKGROUND", (0, 2), (0, 2), FRAGILE_BG),
        ("BACKGROUND", (0, 3), (0, 3), ASSUMP_BG),
        ("BACKGROUND", (0, 4), (0, 4), FRAGILE_BG),
        ("BACKGROUND", (0, 5), (0, 5), FRAGILE_BG),
        ("BACKGROUND", (0, 6), (0, 6), ROBUST_BG),
        ("BACKGROUND", (0, 7), (0, 7), FRAGILE_BG),
        ("BACKGROUND", (0, 8), (0, 8), ROBUST_BG),
        ("BACKGROUND", (0, 9), (0, 9), PALE),
        ("ROWBACKGROUNDS", (1, 1), (-1, -1), [WHITE, PALE]),
    ]))
    story.append(t)
    story.append(Spacer(1, 3 * mm))
    story.append(P(
        "v3.1 already evaluates three price bands. On all 60 bands, five low-velocity "
        "high-price bands are Do not range at A (cooking, office, outerwear, pushchairs, "
        "car seats). The mid-band 20/20 is a statement about the mid band, not about "
        "every SKU. That is already in the published model; it is not Task 6.",
        "Caption",
    ))

    story.append(KeepTogether([
    P("3. Tornado, flip points, and the coverage-spillover break", "H1"),
    P(
        "Each parameter is moved on its own across the range in the chart, with every "
        "other default held. Diamonds mark A's unit-layer flips where they exceed the "
        "operating count (haircut, variable share, fulfilment). Haircut, variable share "
        "and introductory commission are inert at B and show zero, as they must."
    ),
    ]))
    story.append(Image(str(FIG / "tornado.png"), width=178 * mm, height=88 * mm))
    story.append(P(
        "Figure 1. Operating flips inside each stated range. Seller coverage at A is shown "
        "twice: the evidence-informed 0-10% (zero flips) and the 0-100% search used only "
        "to locate the break (10 flips). Top three, operating: fulfilment +/-5pp (15 at B); "
        "seller coverage (10 at B; 10 at A beyond evidence); advertising take (5 at B).",
        "Caption",
    ))

    story.append(P("Exact flip points (operating unless noted)", "H2"))
    fh = [P(h, "Th") for h in ["Side", "Parameter and range", "First flip (then others)", "From to"]]
    fr = [fh]

    def fr_row(side, param, first, direction):
        return [P(side, "TdC"), P(param, "Td"), P(first, "Td"), P(direction, "Td")]

    fr += [
        fr_row("A", "Seller coverage 0-10% (evidence)", "None, either layer.", "none"),
        fr_row("A", "Seller coverage 0-100% (beyond evidence), both layers",
               "Pushchairs at 72.31%. Then peripherals, car seats, office at 73.46%; compact, cooking at 74.60%; laundry, refrigeration, laptops, tablets at 75.75%. At 80%+ coverage, mid-band is 10/20 1P and 13.6% of sales (beauty and clothing stay 1P even at 100% coverage, under entrant costs).",
               "Bring to Test as 3P first"),
        fr_row("A", "Spillover 0-20%; intro commission 5-15%; ad take 0-5%; hurdle 10-35%", "None, either layer.", "none"),
        fr_row("A unit", "Haircut 0-25% (operating: none)",
               "Pushchairs 13.52%; peripherals, office, car seats 14.87%; cooking, compact 16.22%; laundry, refrigeration, laptops, tablets 17.57%. At 25%, 10 unit Bring remain (beauty and fashion).",
               "Bring to Do not range"),
        fr_row("A unit", "Variable share 50-90% (operating: none)",
               "Pushchairs 83.83%; office, car seats, peripherals 86.01%; cooking, compact 88.19%. Six unit flips. Laundry group does not flip inside 90%.",
               "Bring to Do not range"),
        fr_row("A unit", "Fulfilment +/-5pp (operating: none)",
               "Pushchairs +2.37pp; peripherals, car seats, office +2.74pp; compact, cooking +3.12pp; laundry, refrigeration, laptops, tablets +3.49pp. Ten unit flips.",
               "Bring to Do not range"),
        fr_row("B", "Seller coverage 50-95%, both layers",
               "Cooking Keep to Test at 57.00%; laundry, refrigeration, laptops, tablets at 64.54%; footwear Test to Bring at 77.52%; outerwear Test to Bring at 82.62%; everyday Keep to Test at 82.63%; baby clothing Test to Bring at 84.84%; sportswear Keep to Test at 88.21%. Ten flips.",
               "As listed"),
        fr_row("B", "Spillover 0-20%",
               "Footwear Test to Keep at 1.06%; sportswear Keep to Test at 10.36%; everyday Keep to Test at 18.29%. Three flips.",
               "As listed"),
        fr_row("B", "Advertising take 0-5%",
               "Everyday Keep to Test at 0.59%; outerwear Test to Bring at 1.04%; baby clothing Test to Bring at 1.65%; sportswear Keep to Test at 2.45%; footwear Test to Keep at 4.63%. Five clothing flips.",
               "As listed"),
        fr_row("B", "Fulfilment +/-5pp (largest tornado bar)",
               "Fifteen of 20. Durables Keep to Test when fulfilment falls about 4.6-4.8pp (cooking -4.85; laundry group -4.56). Clothing: footwear Test to Bring at -3.56pp; outerwear and everyday at -1.96pp; baby clothing at -1.35pp; sportswear Keep to Test at -0.45pp. Beauty and baby care Bring to Test when fulfilment rises 2.75pp (makeup, fragrance) or 2.96pp (skincare, haircare, baby care). Five durables (compact, peripherals, office, pushchairs, car seats) do not flip.",
               "As listed"),
        fr_row("B", "Haircut, variable share, intro commission; hurdle 10-35%",
               "Inert, or (hurdle) zero flips. Asking for a B haircut flip point is asking for a result v3.1 cannot produce.",
               "none"),
    ]
    story.append(styled_table(fr, [16 * mm, 42 * mm, 82 * mm, 38 * mm]))
    story.append(Spacer(1, 3 * mm))

    story.append(Image(str(FIG / "coverage_break.png"), width=178 * mm, height=81 * mm))
    story.append(P(
        "Figure 2. Seller coverage at which Entrant A first leaves 100% mid-band 1P, "
        "as spillover varies. Operating and unit coincide because every break is above "
        "the 50% strategic threshold. Inside the evidence range 0-10%, and even at 50% "
        "coverage with 8% spillover, the mid-band stays 20/20 1P. At 20% spillover the "
        "break is 79.66% coverage.",
        "Caption",
    ))

    story.append(P("4. Monte Carlo, with the ranges printed", "H1"))
    story.append(P(RANGES_A))
    story.append(P(RANGES_B))
    story.append(P(
        "A &#8220;fragile&#8221; flag means no single verdict exceeds 60% of the 10,000 draws. "
        "That flag is a function of the ranges above, which is why they are printed "
        "next to every result. Draws are uniform and independent."
    ))

    mh = [P(h, "Th") for h in [
        "Side and metric", "Mean", "Median", "5th pct.", "95th pct.", "Min", "Max",
    ]]

    def mr(name, mean, med, p5, p95, mn, mx):
        return [P(name, "Td"), P(mean, "TdC"), P(med, "TdC"), P(p5, "TdC"), P(p95, "TdC"), P(mn, "TdC"), P(mx, "TdC")]

    mrows = [mh,
        mr("A operating, 1P share of sub-categories", "100%", "100%", "100%", "100%", "100%", "100%"),
        mr("A operating, 1P share of modelled sales", "100%", "100%", "100%", "100%", "100%", "100%"),
        mr("A unit, 1P share of sub-categories", "82.2%", "100%", "50%", "100%", "25%", "100%"),
        mr("A unit, 1P share of modelled sales", "70.9%", "100%", "13.6%", "100%", "5.6%", "100%"),
        mr("A unit, n Bring in-house (of 20)", "16.45", "20", "10", "20", "5", "20"),
        mr("B operating = unit, 1P share of sub-categories", "44.1%", "45%", "25%", "75%", "0%", "100%"),
        mr("B operating = unit, 1P share of modelled sales", "22.8%", "11.7%", "5.6%", "85.0%", "0%", "100%"),
        mr("B, n Bring in-house (of 20)", "8.82", "9", "5", "15", "0", "20"),
    ]
    story.append(styled_table(mrows, [58 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm]))
    story.append(P(
        "Table. 10,000 draws, seed 20261113. B operating equals B unit because every "
        "draw at B has coverage of at least 50%, so the strategic layer follows unit "
        "economics. A's operating mix is 20/20 Bring in every draw. A's unit mix is "
        "right-skewed: the median is still 100% 1P, but the 5th percentile of unit "
        "sales share is 13.6% (beauty and fashion only). Ranges: see the two paragraphs "
        "immediately above this table.",
        "Caption",
    ))

    story.append(P("Per sub-category, Monte Carlo shares (fragile highlighted)", "H2"))
    story.append(P(
        "A operating is 100% Bring on every line and is omitted. A unit and B "
        "(operating = unit) are shown. Ranges: as printed at the start of this section."
    ))

    mc = pd.read_csv(OUT / "monte_carlo_sub.csv")
    if "side" in mc.columns:
        a_unit = mc[(mc.side == "A") & (mc.layer == "unit")].set_index("sub_id")
        b_op = mc[(mc.side == "B") & (mc.layer == "operating")].set_index("sub_id")
    else:
        a_unit = mc[(mc.layer == "unit")].iloc[:20].set_index("sub_id")
        b_op = mc[(mc.layer == "operating")].iloc[20:40].set_index("sub_id")

    ch = [P(h, "Th") for h in [
        "Sub-category", "A unit % Bring", "A unit % Do not range", "A fragile?",
        "B % Bring", "B % Test", "B % Keep", "B fragile?",
    ]]
    crow = [ch]
    for sid in a_unit.index:
        a = a_unit.loc[sid]
        b = b_op.loc[sid]
        crow.append([
            P(a["sub_en"], "Td"),
            P(f"{a['pct_bring']:.1f}", "TdC"),
            P(f"{a['pct_unranged']:.1f}", "TdC"),
            P("Yes" if a["fragile"] else "No", "TdC"),
            P(f"{b['pct_bring']:.1f}", "TdC"),
            P(f"{b['pct_test']:.1f}", "TdC"),
            P(f"{b['pct_keep']:.1f}", "TdC"),
            P("Yes" if b["fragile"] else "No", "TdC"),
        ])
    ct = Table(crow, colWidths=[44 * mm, 18 * mm, 24 * mm, 16 * mm, 18 * mm, 16 * mm, 16 * mm, 16 * mm], repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
    ]
    for i, sid in enumerate(a_unit.index, start=1):
        if bool(a_unit.loc[sid, "fragile"]):
            style_cmds.append(("BACKGROUND", (1, i), (3, i), FRAGILE_BG))
        if bool(b_op.loc[sid, "fragile"]):
            style_cmds.append(("BACKGROUND", (4, i), (7, i), FRAGILE_BG))
    ct.setStyle(TableStyle(style_cmds))
    story.append(ct)
    story.append(P(
        "Table. Monte Carlo per mid-band sub-category, 10,000 draws, seed 20261113. "
        "Fragile (highlighted): A unit Pushchairs (58.6% Bring); B Everyday clothing (42.3%) "
        "and Sportswear (52.3%). B laundry-group Keep at 60.29% is just above the cut. "
        "Ranges as printed at the start of section 4.",
        "Caption",
    ))

    story.append(P("5. Attribution of the 15 flips, and the Amazon comparison", "H1"))
    story.append(P(
        "The brief's &#8220;four tests&#8221; is five, counting the strategic tilt. Each of the 15 "
        "A-to-B mid-band flips was isolated against: (1) contribution versus the "
        "availability-adjusted 3P take; (2) inventory liquidity; (3) the 25% GMROI "
        "hurdle; (4) demand predictability (the mid-tail rule); (5) the strategic layer. "
        "A flip is hurdle-driven only if turning the hurdle off at B undoes it."
    ))
    story.append(P(
        "Result: <b>none of the 15 is hurdle-driven.</b> The primary cause for every "
        "flip is test 1, the availability-adjusted contribution comparison. At A, "
        "coverage is 0%, so the 3P payoff is zero and any positive 1P payoff wins on "
        "the unit layer; the strategic layer then ranges the core. At B, coverage is "
        "90%, fulfilment is fully loaded, and the 3P take is the Amazon UK referral "
        "(grossed up for VAT) plus a 3% ad take and a warehouse margin. That is enough "
        "for twelve lines to stay 3P and for three mid-tail clothing lines to go to "
        "Test. The four beauty lines and baby care remain 1P at B because the THG proxy "
        "margin still clears that take at default. Isolations: running B with A's "
        "coverage (0%) brings most durables back toward Bring, but not all the way to "
        "A's result, because B's take and fully loaded fulfilment still differ. Running "
        "A with B's coverage (90%) turns durables to Test, not all the way to Keep, "
        "because entrant take and variable-only fulfilment still differ. Clothing at A "
        "with 90% coverage stays Bring. Beauty and baby care do not flip in either isolation."
    ))

    ah = [P(h, "Th") for h in ["Sub-category", "A default", "B default", "Primary cause", "Hurdle-driven?"]]
    attr = pd.read_csv(OUT / "attribution.csv")
    if "flipped" in attr.columns:
        flipped = attr[attr["flipped"] == True]
    else:
        flipped = attr[attr["rec_a"] != attr["rec_b"]]
    arows = [ah]
    for _, r in flipped.iterrows():
        cause_s = "Contribution vs 3P take (availability-adjusted)"
        hd = r["hurdle_driven"] if "hurdle_driven" in r.index else False
        hd_s = "Yes" if hd in (True, "True", "true", 1) else "No"
        arows.append([
            P(r["sub_en"], "Td"),
            P(r["rec_a"], "TdC"),
            P(r["rec_b"], "TdC"),
            P(cause_s, "Td"),
            P(hd_s, "TdC"),
        ])
    story.append(styled_table(arows, [48 * mm, 32 * mm, 32 * mm, 46 * mm, 20 * mm]))
    story.append(P(
        "Table. All 15 mid-band A-to-B flips. The five unlisted lines (skincare, makeup, "
        "haircare, fragrance, baby care) are Bring in-house on both sides at the default.",
        "Caption",
    ))

    story.append(KeepTogether([
    P("Task 4: Amazon's 61%, direction only", "H2"),
    P(
        "Amazon has disclosed that third-party sellers accounted for 61% of worldwide "
        "paid units in Q4 2025 (Amazon.com Q4 2025 results, 5 February 2026, Supplemental "
        "Financial Information, &#8220;WW seller unit mix, % of WW paid units&#8221;, 61% in Q4 2025; "
        "Q1 2025 61%; Q2 and Q3 2025 62%. Footnote: excludes Whole Foods Market. Paid units "
        "are physical and digital units sold, net of returns and cancellations, by Amazon "
        "and by sellers in its stores. "
        "https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/). "
        "That is a worldwide unit share, across all categories. B is five UK categories, "
        "measured by assumed sales (ex-VAT price times assumed weekly units)."
    ),
    ]))
    story.append(P(
        "A naive subtraction, 39% implied 1P units versus 5.6% modelled 1P sales, is a "
        "33.4 percentage-point gap in unlike units. This stress test does not treat that "
        "as a hard miscalibration. A price-mix illustration (Assumption, not an Amazon "
        "disclosure): if 1P units sold at the same average price as 3P units, 39% of units "
        "would be 39% of sales; at half the 3P average, 24.2% of sales; at twice, 56.1%. "
        "In this model the 1P recommendations at B sit in lower-priced beauty and baby "
        "care, so a sales share below a unit share is the direction the model's own prices "
        "produce, but 5.6% is still well below the half-price illustration of 24.2%. "
        "That points toward &#8220;B is 1P-light relative to Amazon's worldwide unit mix, for "
        "these five UK categories.&#8221; It does not prove B is wrong. Amazon's 61% includes "
        "categories this model does not (grocery, media, consumables) and is not a UK "
        "sales figure. The parameters that pull B's 1P sales share down are a rich 3P take, "
        "thin fully loaded contribution on durables (Currys 18.3% after 12% fulfilment) "
        "and fashion (Zalando 23% fulfilment), and 90% seller coverage. Those are named, "
        "not tuned, and v3.2 should not raise B toward 39% to close the gap."
    ))

    story.append(P("6. Task 5: what survives a direct attack", "H1"))
    story.append(P(
        "Task 5a moves the entrant haircut. Task 5b cuts the published THG, Zalando and "
        "Currys gross-margin proxies, then (at A) applies the default 5% haircut on top. "
        "A combined adverse case stacks a 25% haircut with beauty and clothing down 10 "
        "points and electronics down 5 points."
    ))
    th = [P(h, "Th") for h in [
        "Attack", "A operating 1P", "A unit 1P", "B operating = unit 1P",
    ]]

    def tr(a, b, c, d):
        return [P(a, "Td"), P(b, "TdC"), P(c, "TdC"), P(d, "TdC")]

    t5 = [th,
        tr("Default (for reference)", "20 / 20, 100% sales", "20 / 20, 100% sales", "5 / 20, 5.6% sales"),
        tr("Haircut 0%, 5%, 10%", "20, 100%", "20, 100%", "Inert: still 5, 5.6%"),
        tr("Haircut 15%", "20, 100%", "16, 88.5% sales (4 Do not range: peripherals, office, pushchairs, car seats)", "Inert: still 5, 5.6%"),
        tr("Haircut 25%", "20, 100%", "10, 13.6% sales (durables all leave; beauty and fashion remain)", "Inert: still 5, 5.6%"),
        tr("Beauty and clothing GM minus 5 points", "20, 100% (and still 20 after the 5% haircut)", "20, 100%", "0 Bring, 5 Test, 15 Keep; 0% of sales. All five default 1P lines leave."),
        tr("Beauty and clothing GM minus 10 points", "20, 100%", "20, 100%", "0 Bring, 0 Test, 20 Keep; 0% of sales"),
        tr("Electronics GM, Currys minus 3 or 5 points", "20, 100%", "12, 20.4% sales, after the 5% haircut (8 durables Do not range)", "Still 5, 5.6% (beauty and baby care unchanged)"),
        tr("Combined adverse (A: 25% haircut + both cuts; B: beauty/clothing minus 10 and electronics minus 5)", "20, 100%", "8, 9.8% sales (beauty four, baby care, footwear, sportswear, baby clothing). Some durables have a negative 1P contribution.", "0 Bring, 0% of sales"),
    ]
    story.append(styled_table(t5, [44 * mm, 42 * mm, 50 * mm, 42 * mm]))
    story.append(P(
        "Table. Mid-band counts. B haircut rows are inert because at maturity 1 the "
        "haircut interpolates to zero. The result that should be passed on: B's 1P "
        "headline does not survive a 5-point cut on the THG and Zalando proxies. A's "
        "operating 100% 1P survives every row, because of the strategic layer. A's unit "
        "100% 1P does not survive a 15% haircut or a Currys-style electronics cut.",
        "Caption",
    ))
    story.append(P(
        "<b>Survivors of every attack in this file, including Task 5 and the Monte Carlo.</b> "
        "A operating: all 20 mid-band Bring. A unit: skincare, makeup, haircare, fragrance, "
        "and baby care. B: compact appliances, peripherals, office equipment, pushchairs, "
        "and car seats (all stay Keep 3P). Beauty and baby care at B, and the three default "
        "Test clothing lines, do not survive Task 5b. Everyday clothing and sportswear at B "
        "are Monte Carlo fragile."
    ))

    story.append(P("7. Circularity and logic (Task 7)", "H1"))
    story.append(P(
        "Ranked by damage to credibility. This is a stress test of v3.1 as published."
    ))
    t7 = [
        "<b>1. The 0% coverage default is chosen to match the launch (high).</b> "
        "The mid-band 100% 1P unit result at A is implied by seller coverage of 0% plus "
        "a positive 1P contribution. When coverage is 0%, the 3P payoff is identically "
        "zero, so any positive 1P payoff wins. Task 0 finds that 0% is evidenced at the "
        "March 2026 launch and is not replaced by a later published share, so the input "
        "is defensible. It is also, plainly, chosen to match Joybuy's 1P-only launch. "
        "The &#8220;not fitted&#8221; claim is technically true: no parameter was searched to hit "
        "100% 1P. The honest wording is that parameters were not searched, but the "
        "coverage default was set to the launch-day state, and that single choice does "
        "most of the work on the unit 100% 1P result. A reviewer who hears &#8220;not fitted&#8221; "
        "may think the 100% came out as a surprise. It should not have.",
        "<b>2. B's 25% / 5.6% 1P headline rests on the THG and Zalando proxies (high).</b> "
        "A 5-point cut, which the brief asked for because those businesses are own-brand "
        "and DTC-heavy, removes all five B 1P lines. The filings are real; the step to a "
        "UK marketplace 1P margin is an Assumption, and the headline hangs on it.",
        "<b>3. The 5% haircut is a UK Assumption dressed with a China filing (medium).</b> "
        "JD 20-F FY2025, Item 4.B, pages 88 and 95, does say JD has supplier relationships "
        "and can obtain better procurement terms. Joybuy is not named. The step to &#8220;a 5% "
        "residual UK haircut, not 25%&#8221; is a judgement. The first unit break is at 13.52%. "
        "The 5% sits inside the pre-committed 0-10% band and was not searched to keep "
        "unit 1P intact. It should be labelled as a UK-local Assumption, not as a figure "
        "&#8220;from the 20-F&#8221;.",
        "<b>4. The 50% strategic threshold has no citation (medium, and not binding here).</b> "
        "At default 8% spillover, unit and operating leave 100% 1P together at 72.3% "
        "coverage, already above 50%. The threshold would matter if unit flipped earlier. "
        "It is still an Assumption with no paper behind it.",
        "<b>5. Spillover is applied in full to 1P and only with coverage to 3P (medium, not binding at A).</b> "
        "The 8% is an Assumption. It is not needed for A's default 100% 1P. It does move "
        "close B clothing verdicts (footwear at 1.06%; sportswear at 10.36%; everyday at 18.29%).",
        "<b>6. A single mid-band unit ignores cannibalisation, the buy-box, seller churn, and the long tail the model already has (medium).</b> "
        "Five of 60 bands are already Do not range at A. Task 6's request to rebuild SKU "
        "curves belongs in v3.2, not in these tables.",
        "<b>7. Using Amazon's 61% as a tuning target would itself be circular (lower, because we did not).</b> "
        "The figure is a different geography, a different mix, and units not sales. If v3.2 "
        "raised B's 1P sales share toward 39%, that would be fitting.",
    ]
    for item in t7:
        story.append(P("&#8226;  " + item, "BulletBody"))

    story.append(P("8. What in the brief does not make sense", "H1"))
    story.append(P(
        "Listed so it can be passed on. These are problems with the brief, not with the model."
    ))
    brief = [
        "<b>Task 6 is a rebuild, not a review.</b> Adding price-band distributions, Pareto "
        "SKU curves and three new categories changes the model. Mixing those results into "
        "the v3.1 verdict tables would test a model that was not the one published. Task 6 "
        "is treated as v3.2 work and is kept out of the v3.1 tables.",
        "<b>Task 4 compares unlike things.</b> Amazon's 61% is a worldwide share of paid "
        "units across all categories. B is five UK categories, measured by assumed sales. "
        "A gap will appear whether or not B is wrong. The brief's request to &#8220;say whether "
        "B is plausibly miscalibrated&#8221; is therefore too strong. This stress test reports "
        "only whether the gap points in a plausible direction.",
        "<b>The Monte Carlo &#8220;fragile&#8221; flag is a function of the ranges.</b> Drawing "
        "uniformly across ranges that were chosen in the brief (or, for coverage, reset "
        "by Task 0) makes &#8220;no verdict exceeds 60%&#8221; depend on those ranges. Every Monte "
        "Carlo result in this PDF sits next to the ranges that produced it. The 60% cut "
        "itself is sharp: laundry at B is 60.29% Keep (not fragile) and Pushchairs at A, "
        "unit, is 58.62% Bring (fragile).",
        "<b>&#8220;The four tests&#8221; lists five.</b> Contribution versus take, inventory liquidity, "
        "GMROI, demand predictability, and the strategic tilt. Attribution uses all five.",
        "<b>The brief's 0-30% entrant coverage range assumes a marketplace that Task 0 does not find.</b> "
        "Thirty percent would be a material seller base. The evidence is a 1P-only launch, "
        "a planned invitation-only curated test, &#8220;no third-party listings&#8221; as of September "
        "2026, and no published coverage share. This stress test uses 0-10% and reports "
        "0-100% only to locate the exact break.",
        "<b>Haircut, variable share and introductory commission are inert at B</b> under "
        "v3.1 construction. Asking for flip points on those at B is asking for a result "
        "the model cannot produce. They are reported as inert and were not drawn in the "
        "B Monte Carlo.",
    ]
    for item in brief:
        story.append(P("&#8226;  " + item, "BulletBody"))

    story.append(P("9. Proposed v3.2 changes (kept separate from the v3.1 results)", "H1"))
    story.append(P(
        "Main stays on v3.1. These changes go on branch v3.2. Each item is old value, "
        "new value, reason. No silent edits to defaults."
    ))
    v32 = [
        "<b>Marketplace labels.</b> Old: &#8220;A &#183; Entrant (Joybuy-like)&#8221;, &#8220;B &#183; Established "
        "(Amazon UK-like)&#8221;. New: &#8220;A &#183; Entrant&#8221;, &#8220;B &#183; Established&#8221;, with a clear note that "
        "A is Joybuy-inspired and illustrative, not Joybuy's actual economics. Real names "
        "(Joybuy, JD, Amazon, Currys, THG, Zalando) appear only where a published figure "
        "is cited. No invented brand names. Reason: generic letters keep the model from "
        "being read as Joybuy's books, while real names on citations keep the sourcing honest.",
        "<b>Honesty wording on &#8220;not fitted&#8221;.</b> Old: &#8220;the model was not fitted to Joybuy's "
        "launch.&#8221; New: &#8220;Parameters were not searched to hit a 100% 1P mix. The 0% "
        "seller-coverage default was set to the launch-day 1P-only state, which is "
        "published, and that choice does most of the work on the unit 100% 1P result. "
        "0% remains the evidenced launch value; it is an Assumption for later dates.&#8221; "
        "The default itself is not changed: Task 0 gives no published non-zero replacement.",
        "<b>No-change, with reason:</b> coverage 0% / 90%; haircut 5% (still inside the "
        "0-10% band; 25% remains a stress); spillover 8%; variable share 70%; strategic "
        "threshold 50% (label more clearly as an Assumption with no citation); "
        "introductory commission 7%; established ad take 3%. Do not tune B toward Amazon's "
        "39% implied 1P unit share.",
        "<b>Reviewer warning on the THG and Zalando proxies</b> (documentation, not a "
        "default change). The same default 25% / 5.6% numbers, with a prominent note that "
        "a 5-point cut removes all five B 1P lines. Reason: Task 5b.",
        "<b>Task 6</b> (price bands as a distribution, Pareto head / torso / tail, grocery, "
        "toys, home and garden) is implemented as v3.2 exploratory analysis. Every new "
        "proxy is cited or labelled UNVERIFIED. It is not folded into the v3.1 mid-band tables.",
    ]
    for item in v32:
        story.append(P("&#8226;  " + item, "BulletBody"))

    story.append(P("10. Three sentences that are safe to say in public, and three that are not", "H1"))
    story.append(P("Safe", "H2"))
    safe = [
        "&#8220;Under the default assumptions, the entrant's mid-band operating mix is 100% 1P, "
        "and that operating result stayed 100% in all 10,000 Monte Carlo draws inside the "
        "evidence-informed coverage range of 0-10% (and the other ranges printed in the "
        "stress-test note).&#8221;",
        "&#8220;None of the 15 flips from the entrant mid-band to the established mid-band is "
        "driven by the 25% GMROI hurdle alone; each is a contribution-versus-take comparison.&#8221;",
        "&#8220;Joybuy has not published a seller fee card, and Amazon UK referral fees are used "
        "as a labelled stand-in. JD China's 78.2% is a parent revenue share, not Joybuy's mix. "
        "The modelled entrant is inspired by Joybuy and is illustrative, not Joybuy's actual economics.&#8221;",
    ]
    for i, s in enumerate(safe, 1):
        story.append(P(f"<b>S{i}.</b> {s}", "Safe"))
    story.append(P("Not safe", "H2"))
    unsafe = [
        "&#8220;Joybuy should stock everything as 1P,&#8221; or &#8220;Joybuy's actual mix is 100% 1P because "
        "the model says so.&#8221; The model is illustrative, not Joybuy's books. Unit contribution "
        "on durables is thin and leaves 1P at a 13.52% haircut. The operating 100% result "
        "depends on a strategic layer and on 0% seller coverage.",
        "&#8220;The established scenario is miscalibrated because it shows 6% 1P sales against "
        "Amazon's 39% 1P units.&#8221; That compares worldwide units across all categories with "
        "assumed sales in five UK categories. The gap points in a 1P-light direction; it "
        "is not a hard miscalibration, and it is not a reason to retune the model.",
        "&#8220;Beauty is a clear 1P win at an established marketplace,&#8221; or &#8220;We fitted the model "
        "to Joybuy's launch.&#8221; A 5-point cut on the THG proxy turns all five B 1P lines to "
        "Test. The 0% coverage default was chosen to match the launch-day state, and that "
        "choice does most of the work on the unit 100% 1P result.",
    ]
    for i, s in enumerate(unsafe, 1):
        story.append(P(f"<b>U{i}.</b> {s}", "Unsafe"))

    story.append(P("11. Prediction score", "H1"))
    story.append(P(
        "Predictions were written to analysis/stress_test_v3.1/00_predictions.md at "
        "10:48 Asia/Calcutta (05:18 UTC) on 13 November 2026, before Task 0 was written up and before any new "
        "model run. Scoring: HIT = 1, PARTIAL = 0.5, MISS = 0. Already-known v3.1 facts "
        "were not counted as fresh hits if they were merely repeated."
    ))
    ph = [P(h, "Th") for h in ["#", "Claim (short)", "Result", "Score"]]

    def pr(n, claim, result, score):
        return [P(n, "TdC"), P(claim, "Td"), P(result, "Td"), P(score, "TdC")]

    prows = [ph,
        pr("1", "Durables A-to-B flips survive most one-at-a-time moves",
           "B's Currys-proxy lines stay off-1P except at the edges (Keep to Test, not a stable Bring).", "HIT"),
        pr("2", "Outerwear, footwear, baby clothing are Monte Carlo fragile (under 60%)",
           "Bring 73.9%, 64.4%, 77.4%. None is fragile. The default Test sits off-centre.", "MISS"),
        pr("3", "Everyday clothing and sportswear may also be fragile",
           "Max 42.3% and 52.3%. Both fragile.", "HIT"),
        pr("4", "A operating 100% 1P holds while coverage is below 50%",
           "Holds until 72.3% at 8% spillover, so it holds below 50%.", "HIT"),
        pr("5", "A unit 100% 1P breaks around 80% coverage at 8% spillover",
           "Exact: 72.3%, Pushchairs first; operating and unit together.", "PARTIAL"),
        pr("6", "At 0% spillover, unit break around 65-75% coverage",
           "Exact: 56.4%.", "PARTIAL"),
        pr("7", "Inside 0-30% coverage, A stays 100% 1P on both layers",
           "Holds. Evidence range is 0-10%; even at 50% and 8% spillover, still 20/20.", "HIT"),
        pr("8", "First unit haircut break between 10% and 15%",
           "Pushchairs at 13.52%; peripherals, office, car seats at 14.87%.", "HIT"),
        pr("9", "At 25% haircut, 10 of 20 mid-band unit Bring",
           "Confirmed. Operating stays 20/20.", "HIT"),
        pr("10", "Monte Carlo at A, operating: almost nothing fragile",
           "10,000/10,000 draws are 20/20. Zero fragile. Ranges as in section 4.", "HIT"),
        pr("11", "A unit: beauty and clothing above 60%; durables closer",
           "Beauty 100%; clothing 99.96-99.97%; durables 58.6-67.6%. Pushchairs 58.62% is the only A fragile.", "HIT"),
        pr("12", "B beauty Bring stays above 60% in the Monte Carlo",
           "95.3-95.8% Bring.", "HIT"),
        pr("13", "B electronics Keep stays above 60%",
           "Compact group 90-91%. Laundry group 60.29%, on the knife-edge. Cooking 62.2%.", "PARTIAL"),
        pr("14", "None of the 15 flips is driven by the 25% hurdle alone",
           "Confirmed. B with hurdle 0 is unchanged.", "HIT"),
        pr("15", "The 15 flips are contribution versus take",
           "Primary cause for all 15: availability-adjusted payoffs.", "HIT"),
        pr("16", "B is 1P-light versus Amazon, as a direction, not a hard miscalibration",
           "Written that way. Naive gap 39% units vs 5.6% sales, unlike things.", "HIT"),
        pr("17", "Beauty Bring at B survives a 5-point GM cut, at risk at 10 points",
           "Fails at 5 points: all five B 1P lines go to Test. The 25%/5.6% headline is gone.", "MISS"),
        pr("18", "A operating Bring survives all of Task 5",
           "All 20, including the combined adverse case.", "HIT"),
        pr("19", "A unit durables fail the 25% haircut and Currys minus 5 points",
           "Confirmed. Combined adverse: only 8 unit Bring.", "HIT"),
        pr("20", "8% spillover is not required for default mid-band unit 100% 1P",
           "At spillover 0% and coverage 0%, still 20/20.", "HIT"),
        pr("21", "Calling 0% coverage &#8220;not fitted&#8221; needs more honest wording",
           "The default was chosen to match the launch-day 1P-only state.", "HIT"),
    ]
    story.append(styled_table(prows, [10 * mm, 48 * mm, 102 * mm, 18 * mm]))
    story.append(P(
        "Score: 16 HIT + 3 PARTIAL + 2 MISS = 17.5 / 21 (83%). The two misses are which "
        "B clothing lines are fragile, and that B's beauty 1P does not survive a 5-point "
        "cut on the THG proxy.",
        "Caption",
    ))

    story.append(PageBreak())
    story.append(P("12. Method notes and sources", "H1"))
    story.append(P(
        "The engine is analysis/stress_test_v3.1/run_v31.py, run once after predictions "
        "were written. It calls the published v3.1 evaluate functions with explicit "
        "overrides; no default in own_vs_list/ was edited for this test. Outputs sit in "
        "analysis/stress_test_v3.1/outputs/. Seed 20261113. Contribution is used throughout; "
        "this note never claims profit. Sterling figures appear only where a published "
        "fee or a worked example requires them, and not as a headline claim.",
        "LeftBody",
    ))
    story.append(P(
        "The consumer site was not scraped. Partner and seller portal URLs exist; a portal "
        "is not a coverage share. Circulating 5-10% USD fee figures are UNVERIFIED.",
        "LeftBody",
    ))
    story.append(P("Task 0 sources (web search only, 13 November 2026, Asia/Calcutta)", "H2"))
    sources = [
        "The Grocer, 9 June 2026. https://www.thegrocer.co.uk/news/jdcoms-joybuy-to-open-up-to-third-party-sellers-in-marketplace-model-move/719884.article",
        "ChannelX, 15 June 2026. https://channelx.world/2026/06/joybuy-to-open-up-to-uk-and-eu-sellers/",
        "Retail Gazette, June 2026. https://www.retailgazette.co.uk/blog/2026/06/joybuy-marketplace-launch/",
        "Operator One, 24 September 2026 (updated the same day). https://o1.eu/news-insights/how-to-sell-on-joybuy",
        "LockerRules, updated 6 October 2026. https://lockerrules.co.uk/joybuy/uk-guide",
    ]
    for s in sources:
        story.append(P("&#8226;  " + s, "SourceItem"))

    story.append(P("Other citations used as published, not as Joybuy's numbers", "H2"))
    other = [
        "JD.com 20-F FY2025, Item 4.B, pages 88 and 95 (supplier terms; Joybuy is not named).",
        "Currys gross margin 18.3% (Annual Report, Note 3, p. 132) and 60 stock days (p. 50).",
        "THG Beauty gross margin 39.3% (FY2025). Zalando gross margin 39.9% and fulfilment 23% (FY2025).",
        "Amazon UK referral fees as a labelled stand-in, including the £0.25 minimum, with VAT at 20% on referral (7% becomes 8.4% of ex-VAT).",
        "Amazon Q4 2025: 61% of worldwide paid units from third-party sellers, excluding Whole Foods. Amazon.com results, 5 February 2026. https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/",
        "Joybuy's own UK margins and seller fees are not disclosed.",
    ]
    for s in other:
        story.append(P("&#8226;  " + s, "SourceItem"))

    story.append(P(
        "Full tables, the scored predictions, the Task 7 audit, the brief-problems list "
        "and the v3.2 change list also sit in analysis/stress_test_v3.1/. "
        "Main remains on v3.1 at commit 3f428e0 unless a later commit only adds this analysis.",
        "LeftBody",
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(box(
        "How to use this note",
        "This PDF is a stress test of the published v3.1 mid-band model. It is meant to "
        "be shared with peers for feedback. v3.1 itself is unchanged: main stays on the "
        "v3.1 commit. Marketplace labels (Entrant A and Established B), more honest "
        "wording on coverage, a warning on the THG and Zalando proxies, and Task 6 "
        "(price bands, SKU curves, new categories) go on branch v3.2. Do not retune "
        "B toward Amazon's 39% implied 1P unit share. Do not treat the 25% / 5.6% "
        "established 1P headline as robust: a 5-point cut on those proxies removes it.",
        width=178 * mm,
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(box(
        "Made by Ami Sata",
        "This is a portfolio decision-support prototype. It is not production software, "
        "and it is not a forecast of Joybuy's, JD's or Amazon's results. Entrant A is "
        "inspired by Joybuy and is illustrative. Established B uses Amazon UK fees as a "
        "labelled stand-in. Every external figure is cited, or it is marked UNVERIFIED. "
        "Predictions were written before the run and scored after it.",
        width=178 * mm,
    ))


def main():
    global S
    S = styles()

    tornado = pd.read_csv(OUT / "tornado.csv")
    brk = pd.read_csv(OUT / "coverage_spillover_break.csv")
    tornado_chart(tornado, FIG / "tornado.png")
    break_chart(brk, FIG / "coverage_break.png")

    story = []
    build(story)

    DOCS.mkdir(exist_ok=True)
    first = HERE / "stress_test_v3.1.pdf"
    doc = SimpleDocTemplate(
        str(first),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Stress test of the 1P vs 3P model, v3.1",
        author="Ami Sata",
        subject="Stress test of own-vs-list v3.1. Decision support, not Joybuy's actual numbers.",
    )
    doc.build(story, onFirstPage=footer_header, onLaterPages=footer_header)
    print("wrote", first, "pages", doc.page)
    shutil.copy2(first, REPO_PDF)
    shutil.copy2(first, WORKSPACE_PDF)
    print("copied to", REPO_PDF, "and", WORKSPACE_PDF)


if __name__ == "__main__":
    main()
