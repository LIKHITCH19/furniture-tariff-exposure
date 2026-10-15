"""PNG charts for the README (images/)."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
IMG = ROOT / "images"

# same colors in every chart
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
RED = "#e34948"
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, SURFACE = "#e1e0d9", "#fcfcfb"
PHASE_WASH = "#f0efec"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "axes.titlesize": 13,
    "axes.titleweight": "semibold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.size": 10,
    "font.family": "sans-serif",
    "legend.frameon": False,
    "legend.fontsize": 9,
})


def subtitle(ax, text):
    ax.text(0, 1.02, text, transform=ax.transAxes, color=INK_2, fontsize=9.5, va="bottom")


def source_note(fig, text="Source: US Census Bureau international trade API (HS chapter 94 imports)"):
    fig.text(0.01, 0.01, text, color=MUTED, fontsize=8)


def save(fig, name):
    IMG.mkdir(exist_ok=True)
    fig.savefig(IMG / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  images/{name}")


def duty_rate_by_month():
    df = pd.read_csv(OUT / "01_monthly_duty_burden.csv", parse_dates=["month"])
    wide = df.pivot(index="month", columns="segment", values="effective_rate")
    phases = df.drop_duplicates("month")[["month", "phase"]]

    fig, ax = plt.subplots(figsize=(10, 5.4))

    # shade alternate policy phases
    short = {"IEEPA tariffs": "IEEPA", "IEEPA + Section 232 wood": "IEEPA +\n\u00a7232 wood",
             "Section 122": "\u00a7122", "Section 301 (2026)": "\u00a7301"}
    spans = phases.groupby("phase", sort=False).month.agg(["min", "max"])
    for i, (name, row) in enumerate(spans.iterrows()):
        start = row["min"] - pd.Timedelta(days=15)
        end = row["max"] + pd.Timedelta(days=15)
        if i % 2:
            ax.axvspan(start, end, color=PHASE_WASH, zorder=0, lw=0)
        if name in short:
            ax.text(start + (end - start) / 2, 0.375, short[name],
                    ha="center", va="top", fontsize=7.5, color=INK_2)

    # flag the Nov 2025 dip (see caveats in README)
    nov = pd.Timestamp("2025-11-01")
    ax.annotate("Nov 2025 dip:\nsee data notes", (nov, wide.loc[nov, "Wood furniture"]),
                xytext=(nov + pd.Timedelta(days=20), 0.075), fontsize=7.5, color=INK_2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

    series = [("All furniture", BLUE, 2.4), ("Wood furniture", ORANGE, 1.8),
              ("Non-wood furniture", AQUA, 1.8)]
    for name, color, lw in series:
        ax.plot(wide.index, wide[name], color=color, lw=lw, label=name,
                solid_capstyle="round", zorder=3)

    # the lines end too close together for 3 labels, so just label the total
    last = wide["All furniture"].iloc[-1]
    ax.annotate(f"{last:.1%}", (wide.index[-1], last), xytext=(6, 0),
                textcoords="offset points", va="center", fontsize=8.5, color=INK)

    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1, decimals=0))
    ax.set_ylim(0, 0.38)
    ax.grid(axis="x", visible=False)
    peak = wide["All furniture"].max()
    base = wide.loc["2024", "All furniture"].mean()
    ax.set_title(f"The duty rate on furniture went from {base:.0%} to a peak of {peak:.0%}, "
                 "then eased after the Supreme Court ruling", pad=24, fontsize=12)
    subtitle(ax, "Calculated duty as a share of customs value, US furniture imports, monthly")
    ax.legend(loc="upper left", ncol=3, bbox_to_anchor=(0, 0.92))
    source_note(fig)
    save(fig, "duty_rate_by_month.png")


def sourcing_shift():
    df = pd.read_csv(OUT / "04_sourcing_shift.csv")
    period = df["period_compared"].iloc[0]
    df = df[df["share_change_pts"].abs() >= 0.1].sort_values("share_change_pts")

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [BLUE if v > 0 else RED for v in df["share_change_pts"]]
    ax.barh(df["country"], df["share_change_pts"], color=colors, height=0.6, zorder=3)

    for y, (v, pct) in enumerate(zip(df["share_change_pts"], df["value_change_pct"])):
        label = f"{v:+.1f} pts  ({pct:+.0%} $)"
        ax.annotate(label, (v, y), xytext=(5 if v > 0 else -5, 0), textcoords="offset points",
                    ha="left" if v > 0 else "right", va="center", fontsize=8.5, color=INK)

    ax.axvline(0, color=MUTED, lw=1, zorder=4)
    ax.grid(axis="y", visible=False)
    # leave room past each bar end for its label
    ax.set_xlim(df["share_change_pts"].min() * 1.75, df["share_change_pts"].max() * 1.6)
    ax.set_xlabel("Change in share of US furniture imports (percentage points)")
    china = df.set_index("country").loc["China", "share_change_pts"]
    ax.set_title(f"China lost {abs(china):.0f} points of share. Vietnam gained the most share, "
                 "Cambodia and Thailand the most volume", pad=24, fontsize=11.5)
    subtitle(ax, f"{period} (same months each year). Bracket = change in dollar value")
    source_note(fig)
    save(fig, "sourcing_shift.png")


def duty_rate_by_country():
    df = pd.read_csv(OUT / "03_duty_rate_by_country.csv")
    groups = {1: "Baseline (Jan 2023-Jan 2025)", 3: "Peak (Oct 2025-Feb 2026)", 4: "Now", 5: "Now"}
    df["period"] = df["phase_id"].map(groups)
    agg = df.groupby(["country", "period"])[["duty_usd", "consumption_usd"]].sum()
    rates = (agg["duty_usd"] / agg["consumption_usd"]).unstack()
    rates = rates.rename(columns={"Now": "Now (Mar-Aug 2026)"}).sort_values("Now (Mar-Aug 2026)")

    fig, ax = plt.subplots(figsize=(9, 5.8))
    y = range(len(rates))
    for i, (_, r) in enumerate(rates.iterrows()):
        ax.plot([r.min(), r.max()], [i, i], color=GRID, lw=2, zorder=2)

    marks = [("Baseline (Jan 2023-Jan 2025)", MUTED), ("Peak (Oct 2025-Feb 2026)", ORANGE),
             ("Now (Mar-Aug 2026)", BLUE)]
    for col, color in marks:
        ax.scatter(rates[col], y, s=64, color=color, edgecolor=SURFACE, linewidth=2,
                   zorder=3, label=col)

    for i, v in enumerate(rates["Now (Mar-Aug 2026)"]):
        ax.annotate(f"{v:.0%}", (v, i), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=8, color=INK)

    ax.set_yticks(list(y), rates.index)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", visible=False)
    now = rates["Now (Mar-Aug 2026)"].sort_values(ascending=False)
    ratio = now.iloc[0] / now.iloc[1]
    how_much = "about twice" if 1.8 <= ratio <= 2.2 else f"{ratio:.1f} times"
    ax.set_title(f"{now.index[0]} still pays {how_much} the rate of any other major supplier", pad=24)
    subtitle(ax, "Effective duty rate on furniture by supplier, 12 largest suppliers")
    ax.legend(loc="lower right")
    source_note(fig)
    save(fig, "duty_rate_by_country.png")


def extra_duty_by_product():
    df = pd.read_csv(OUT / "05_exposure_by_product.csv", dtype={"hs6": str})
    df = df.sort_values("extra_duty_usd")
    df["label"] = df["hs_label"] + "  (" + df["hs6"] + ")"

    fig, ax = plt.subplots(figsize=(9.5, 6))
    colors = [ORANGE if w else BLUE for w in df["is_wood"]]
    ax.barh(df["label"], df["extra_duty_usd"] / 1e6, color=colors, height=0.6, zorder=3)
    for i, (v, pts) in enumerate(zip(df["extra_duty_usd"] / 1e6, df["rate_change_pts"])):
        ax.annotate(f"${v:,.0f}M  (+{pts:.0f} pts)", (v, i), xytext=(5, 0),
                    textcoords="offset points", va="center", fontsize=8.5, color=INK)

    ax.set_xlim(0, df["extra_duty_usd"].max() / 1e6 * 1.3)
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}M"))
    ax.grid(axis="y", visible=False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=ORANGE), plt.Rectangle((0, 0), 1, 1, color=BLUE)]
    ax.legend(handles, ["Wood", "Non-wood"], loc="lower right")
    total = df["extra_duty_usd"].sum() / 1e9
    ax.set_title(f"${total:.1f}B in extra duty over the last 12 months, led by upholstered wood seating",
                 pad=24, fontsize=12)
    subtitle(ax, "Duty paid minus what the same goods would have paid at each line's 2024 rate. "
                 "Bracket = rate change")
    source_note(fig)
    save(fig, "extra_duty_by_product.png")


def price_vs_duty():
    df = pd.read_csv(OUT / "07_price_vs_duty.csv", parse_dates=["month"])
    df = df[df["month"] >= "2024-01-01"]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.fill_between(df["month"], df["pre_duty_index"], df["with_duty_index"],
                    color=ORANGE, alpha=0.1, lw=0, zorder=1)
    for col, color, name in [("with_duty_index", ORANGE, "Price including duty"),
                             ("pre_duty_index", BLUE, "Supplier price before duty (BLS)")]:
        ax.plot(df["month"], df[col], color=color, lw=2.2, label=name, zorder=3)
        last = df.dropna(subset=[col]).iloc[-1]
        ax.annotate(f"{last[col]:.0f}", (last["month"], last[col]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8.5, color=INK)

    ax.axhline(100, color=MUTED, lw=1, zorder=2)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Index, Jan 2025 = 100")
    ax.set_title("Suppliers did not cut prices to absorb the tariffs, so US buyers paid them", pad=24)
    subtitle(ax, "Furniture import prices before and after duty. The shaded gap is the tariff cost")
    ax.legend(loc="upper left")
    source_note(fig, "Sources: BLS import price index EIUIR41000 (furniture, household goods; excludes duty); "
                     "US Census calculated duty. Oct 2025 not published by BLS")
    save(fig, "price_vs_duty.png")


def main():
    print("writing charts:")
    duty_rate_by_month()
    sourcing_shift()
    duty_rate_by_country()
    extra_duty_by_product()
    price_vs_duty()


if __name__ == "__main__":
    main()
