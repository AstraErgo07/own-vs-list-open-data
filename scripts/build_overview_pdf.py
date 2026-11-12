"""Build the peer-review PDF overview for Joybuy own-vs-list v3.0."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from own_vs_list.calc import (
    BRING_IN_HOUSE,
    KEEP_3P,
    TEST_3P_FIRST,
    RULE_CITATIONS,
    comparison_mid_table,
    counts,
    evaluate_entrant,
    evaluate_established,
    mid_band_table,
    mix_curve,
    mix_summary,
)
from own_vs_list.insights import insights, nuance_findings, mix_narrative
from own_vs_list.maturity import (
    ENTRANT_AD_TAKE,
    ENTRANT_AD_TAKE_REASON,
    ENTRANT_FULFILMENT_MULTIPLIER,
    ENTRANT_FULFILMENT_REASON,
    ENTRANT_GM_HAIRCUT,
    ENTRANT_GM_HAIRCUT_REASON,
    ENTRANT_INTRO_COMMISSION,
    ENTRANT_INTRO_REASON,
    ENTRANT_LOGISTICS_MARGIN,
    ENTRANT_LOGISTICS_MARGIN_REASON,
    ENTRANT_WAREHOUSE_SHARE,
    ENTRANT_WAREHOUSE_SHARE_REASON,
    ESTABLISHED_AD_TAKE,
    ESTABLISHED_AD_TAKE_REASON,
    ESTABLISHED_LOGISTICS_MARGIN,
    ESTABLISHED_WAREHOUSE_SHARE,
    OPEN_QUESTIONS,
    SCENARIO_A_BLURB,
    SCENARIO_A_NAME,
    SCENARIO_B_BLURB,
    SCENARIO_B_NAME,
    WHY_ENTRANT_STARTS_1P,
    WHY_ENTRANT_STARTS_1P_POINTS,
    WHY_SHIFT_TO_3P,
)
from own_vs_list.uk_sources import (
    AMZN_ADVERTISING_2025,
    AMZN_SELLER_UNIT_MIX_Q4_2025,
    CURRYS_GROUP_GROSS_MARGIN_2026,
    CURRYS_STOCK_DAYS_2026,
    JD_PARENT_MIX_CAUTION,
    JOYBUY_LAUNCH_NOTE,
    JOYBUY_NO_FEES_NOTE,
    THG_BEAUTY_GROSS_MARGIN_2025,
    THG_GROUP_DISTRIBUTION_2025,
    UK_COST_OF_CAPITAL_NOTE,
    UK_VAT_NOTE,
)
from own_vs_list.published import (
    ZALANDO_FULFILMENT_PCT_2025,
    ZALANDO_GROSS_MARGIN_2025,
)
from common.text import BENCHMARK_STANDIN, FOOTER, VERSION

OUT = Path("/workspace/joybuy_own_vs_list_overview.pdf")
REPO_OUT = ROOT / "docs" / "joybuy_own_vs_list_overview.pdf"
CHART_DIR = Path("/tmp/v3_pdf_charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#1f4e79")
GOLD = colors.HexColor("#c47b17")
SLATE = colors.HexColor("#5b6770")
PALE = colors.HexColor("#f4f6f8")
LINE = colors.HexColor("#d0d5da")
WHITE = colors.white

pdfmetrics.registerFont(TTFont("Lib", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("LibBd", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("LibIt", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("LibBI", "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"))


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CoverTitle", fontName="LibBd", fontSize=22, leading=26, textColor=NAVY, spaceAfter=6))
    s.add(ParagraphStyle("CoverSub", fontName="Lib", fontSize=11, leading=15, textColor=SLATE, spaceAfter=8))
    s.add(ParagraphStyle("H1", fontName="LibBd", fontSize=14, leading=18, textColor=NAVY, spaceBefore=12, spaceAfter=6))
    s.add(ParagraphStyle("H2", fontName="LibBd", fontSize=11.5, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=4))
    s.add(ParagraphStyle("Body", fontName="Lib", fontSize=9, leading=12.5, textColor=colors.HexColor("#1a1a1a"), alignment=TA_JUSTIFY, spaceAfter=6))
    s.add(ParagraphStyle("BulletBody", fontName="Lib", fontSize=9, leading=12.5, textColor=colors.HexColor("#1a1a1a"), leftIndent=8, spaceAfter=4))
    s.add(ParagraphStyle("Caption", fontName="LibIt", fontSize=8, leading=11, textColor=SLATE, spaceAfter=8))
    s.add(ParagraphStyle("BoxTitle", fontName="LibBd", fontSize=10, leading=13, textColor=NAVY, spaceAfter=3))
    s.add(ParagraphStyle("BoxBody", fontName="Lib", fontSize=8, leading=11, textColor=colors.HexColor("#1a1a1a"), alignment=TA_JUSTIFY))
    s.add(ParagraphStyle("Th", fontName="LibBd", fontSize=7, leading=9, textColor=WHITE, alignment=TA_CENTER))
    s.add(ParagraphStyle("Td", fontName="Lib", fontSize=7, leading=9, textColor=colors.HexColor("#1a1a1a"), alignment=TA_LEFT))
    s.add(ParagraphStyle("TdC", fontName="Lib", fontSize=7, leading=9, textColor=colors.HexColor("#1a1a1a"), alignment=TA_CENTER))
    s.add(ParagraphStyle("TdBd", fontName="LibBd", fontSize=7, leading=9, textColor=colors.HexColor("#1a1a1a"), alignment=TA_LEFT))
    s.add(ParagraphStyle("Footer", fontName="Lib", fontSize=7.5, leading=9, textColor=SLATE, alignment=TA_CENTER))
    s.add(ParagraphStyle("Small", fontName="Lib", fontSize=8, leading=11, textColor=colors.HexColor("#1a1a1a"), alignment=TA_LEFT, spaceAfter=4))
    return s


S = styles()


def P(text, style="Body"):
    return Paragraph(text, S[style])


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 10 * mm, w, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Lib", 8)
    canvas.drawString(16 * mm, h - 6.5 * mm, f"Joybuy UK  ·  own stock vs marketplace listing  ·  {VERSION}")
    canvas.drawRightString(w - 16 * mm, h - 6.5 * mm, "Decision support, not Joybuy's actual numbers")
    canvas.setFillColor(PALE)
    canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(SLATE)
    canvas.setFont("Lib", 7.5)
    canvas.drawString(16 * mm, 5 * mm, "Made by Ami Sata  ·  Portfolio project")
    canvas.drawCentredString(w / 2, 5 * mm, f"Page {doc.page}")
    canvas.drawRightString(w - 16 * mm, 5 * mm, "Amazon UK fees as a labelled stand-in")
    canvas.restoreState()


def _rec_colour(rec):
    return {"Bring in-house": NAVY, "Test as 3P first": GOLD, "Keep 3P": SLATE}.get(rec, SLATE)


def mix_chart(curve: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
    ax.plot(curve["maturity"] * 100, curve["share_subs_1p"] * 100, "o-", color="#1f4e79", label="1P share of sub-categories", linewidth=2)
    ax.plot(curve["maturity"] * 100, curve["share_sales_1p"] * 100, "s--", color="#c47b17", label="1P share of modelled sales", linewidth=2)
    ax.set_xlabel("Platform maturity, %  (0 = entrant, 100 = established)")
    ax.set_ylabel("1P mix, %")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_title("Implied 1P mix as the platform matures", loc="left", color="#1f4e79", fontsize=11, fontweight="bold")
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6")
    fig.tight_layout()
    fig.savefig(path, dpi=140, facecolor="white")
    plt.close(fig)
    return path


def counts_chart(mix_a, mix_b, path: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8), sharey=True)
    labels = [BRING_IN_HOUSE, TEST_3P_FIRST, KEEP_3P]
    cols = ["#1f4e79", "#c47b17", "#5b6770"]
    for ax, mix, title in (
        (axes[0], mix_a, SCENARIO_A_NAME),
        (axes[1], mix_b, SCENARIO_B_NAME),
    ):
        vals = [mix["n_1p"], mix["n_test"], mix["n_keep"]]
        bars = ax.bar(labels, vals, color=cols)
        ax.set_title(title, loc="left", color="#1f4e79", fontsize=9, fontweight="bold")
        ax.set_ylim(0, 20)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v), ha="center", fontsize=8)
        ax.tick_params(axis="x", labelsize=7)
        ax.set_ylabel("Mid-band sub-categories")
    fig.tight_layout()
    fig.savefig(path, dpi=140, facecolor="white")
    plt.close(fig)
    return path


def breakeven_chart(cmp_: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    rec_col = {BRING_IN_HOUSE: "#1f4e79", TEST_3P_FIRST: "#c47b17", KEEP_3P: "#5b6770"}
    for rec, colour in rec_col.items():
        a = cmp_[cmp_["rec_a"] == rec]
        b = cmp_[cmp_["rec_b"] == rec]
        ax.scatter(a["take_a"] * 100, a["c1p_pct_a"] * 100, c=colour, marker="o", s=36, label=f"A · {rec}", alpha=0.9)
        ax.scatter(b["take_b"] * 100, b["c1p_pct_b"] * 100, c=colour, marker="s", s=36, label=f"B · {rec}", alpha=0.9, edgecolors="black", linewidths=0.4)
    ax.plot([-5, 30], [-5, 30], "--", color="#999", linewidth=1)
    ax.axhline(0, color="#ccc", linewidth=0.8)
    ax.set_xlabel("Effective 3P take, % of ex-VAT price")
    ax.set_ylabel("1P contribution, % of ex-VAT price")
    ax.set_title("Breakeven: 1P contribution versus the 3P take", loc="left", color="#1f4e79", fontsize=11, fontweight="bold")
    ax.legend(frameon=False, fontsize=6.5, ncol=2, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="both", color="#f0f0f0")
    fig.tight_layout()
    fig.savefig(path, dpi=140, facecolor="white")
    plt.close(fig)
    return path


def styled_table(data, col_widths, header=True):
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY if header else PALE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE if header else NAVY),
        ("FONTNAME", (0, 0), (-1, 0), "LibBd"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("LEADING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
    ]
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle(style))
    return t


def box(title, body, width=85 * mm):
    inner = [P(title, "BoxTitle"), P(body, "BoxBody")]
    t = Table([[inner]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 1, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def metric_row(pairs, widths=None):
    cells = []
    for label, value in pairs:
        cells.append([P(label, "Caption"), P(str(value), "CoverTitle")])
    t = Table([[cells[i] for i in range(len(cells))]], colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def build():
    res_a = evaluate_entrant()
    res_b = evaluate_established()
    mid_a, mid_b = mid_band_table(res_a), mid_band_table(res_b)
    mix_a, mix_b = mix_summary(res_a), mix_summary(res_b)
    cmp_ = comparison_mid_table()
    curve = mix_curve()
    ca, cb = counts(mid_a), counts(mid_b)

    p_counts = counts_chart(mix_a, mix_b, CHART_DIR / "counts.png")
    p_curve = mix_chart(curve, CHART_DIR / "curve.png")
    p_break = breakeven_chart(cmp_, CHART_DIR / "breakeven.png")

    story = []

    # ----- Page 1: purpose and central lens -----
    story.append(P("Own stock vs marketplace listing", "CoverTitle"))
    story.append(P(
        f"{VERSION}  ·  Joybuy’s UK and European business  ·  {BENCHMARK_STANDIN}",
        "CoverSub",
    ))
    story.append(P(
        "This is a decision-support overview, written so colleagues can review "
        "the method, challenge the assumptions, and improve the model. It asks, "
        "for five UK categories, whether a marketplace should stock a "
        "representative line itself (1P) or leave it with a third-party seller (3P). "
        "<b>It is not a forecast, not a profit claim, and not Joybuy’s actual numbers.</b> "
        "Joybuy has not published a seller fee card. Contribution is not profit. "
        "Prices and weekly demand are Assumptions, in pounds, exclusive of the "
        "UK’s 20% VAT, and were not scraped from retailer listings."
    ))
    story.append(P("Purpose", "H1"))
    story.append(P(
        "The central lens is a <b>scale-up entrant</b> (Joybuy-like) versus an "
        "<b>established marketplace</b> (Amazon UK-like), and the 1P versus 3P "
        "mix that follows. Scenario A uses assumed lower 1P margins, higher "
        "per-unit fulfilment (low warehouse utilisation and a subsidised same-day "
        "promise), little advertising income, and a possibly lower introductory "
        "commission. Scenario B uses published retailer cost benchmarks, Amazon UK "
        "published referral fees as a labelled stand-in, scale fulfilment, and a "
        "material model-estimated ad take. A platform-maturity slider interpolates "
        "between them. All entrant parameters are Assumptions with stated reasoning."
    ))

    story.append(P("The two scenarios, side by side", "H1"))
    usable = 178 * mm
    half = usable / 2 - 2 * mm
    left = box(
        SCENARIO_A_NAME,
        SCENARIO_A_BLURB
        + f"<br/><br/><b>Mid-band recommendations (20 sub-categories).</b> "
        f"Bring in-house {ca[BRING_IN_HOUSE]}  ·  Test as 3P first {ca[TEST_3P_FIRST]}  ·  "
        f"Keep 3P {ca[KEEP_3P]}.<br/>"
        f"<b>Implied 1P mix.</b> {mix_a['share_subs_1p']:.0%} of sub-categories, "
        f"{mix_a['share_sales_1p']:.0%} of modelled mid-band sales "
        f"(Assumption: ex-VAT price × assumed weekly units).",
        width=half,
    )
    right = box(
        SCENARIO_B_NAME,
        SCENARIO_B_BLURB
        + f"<br/><br/><b>Mid-band recommendations (20 sub-categories).</b> "
        f"Bring in-house {cb[BRING_IN_HOUSE]}  ·  Test as 3P first {cb[TEST_3P_FIRST]}  ·  "
        f"Keep 3P {cb[KEEP_3P]}.<br/>"
        f"<b>Implied 1P mix.</b> {mix_b['share_subs_1p']:.0%} of sub-categories, "
        f"{mix_b['share_sales_1p']:.0%} of modelled mid-band sales.",
        width=half,
    )
    pair = Table([[left, right]], colWidths=[usable / 2, usable / 2])
    pair.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(pair)
    story.append(Spacer(1, 4 * mm))
    story.append(Image(str(p_counts), width=usable, height=usable * 2.8 / 7.4 * 0.95))
    story.append(P(
        "Figure 1. Mid-band recommendations under the default assumptions. "
        "Bring in-house is the 1P path; Test as 3P first and Keep 3P are the 3P path. "
        "These are model estimates, not Joybuy decisions.",
        "Caption",
    ))
    story.append(P(mix_narrative(), "Body"))

    # ----- Why start 1P -----
    story.append(P("Why an entrant tends to start 1P, then shift toward 3P", "H1"))
    story.append(P(WHY_ENTRANT_STARTS_1P))
    for i, (title, body) in enumerate(WHY_ENTRANT_STARTS_1P_POINTS, 1):
        story.append(P(f"<b>{i}. {title}.</b> {body}", "BulletBody"))
    story.append(P(WHY_SHIFT_TO_3P))
    story.append(P(
        "The unit-economics test is a separate question. If, at the assumed "
        "entrant margins, 1P contribution is thin or negative on some lines, "
        "that tension is shown honestly in the findings and in the decision "
        "table. Joybuy’s 1P-only launch is published context; it is not a "
        "result this model is forced to reproduce."
    ))

    # ----- Findings -----
    story.append(P("What this run is saying", "H1"))
    for bullet in insights():
        # insights why_starts text is long and already on page 1; skip the last long dump if it's the why text
        if bullet.startswith("An entrant tends to start"):
            continue
        story.append(P(bullet, "BulletBody"))
    story.append(P("Nuance", "H2"))
    for n in nuance_findings():
        story.append(P(n, "BulletBody"))

    story.append(P("Platform maturity and the mix shift", "H1"))
    story.append(P(
        "The optional platform-maturity slider in the app interpolates linearly "
        "from A to B: the 1P margin haircut fades, fulfilment falls toward the "
        "established rate, commission blends from the assumed introductory rate "
        "toward Amazon UK published referral, and advertising and the warehouse "
        "margin move toward their established values. The chart below is the "
        "implied 1P mix along that path, under the default assumptions."
    ))
    story.append(KeepTogether([
        Image(str(p_curve), width=usable, height=usable * 2.6 / 7.4 * 0.95),
        P(
            "Figure 2. Implied 1P mix along the platform-maturity slider. The "
            "sales-weighted share can sit well below the sub-category share when "
            "1P recommendations are in lower-priced categories (beauty, baby care) "
            "and higher-priced durables stay on the 3P path. Both series are model "
            "outputs on assumed prices and weekly units, not observed GMV, and not "
            "fitted to Amazon’s disclosed 61% third-party share of paid units.",
            "Caption",
        ),
    ]))

    # ----- Decision table -----
    story.append(P("Decisions per sub-category, under each scenario", "H1"))
    story.append(P(
        "One mid-price band per sub-category. Prices are Assumptions in GBP, "
        "ex-VAT. Contribution and the 3P take are shares of that ex-VAT price. "
        "A flip means the recommendation changes between A and B."
    ))
    header = [
        P(h, "Th") for h in (
            "Category", "Sub-category", "Mid price (ex-VAT)",
            "A 1P contrib.", "A 3P take", "A rec.",
            "B 1P contrib.", "B 3P take", "B rec.", "Flip",
        )
    ]
    rows = [header]
    for _, r in cmp_.iterrows():
        rows.append([
            P(r["category_en"], "Td"),
            P(r["sub_en"], "Td"),
            P(f"£{r['price_gbp']:.0f}", "TdC"),
            P(f"{r['c1p_pct_a']:.1%}", "TdC"),
            P(f"{r['take_a']:.1%}", "TdC"),
            P(r["rec_a"], "Td"),
            P(f"{r['c1p_pct_b']:.1%}", "TdC"),
            P(f"{r['take_b']:.1%}", "TdC"),
            P(r["rec_b"], "Td"),
            P("Yes" if r["flipped"] else "—", "TdC"),
        ])
    widths = [24*mm, 38*mm, 16*mm, 16*mm, 15*mm, 26*mm, 16*mm, 15*mm, 26*mm, 10*mm]
    # sum check: 24+38+16+16+15+26+16+15+26+10 = 202, a bit over 178. Shrink.
    widths = [22*mm, 36*mm, 15*mm, 15*mm, 14*mm, 22*mm, 15*mm, 14*mm, 22*mm, 9*mm]
    story.append(styled_table(rows, widths))
    n_flip = int(cmp_["flipped"].sum())
    story.append(P(
        f"Table 1. {n_flip} of {len(cmp_)} mid-band sub-categories change "
        "recommendation between the entrant and the established scenario. "
        "Model estimates on assumed price points, not Joybuy decisions.",
        "Caption",
    ))

    # By-category mix
    story.append(P("Implied 1P mix by category", "H2"))
    ch = [P(h, "Th") for h in (
        "Category", "A: 1P subs", "A: 1P share of subs", "A: 1P share of sales",
        "B: 1P subs", "B: 1P share of subs", "B: 1P share of sales",
    )]
    crow = [ch]
    cats = {row["category"]: row for row in mix_a["by_category"]}
    cats_b = {row["category"]: row for row in mix_b["by_category"]}
    for cat in cats:
        ra, rb = cats[cat], cats_b[cat]
        crow.append([
            P(cat, "Td"),
            P(f"{ra['n_1p']} of {ra['n']}", "TdC"),
            P(f"{ra['share_subs_1p']:.0%}", "TdC"),
            P(f"{ra['share_sales_1p']:.0%}", "TdC"),
            P(f"{rb['n_1p']} of {rb['n']}", "TdC"),
            P(f"{rb['share_subs_1p']:.0%}", "TdC"),
            P(f"{rb['share_sales_1p']:.0%}", "TdC"),
        ])
    story.append(styled_table(crow, [36*mm, 22*mm, 26*mm, 26*mm, 22*mm, 26*mm, 26*mm]))
    story.append(P(
        "Table 2. 1P path share of sub-categories and of modelled mid-band sales, "
        "by category. Modelled sales are an Assumption.",
        "Caption",
    ))

    story.append(KeepTogether([
        P("Breakeven chart", "H1"),
        P(
            "Each point is a mid-band sub-category. The vertical axis is 1P "
            "contribution as a share of the ex-VAT price (the 3P take at which "
            "the platform is indifferent on contribution). The horizontal axis is "
            "the effective 3P take. Circles are the entrant (A); squares are the "
            "established marketplace (B). Points above the dashed diagonal have "
            "1P ahead on contribution. Contribution can be negative."
        ),
        Image(str(p_break), width=usable, height=usable * 3.2 / 7.4 * 0.95),
        P("Figure 3. 1P contribution versus the 3P take, mid band, scenarios A and B.", "Caption"),
    ]))

    # ----- KPIs and rules -----
    story.append(P("The four tests, and the decision rules", "H1"))
    story.append(P(
        "<b>1. Contribution per unit.</b> What is kept if we stock it, versus "
        "the 3P take if we list it. 1P has to beat the take. 1P contribution "
        "is ex-VAT price, minus cost of goods at the (maturity-adjusted) gross "
        "margin, minus fulfilment, minus a CV-scaled extra markdown, minus "
        "physical holding. The 3P take is commission (introductory Assumption "
        "at the entrant end; Amazon UK published referral as a benchmark "
        "stand-in at the established end, applied on the VAT-inclusive price) "
        "plus advertising and the platform’s warehouse margin, only for the "
        "assumed share of 3P sales fulfilled through Milton Keynes and Luton."
    ))
    story.append(P(
        "<b>2. Inventory liquidity.</b> Stock days and turn. Currys’ published "
        f"60 stock days ({CURRYS_STOCK_DAYS_2026.label}, page 50) for "
        "electronics and durables; an assumed 50 days for fashion and beauty."
    ))
    story.append(P(
        "<b>3. Return on stock (GMROI).</b> (1P contribution × 52) / (cost of "
        "goods × effective cover in weeks), tested against a 25% hurdle. "
        + UK_COST_OF_CAPITAL_NOTE
    ))
    story.append(P(
        "<b>4. Demand predictability.</b> Assumed weekly velocity and CV drive "
        "the mid-tail rule (Jiang, Jerath and Srinivasan, 2011) and a "
        "safety-stock add-on. Volatility is a cost and a warning, not an "
        "automatic override. A strategic tilt (Hagiu and Wright, 2015; "
        "Joybuy’s 1P-only launch) applies only in close cases, and never "
        "overturns a clear money loss."
    ))
    for key in ("contribution", "gmroi", "midtail", "strategic", "volatility", "maturity"):
        rule = RULE_CITATIONS[key]
        story.append(P(rule["title"], "H2"))
        story.append(P(f"{rule['basis']} <i>{rule['cite']}</i>"))
        story.append(P(f"<b>In this model.</b> {rule['in_this_model']}", "Small"))

    story.append(PageBreak())

    # ----- Sources -----
    story.append(P("Data sources", "H1"))
    story.append(P(
        "Every published figure has a document and a location. Joybuy seller "
        "commission is not among them."
    ))
    story.append(P("Joybuy launch and unpublished fees", "H2"))
    story.append(P(JOYBUY_LAUNCH_NOTE))
    story.append(P(JOYBUY_NO_FEES_NOTE))
    story.append(P("VAT", "H2"))
    story.append(P(UK_VAT_NOTE))

    src_header = [P(h, "Th") for h in ("Figure", "Value", "Where", "Label")]
    src_rows = [src_header]
    sources = [
        ("Currys group gross margin", CURRYS_GROUP_GROSS_MARGIN_2026.display,
         "Annual Report 2025/26, Note 3, page 132 (period ended 2 May 2026). Group figure, including services and the Nordics. UK&amp;I EBIT 2.9% is not used as GM.",
         CURRYS_GROUP_GROSS_MARGIN_2026.label),
        ("Currys stock days", CURRYS_STOCK_DAYS_2026.display,
         "Annual Report 2025/26, Performance review, page 50.",
         CURRYS_STOCK_DAYS_2026.label),
        ("THG Beauty adjusted GM", THG_BEAUTY_GROSS_MARGIN_2025.display,
         "THG FY2025 results: ‘Adjusted gross profit margin for the year stood at 39.3% (2024: 40.0%)’. Multi-geography.",
         THG_BEAUTY_GROSS_MARGIN_2025.label),
        ("THG group distribution", THG_GROUP_DISTRIBUTION_2025.display,
         "THG FY2025 results. Group figure (Beauty and Nutrition), used as a beauty fulfilment proxy.",
         THG_GROUP_DISTRIBUTION_2025.label),
        ("Zalando gross margin", ZALANDO_GROSS_MARGIN_2025.display,
         "FY2025 combined management report, page 82. EU figure.",
         ZALANDO_GROSS_MARGIN_2025.label),
        ("Zalando fulfilment", ZALANDO_FULFILMENT_PCT_2025.display,
         "FY2025 combined management report, page 82. EU figure.",
         ZALANDO_FULFILMENT_PCT_2025.label),
        ("Amazon WW seller unit mix", AMZN_SELLER_UNIT_MIX_Q4_2025.display,
         "Q4 2025 earnings release, 5 February 2026. Excludes Whole Foods. The FY2025 10-K does not repeat this metric.",
         AMZN_SELLER_UNIT_MIX_Q4_2025.label),
        ("Amazon advertising", AMZN_ADVERTISING_2025.display,
         "Amazon 10-K FY2025. Sold to sellers, vendors, publishers, authors and others. 3P GMV is not published.",
         AMZN_ADVERTISING_2025.label),
        ("Amazon UK referral fees", "7% to 15% by category, with clothing and beauty tiers; minimum £0.25",
         "sell.amazon.co.uk/pricing. Used as a labelled stand-in, not as Joybuy’s fees. Applied on the VAT-inclusive price.",
         "Benchmark: Amazon UK published fees"),
    ]
    for name, val, where, lab in sources:
        src_rows.append([P(name, "TdBd"), P(val, "Td"), P(where, "Td"), P(lab, "Td")])
    story.append(styled_table(src_rows, [32*mm, 38*mm, 68*mm, 40*mm]))
    story.append(P("Table 3. Published and benchmark figures used in the UK model.", "Caption"))

    story.append(P("Parent company context (JD.com in China) — not Joybuy UK figures", "H2"))
    story.append(P(JD_PARENT_MIX_CAUTION))

    story.append(P("Entrant assumptions, with reasoning", "H1"))
    story.append(P(
        "Every numerical parameter on the entrant side is an Assumption. "
        "Please challenge them; they are the main open questions."
    ))
    ass_h = [P(h, "Th") for h in ("Parameter", "Default", "Reasoning")]
    ass = [ass_h]
    for name, val, reason in (
        ("1P gross-margin haircut (relative)", f"{ENTRANT_GM_HAIRCUT:.0%}", ENTRANT_GM_HAIRCUT_REASON),
        ("1P fulfilment multiple", f"{ENTRANT_FULFILMENT_MULTIPLIER:.1f}×", ENTRANT_FULFILMENT_REASON),
        ("Advertising take, entrant", f"{ENTRANT_AD_TAKE:.1%}", ENTRANT_AD_TAKE_REASON),
        ("Advertising take, established", f"{ESTABLISHED_AD_TAKE:.1%} (range 1.5–5%)", ESTABLISHED_AD_TAKE_REASON),
        ("Introductory commission", f"{ENTRANT_INTRO_COMMISSION:.0%} (sensitivity 5–8%)", ENTRANT_INTRO_REASON),
        ("Warehouse share, entrant / established", f"{ENTRANT_WAREHOUSE_SHARE:.0%} / {ESTABLISHED_WAREHOUSE_SHARE:.0%}", ENTRANT_WAREHOUSE_SHARE_REASON),
        ("Logistics margin, entrant / established", f"{ENTRANT_LOGISTICS_MARGIN:.0%} / {ESTABLISHED_LOGISTICS_MARGIN:.0%}", ENTRANT_LOGISTICS_MARGIN_REASON),
    ):
        ass.append([P(name, "TdBd"), P(val, "TdC"), P(reason, "Td")])
    story.append(styled_table(ass, [40*mm, 32*mm, 106*mm]))
    story.append(P("Table 4. Entrant (and some established) parameters. All Assumptions or model estimates, with reasoning.", "Caption"))

    story.append(PageBreak())

    # ----- Open questions -----
    story.append(P("Open questions for reviewers", "H1"))
    story.append(P(
        "This overview exists so that others can improve the model. The "
        "entrant assumptions are the most important things to challenge. "
        "Please send comments on any of the following."
    ))
    for i, (title, body) in enumerate(OPEN_QUESTIONS, 1):
        story.append(KeepTogether([
            P(f"{i}. {title}", "H2"),
            P(body),
        ]))

    story.append(KeepTogether([
        P("Limits", "H1"),
        P(
            "Prices, weekly units and CVs are Assumptions, set in a plausible UK "
            "range, not observed Joybuy or Amazon sales, and not scraped from "
            "retailer listings. Joybuy has not published fees, 1P margins, "
            "fulfilment costs or a hurdle. Amazon UK fees are a labelled stand-in. "
            "Advertising takes are model estimates, because Amazon does not publish "
            "3P GMV and sells ads to first-party vendors as well as to sellers. "
            "Currys’ 18.3% is group gross margin, including services and the Nordics. "
            "Zalando figures are EU. THG Beauty is multi-geography. Established "
            "online electronics fulfilment (12%) is a model estimate. Mother and "
            "baby uses adjacent proxies (THG, Zalando, Currys). The 25% inventory "
            "hurdle is an Assumption. The model compares contribution on a single "
            "representative unit; it does not model competitive response, buy-box "
            "rules, or a seller’s decision to leave. Amazon’s disclosed 61% "
            "third-party share of worldwide paid units (Q4 2025) is published "
            "context for a mature mix; this model is not fitted to it."
        ),
        Spacer(1, 4 * mm),
        P(
            "The interactive model (Streamlit) lets you move the platform-maturity "
            "slider, change the entrant haircut, fulfilment multiple, introductory "
            "commission and advertising takes, and inspect a worked example for "
            "any sub-category. Run <font face='Lib'>streamlit run streamlit_app.py</font> "
            "from the repository."
        ),
        Spacer(1, 6 * mm),
        P(FOOTER, "Caption"),
    ]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPO_OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Joybuy UK: own stock vs marketplace listing (v3.0)",
        author="Ami Sata",
        subject="Decision-support overview for peer review",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    REPO_OUT.write_bytes(OUT.read_bytes())
    print(f"Wrote {OUT} and {REPO_OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
