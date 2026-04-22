import os
import re
import pandas as pd
from .utils import read_semicolon_csv, parse_numeric, value_status
from .parse_metadata import ExportMeta

def tidy_from_export(meta: ExportMeta) -> pd.DataFrame:
    csv_path = os.path.join(meta.folder, "Krebsdaten.csv")
    df = read_semicolon_csv(csv_path)
    cols = list(df.columns)
    tidy = []

    if meta.statistik in ["Inzidenz", "Mortalität"]:
        sex_cols = [c for c in cols if str(c).lower() in ["weiblich", "männlich", "maennlich"]]
        id_cols = [c for c in cols if c not in sex_cols]
        if len(id_cols) == 1:
            df_long = df.melt(id_vars=id_cols, value_vars=sex_cols, var_name="sex", value_name="value_raw")
            df_long = df_long.rename(columns={id_cols[0]: "time"})
        else:
            df_long = df.melt(id_vars=id_cols[:2], value_vars=sex_cols, var_name="sex", value_name="value_raw")
            df_long = df_long.rename(columns={id_cols[0]: "time", id_cols[1]: "age_group"})

        for _, r in df_long.iterrows():
            time = str(r["time"]).strip()
            year = int(time) if re.match(r"^\d{4}$", time) else None
            period = None if year is not None else time
            age = r.get("age_group", None)
            tidy.append({
                "export_id": meta.export_id,
                "statistik": meta.statistik,
                "kennzahl": meta.kennzahl,
                "unit": meta.unit,
                "standard_pop": meta.standard_pop,
                "sex": str(r["sex"]).strip().replace("maennlich", "männlich"),
                "year": year,
                "period": period,
                "age_group": None if age is None or str(age) == "nan" else str(age).strip(),
                "horizon_years": None,
                "value_raw": None if r["value_raw"] is None else str(r["value_raw"]).strip(),
                "value": parse_numeric(r["value_raw"]),
                "value_status": value_status(r["value_raw"]),
            })
        return pd.DataFrame(tidy)

    if meta.statistik == "Überleben":
        horizon_cols = [c for c in cols if re.match(r"^\d+$", str(c).strip())]
        id_cols = [c for c in cols if c not in horizon_cols]
        df_long = df.melt(id_vars=id_cols, value_vars=horizon_cols, var_name="horizon_years", value_name="value_raw")
        df_long = df_long.rename(columns={id_cols[0]: "period", id_cols[1]: "age_group"})
        sex = meta.sex_values[0] if meta.sex_values else None

        for _, r in df_long.iterrows():
            tidy.append({
                "export_id": meta.export_id,
                "statistik": meta.statistik,
                "kennzahl": meta.kennzahl,
                "unit": meta.unit,
                "standard_pop": meta.standard_pop,
                "sex": sex,
                "year": None,
                "period": str(r["period"]).strip(),
                "age_group": str(r["age_group"]).strip(),
                "horizon_years": int(str(r["horizon_years"]).strip()),
                "value_raw": None if r["value_raw"] is None else str(r["value_raw"]).strip(),
                "value": parse_numeric(r["value_raw"]),
                "value_status": value_status(r["value_raw"]),
            })
        return pd.DataFrame(tidy)

    if meta.statistik == "Prävalenz":
        sex_cols = [c for c in cols if str(c).lower() in ["weiblich", "männlich", "maennlich"]]
        id_cols = [c for c in cols if c not in sex_cols]
        df_long = df.melt(id_vars=id_cols[:2], value_vars=sex_cols, var_name="sex", value_name="value_raw")
        df_long = df_long.rename(columns={id_cols[0]: "year", id_cols[1]: "age_group"})

        for _, r in df_long.iterrows():
            tidy.append({
                "export_id": meta.export_id,
                "statistik": meta.statistik,
                "kennzahl": meta.kennzahl,
                "unit": meta.unit,
                "standard_pop": meta.standard_pop,
                "sex": str(r["sex"]).strip().replace("maennlich", "männlich"),
                "year": int(str(r["year"]).strip()),
                "period": None,
                "age_group": str(r["age_group"]).strip(),
                "horizon_years": None,
                "value_raw": None if r["value_raw"] is None else str(r["value_raw"]).strip(),
                "value": parse_numeric(r["value_raw"]),
                "value_status": value_status(r["value_raw"]),
            })
        return pd.DataFrame(tidy)

    raise ValueError("Unrecognised export type")
