#!/usr/bin/env python3
"""
Generate all publication figures for the CNS tumour registry paper.

Reads tidy CSVs from data_tidy/ and writes PDF + PNG to figures/.
Run from the repository root:  python -m src.make_figures
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data_tidy"
FIGS = ROOT / "figures"
FIGS.mkdir(exist_ok=True)

# ── palette ──
COLOR_F = "#C1694F"
COLOR_M = "#4878A8"
SHADE_F = ["#E8C4B8", "#D4956E", "#C1694F", "#A0472E", "#7A2E1A"]
SHADE_M = ["#B8C8D8", "#88A8C8", "#6898C0", "#4878A8", "#2A5A88"]
BAR_F   = ["#E8C4B8", "#C1694F", "#A0472E"]
BAR_M   = ["#B8C8D8", "#6898C0", "#3A6898"]

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 10,
    "axes.titlesize": 11, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
})

AGE_ORDER_PREV  = ["0 - 44", "45 - 54", "55 - 64", "65 - 74", "75 und älter"]
AGE_LABELS_PREV = ["0\u201344", "45\u201354", "55\u201364", "65\u201374", "\u226575"]
MARKERS = ["o", "s", "^", "D", "v"]

PERIOD_ORDER = [
    "2007-2008", "2009-2010", "2011-2012", "2013-2014",
    "2015-2016", "2017-2018", "2019-2020", "2021-2023",
]
PERIOD_SHORT = ["07-08", "09-10", "11-12", "13-14",
                "15-16", "17-18", "19-20", "21-23"]


def despine(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}")


# ════════════════════════════════════════════════════════════════════
def figure1(inc, mort):
    """ASR incidence & mortality, 2005-2023."""
    inc_asr = inc[(inc["kennzahl"] == "Altersstandardisierte Rate")
                  & inc["age_group"].isna() & (inc["year"] >= 2005)]
    mort_asr = mort[(mort["kennzahl"] == "Altersstandardisierte Rate")
                    & mort["age_group"].isna() & (mort["year"] >= 2005)]

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.5, 3.0))
    for ax, df, title in [(axa, inc_asr, "Incidence"), (axb, mort_asr, "Mortality")]:
        for sex, color, label in [("männlich", COLOR_M, "Male"),
                                  ("weiblich", COLOR_F, "Female")]:
            d = df[df["sex"] == sex].sort_values("year")
            ax.plot(d["year"], d["value"], "-o", color=color, ms=3, lw=1.2)
            ax.annotate(label, xy=(d["year"].iloc[-1], d["value"].iloc[-1]),
                        xytext=(6, 0), textcoords="offset points",
                        fontsize=9, fontweight="bold", color=color, va="center")
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("Year"); ax.set_ylabel("Age-standardised rate per 100\u202f000")
        ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
        despine(ax)

    axa.text(0.02, 0.97, "(a)", transform=axa.transAxes, fontsize=12,
             fontweight="bold", va="top")
    ymin, ymax = axb.get_ylim()
    axb.set_ylim(ymin, ymax + 0.15 * (ymax - ymin))
    axb.text(0.02, 0.97, "(b)", transform=axb.transAxes, fontsize=12,
             fontweight="bold", va="top")
    fig.tight_layout()
    save(fig, "figure1_asr_incidence_mortality")


def figure2(inc, mort):
    """Incidence & mortality counts."""
    inc_cnt = inc[(inc["kennzahl"] == "Fallzahlen") & inc["age_group"].isna()
                  & (inc["year"] >= 2005)]
    mort_cnt = mort[(mort["kennzahl"] == "Fallzahlen") & mort["age_group"].isna()
                    & (mort["year"] >= 2005)]

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.5, 3.0))
    for ax, df, title, yl in [(axa, inc_cnt, "Incidence", "Number of new cases"),
                               (axb, mort_cnt, "Mortality", "Number of deaths")]:
        for sex, color, label in [("männlich", COLOR_M, "Male"),
                                  ("weiblich", COLOR_F, "Female")]:
            d = df[df["sex"] == sex].sort_values("year")
            ax.plot(d["year"], d["value"], "-o", color=color, ms=3, lw=1.2)
            ax.annotate(label, xy=(d["year"].iloc[-1], d["value"].iloc[-1]),
                        xytext=(6, 0), textcoords="offset points",
                        fontsize=9, fontweight="bold", color=color, va="center")
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("Year"); ax.set_ylabel(yl)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
        despine(ax)
        ax.text(0.02, 0.97, "(a)" if ax is axa else "(b)",
                transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")
    fig.tight_layout()
    save(fig, "figure2_counts_incidence_mortality")


def _survival_bars(surv, kennzahl, ylabel, outname):
    """Helper for Figures 3 and S2."""
    df = surv[(surv["kennzahl"] == kennzahl)
              & (surv["age_group"] == "Altersstandardisiert - 15 und Älter")
              & surv["horizon_years"].isin([1, 2, 5])]
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, sex_de, sex_en, colors, pl in [
            (axa, "weiblich", "Female", BAR_F, "(a)"),
            (axb, "männlich", "Male", BAR_M, "(b)")]:
        d = df[df["sex"] == sex_de]
        x = np.arange(len(PERIOD_ORDER)); w = 0.25
        for i, (h, c) in enumerate(zip([1, 2, 5], colors)):
            vals = [d[(d["period"] == p) & (d["horizon_years"] == h)]["value"].iloc[0]
                    if len(d[(d["period"] == p) & (d["horizon_years"] == h)]) else 0
                    for p in PERIOD_ORDER]
            ax.bar(x + (i - 1) * w, vals, w, color=c, label=f"{h}-year",
                   edgecolor="white", linewidth=0.5)
        ax.set_xticks(x); ax.set_xticklabels(PERIOD_SHORT, rotation=45, ha="right")
        ax.set_xlabel("Diagnostic period"); ax.set_ylabel(ylabel); ax.set_ylim(0, 100)
        ax.legend(loc="upper center", ncol=3, frameon=False, fontsize=9,
                  bbox_to_anchor=(0.5, 1.12))
        ax.set_title(sex_en, fontsize=13, fontweight="bold", pad=35,
                     color=colors[1])
        ax.text(0.02, 0.97, pl, transform=ax.transAxes, fontsize=12,
                fontweight="bold", va="top")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, outname)


def figure3(surv):
    _survival_bars(surv, "Relative Rate", "Relative survival (%)",
                   "figure3_relative_survival_periods")


def figure4(surv):
    """Age gradient 5-year relative survival."""
    age_order = ["15 - 44", "45 - 54", "55 - 64", "65 - 74", "75 und älter"]
    age_lbl = ["15\u201344", "45\u201354", "55\u201364", "65\u201374", "\u226575"]
    df = surv[(surv["kennzahl"] == "Relative Rate") & (surv["horizon_years"] == 5)
              & ~surv["age_group"].str.contains("Rate|standardisiert", na=False)
              & surv["period"].isin(["2007-2008", "2021-2023"])]
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, sex_de, sex_en, cols, pl in [
            (axa, "weiblich", "Female", ["#E8C4B8", "#A0472E"], "(a)"),
            (axb, "männlich", "Male", ["#B8C8D8", "#3A6898"], "(b)")]:
        d = df[df["sex"] == sex_de]; x = np.arange(len(age_order)); w = 0.35
        for i, (per, c) in enumerate(zip(["2007-2008", "2021-2023"], cols)):
            vals = [d[(d["period"] == per) & (d["age_group"] == ag)]["value"].iloc[0]
                    if len(d[(d["period"] == per) & (d["age_group"] == ag)]) else 0
                    for ag in age_order]
            ax.bar(x + (i - 0.5) * w, vals, w, color=c, label=per,
                   edgecolor="white", linewidth=0.5)
        ax.set_xticks(x); ax.set_xticklabels(age_lbl)
        ax.set_xlabel("Age group"); ax.set_ylabel("5-year relative survival (%)")
        ax.set_ylim(0, 100); ax.set_title(sex_en, fontsize=12, fontweight="bold")
        ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
        despine(ax)
        ax.text(0.02, 0.97, pl, transform=ax.transAxes, fontsize=12,
                fontweight="bold", va="top")
    fig.tight_layout()
    save(fig, "figure4_age_gradient_rel_survival_5y")


def _prevalence_panels(prev, kennzahl, ylabel, outname):
    """Helper for Figure 5 and Supp S3 — distinct markers, shared black legend below."""
    df = prev[prev["kennzahl"] == kennzahl]
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.5, 4.0))
    for ax, sex_de, sex_en, shades, pl in [
            (axa, "weiblich", "Female", SHADE_F, "(a)"),
            (axb, "männlich", "Male", SHADE_M, "(b)")]:
        ax.set_title(sex_en, fontsize=11, fontweight="bold")
        for ag, al, c, m in zip(AGE_ORDER_PREV, AGE_LABELS_PREV, shades, MARKERS):
            dd = df[(df["sex"] == sex_de) & (df["age_group"] == ag)].sort_values("year")
            ax.plot(dd["year"], dd["value"], "-", marker=m, color=c,
                    ms=3.5, lw=1.2, markeredgecolor=c, markerfacecolor=c)
        ax.set_xlabel("Year"); ax.set_ylabel(ylabel)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
        despine(ax)
        ax.text(0.02, 0.97, pl, transform=ax.transAxes, fontsize=12,
                fontweight="bold", va="top")
    handles = [mlines.Line2D([], [], color="black", marker=m, ms=5, lw=1,
               markeredgecolor="black", markerfacecolor="black", label=al)
               for al, m in zip(AGE_LABELS_PREV, MARKERS)]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False,
               fontsize=9, handlelength=1.8, handletextpad=0.5,
               columnspacing=1.5, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    save(fig, outname)


def figure5(prev):
    _prevalence_panels(prev, "Rohe Rate",
                       "5-year prevalence rate per 100\u202f000",
                       "figure5_prevalence_5y_crude_rate_age")


def supp_s1(inc):
    """Extended ASR 1999-2023."""
    df = inc[(inc["kennzahl"] == "Altersstandardisierte Rate") & inc["age_group"].isna()]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for sex, color, label in [("männlich", COLOR_M, "Male"),
                              ("weiblich", COLOR_F, "Female")]:
        d = df[df["sex"] == sex].sort_values("year")
        ax.plot(d["year"], d["value"], "-o", color=color, ms=3.5, lw=1.3)
        ax.annotate(label, xy=(d["year"].iloc[-1], d["value"].iloc[-1]),
                    xytext=(8, 0), textcoords="offset points",
                    fontsize=10, fontweight="bold", color=color, va="center")
    ax.axvspan(1999, 2004, alpha=0.12, color="grey", zorder=0)
    ax.text(1999.3, ax.get_ylim()[1] * 0.98,
            "Pre-study period\n(incomplete registration)",
            fontsize=8.5, fontstyle="italic", va="top", color="#444444")
    ax.set_xlabel("Year"); ax.set_ylabel("Age-standardised rate per 100\u202f000")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(5)); despine(ax)
    fig.tight_layout()
    save(fig, "supp_figure_s1_asr_extended_1999_2023")


def supp_s2(surv):
    _survival_bars(surv, "Absolute Rate", "Absolute survival (%)",
                   "supp_figure_s2_absolute_survival_periods")


def supp_s3(prev):
    _prevalence_panels(prev, "Fallzahlen",
                       "5-year prevalence (number of cases)",
                       "supp_figure_s3_prevalence_5y_counts_age")


def main():
    inc  = pd.read_csv(DATA / "incidence_tidy.csv")
    mort = pd.read_csv(DATA / "mortality_tidy.csv")
    surv = pd.read_csv(DATA / "survival_tidy.csv")
    prev = pd.read_csv(DATA / "prevalence_tidy.csv")

    print("Generating figures:")
    figure1(inc, mort)
    figure2(inc, mort)
    figure3(surv)
    figure4(surv)
    figure5(prev)
    supp_s1(inc)
    supp_s2(surv)
    supp_s3(prev)
    print("All figures written to", FIGS)


if __name__ == "__main__":
    main()
