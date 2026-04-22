#!/usr/bin/env python3
"""
Generate summary tables for the CNS tumour registry paper.

Reads tidy CSVs from data_tidy/ and analysis_results.json,
writes CSV tables to tables/.
Run from the repository root:  python -m src.make_tables
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data_tidy"
TABS = ROOT / "tables"
TABS.mkdir(exist_ok=True)
RESULTS = ROOT / "analysis_results.json"


def table1(inc, mort, results):
    """Key endpoints at start and end of analysis window."""
    rows = []
    for stat, df, label in [("Incidence", inc, "Incidence"),
                             ("Mortality", mort, "Mortality")]:
        asr = df[(df["kennzahl"] == "Altersstandardisierte Rate") & df["age_group"].isna()]
        cnt = df[(df["kennzahl"] == "Fallzahlen") & df["age_group"].isna()]
        for sex_de, sex_en in [("weiblich", "Female"), ("männlich", "Male")]:
            a = asr[asr["sex"] == sex_de].sort_values("year")
            c = cnt[cnt["sex"] == sex_de].sort_values("year")
            rkey = f"{'inc' if stat == 'Incidence' else 'mort'}_asr_{sex_de}"
            r = results.get(rkey, {})
            apc_str = (f"{r['APC']:.2f} [{r['APC_CI95'][0]:.2f}, {r['APC_CI95'][1]:.2f}]"
                       if r else "")
            p_str = f"{r.get('APC_p', '')}" if r else ""
            rows.append({
                "Endpoint": f"{label} ASR", "Sex": sex_en,
                "2004": a[a["year"] == 2004]["value"].iloc[0],
                "2023": a[a["year"] == 2023]["value"].iloc[0],
                "APC (%) [95% CI]": apc_str, "p (APC)": p_str,
            })
            rows.append({
                "Endpoint": f"{label} counts", "Sex": sex_en,
                "2004": c[c["year"] == 2004]["value"].iloc[0],
                "2023": c[c["year"] == 2023]["value"].iloc[0],
                "APC (%) [95% CI]": "", "p (APC)": "",
            })
    pd.DataFrame(rows).to_csv(TABS / "table1_key_endpoints.csv", index=False)
    print("  table1_key_endpoints.csv")


def table2_survival(surv):
    """Age-stratified 5-year relative survival, earliest vs latest period."""
    df = surv[(surv["kennzahl"] == "Relative Rate") & (surv["horizon_years"] == 5)
              & ~surv["age_group"].str.contains("Rate|standardisiert", na=False)
              & surv["period"].isin(["2007-2008", "2021-2023"])]
    out = df[["sex", "age_group", "period", "value"]].copy()
    out.columns = ["Sex", "Age group", "Period", "5-year relative survival (%)"]
    out.to_csv(TABS / "table2_age_stratified_5y_relative_survival.csv", index=False)
    print("  table2_age_stratified_5y_relative_survival.csv")


def table2_trends(results):
    """Trend statistics summary."""
    rows = []
    labels = {
        "inc_asr_weiblich": "Incidence ASR, Female",
        "inc_asr_männlich": "Incidence ASR, Male",
        "mort_asr_weiblich": "Mortality ASR, Female",
        "mort_asr_männlich": "Mortality ASR, Male",
    }
    for key, label in labels.items():
        r = results[key]
        rows.append({
            "Endpoint": label,
            "Linear slope": r["linear_slope"], "SE": r["linear_se"],
            "R\u00b2": r["linear_r2"], "p (linear)": r["linear_p"],
            "APC (%)": r["APC"],
            "APC 95% CI (%)": f"[{r['APC_CI95'][0]}, {r['APC_CI95'][1]}]",
            "p (APC)": r["APC_p"],
            "MK Z": r["MK_Z"], "p (MK)": r["MK_p"],
            "Theil-Sen": r["TheilSen_slope"],
            "TS 95% CI": f"[{r['TheilSen_CI95'][0]}, {r['TheilSen_CI95'][1]}]",
        })
    pd.DataFrame(rows).to_csv(TABS / "table2_trend_statistics.csv", index=False)
    print("  table2_trend_statistics.csv")


def table3_survival_grid(surv):
    """Full 5-year relative survival grid across all periods."""
    df = surv[(surv["kennzahl"] == "Relative Rate") & (surv["horizon_years"] == 5)]
    periods = sorted(df["period"].unique())
    rows = []
    for sex_de in ["weiblich", "männlich"]:
        sex_en = "Female" if sex_de == "weiblich" else "Male"
        for ag in df[df["sex"] == sex_de]["age_group"].unique():
            row = {"Sex": sex_en, "Age group": ag}
            for p in periods:
                v = df[(df["sex"] == sex_de) & (df["age_group"] == ag)
                       & (df["period"] == p)]["value"]
                row[p] = int(v.iloc[0]) if len(v) else ""
            rows.append(row)
    pd.DataFrame(rows).to_csv(TABS / "table3_survival_5y_relative.csv", index=False)
    print("  table3_survival_5y_relative.csv")


def table4_prevalence(prev):
    """5-year prevalence by age band at selected years."""
    sel_years = [2004, 2008, 2013, 2018, 2023]
    rows = []
    for sex_de in ["weiblich", "männlich"]:
        sex_en = "Female" if sex_de == "weiblich" else "Male"
        for ag in ["0 - 44", "45 - 54", "55 - 64", "65 - 74", "75 und älter"]:
            row = {"Sex": sex_en, "Age group": ag}
            cnt = prev[(prev["sex"] == sex_de) & (prev["age_group"] == ag)
                       & (prev["kennzahl"] == "Fallzahlen")]
            rate = prev[(prev["sex"] == sex_de) & (prev["age_group"] == ag)
                        & (prev["kennzahl"] == "Rohe Rate")]
            for y in sel_years:
                n = cnt[cnt["year"] == y]["value"]
                r = rate[rate["year"] == y]["value"]
                row[f"n ({y})"] = int(n.iloc[0]) if len(n) else ""
                row[f"Rate ({y})"] = r.iloc[0] if len(r) else ""
            rows.append(row)
    pd.DataFrame(rows).to_csv(TABS / "table4_prevalence_5y.csv", index=False)
    print("  table4_prevalence_5y.csv")


def supp_tables(inc, mort, surv, prev):
    """Supplementary tables S1-S3 (full series)."""
    asr_i = inc[(inc["kennzahl"] == "Altersstandardisierte Rate") & inc["age_group"].isna()]
    asr_m = mort[(mort["kennzahl"] == "Altersstandardisierte Rate") & mort["age_group"].isna()]
    s1 = pd.concat([
        asr_i[["sex", "year", "value"]].assign(endpoint="Incidence ASR"),
        asr_m[["sex", "year", "value"]].assign(endpoint="Mortality ASR"),
    ]).sort_values(["endpoint", "sex", "year"])
    s1.to_csv(TABS / "supp_table_s1_asr_full_series.csv", index=False)
    print("  supp_table_s1_asr_full_series.csv")

    prev.to_csv(TABS / "supp_table_s2_prevalence_full_series.csv", index=False)
    print("  supp_table_s2_prevalence_full_series.csv")

    surv.to_csv(TABS / "supp_table_s3_survival_full_series.csv", index=False)
    print("  supp_table_s3_survival_full_series.csv")


def main():
    inc  = pd.read_csv(DATA / "incidence_tidy.csv")
    mort = pd.read_csv(DATA / "mortality_tidy.csv")
    surv = pd.read_csv(DATA / "survival_tidy.csv")
    prev = pd.read_csv(DATA / "prevalence_tidy.csv")

    with open(RESULTS) as f:
        results = json.load(f)

    print("Generating tables:")
    table1(inc, mort, results)
    table2_survival(surv)
    table2_trends(results)
    table3_survival_grid(surv)
    table4_prevalence(prev)
    supp_tables(inc, mort, surv, prev)
    print("All tables written to", TABS)


if __name__ == "__main__":
    main()
