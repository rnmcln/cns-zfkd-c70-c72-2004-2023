import re
import numpy as np
import pandas as pd

STATUS_MAP = {"*": "suppressed", "x": "not_estimable"}

def value_status(v):
    if v is None:
        return "missing"
    s = str(v).strip()
    if s == "" or s.lower() == "nan":
        return "missing"
    if s in STATUS_MAP:
        return STATUS_MAP[s]
    if s.startswith("<"):
        return "suppressed"
    return "observed"

def parse_numeric(v):
    if v is None:
        return np.nan
    s = str(v).strip()
    if s == "" or s.lower() == "nan":
        return np.nan
    if s in STATUS_MAP or s.startswith("<"):
        return np.nan
    s = s.replace(".", "") if re.match(r"^\d{1,3}(\.\d{3})+(,\d+)?$", s) else s
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return np.nan

def read_semicolon_csv(path):
    df = pd.read_csv(path, sep=";", dtype=str, engine="python")
    df = df.dropna(axis=1, how="all")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    return df
