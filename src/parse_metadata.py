import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ExportMeta:
    export_id: str
    folder: str
    last_update: Optional[str]
    statistik: Optional[str]
    kennzahl: Optional[str]
    unit: Optional[str]
    diagnosis_label: Optional[str]
    sex_values: List[str]
    years: Optional[List[int]]
    periods: Optional[List[str]]
    age_groups: Optional[List[str]]
    standard_pop: Optional[str]
    interval_length_years: Optional[List[str]]

def parse_metadata(text: str, export_id: str, folder: str) -> ExportMeta:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    last_update = None
    if lines and lines[0].lower().startswith("letzte aktualisierung"):
        m = re.search(r":\s*(.+)$", lines[0])
        last_update = m.group(1).strip() if m else None

    statistik = None
    kennzahl = None
    unit = None
    if len(lines) >= 2:
        parts = lines[1].split(",")
        if len(parts) >= 2:
            statistik = parts[0].strip()
            rest = ",".join(parts[1:]).strip()
        else:
            rest = lines[1].strip()
        m = re.match(r"(.+?)\s+in Deutschland\s*(.*)$", rest)
        if m:
            kennzahl = m.group(1).strip()
            unit = m.group(2).strip() if m.group(2) else None
        else:
            kennzahl = rest

    diagnosis = None
    sex = []
    years = None
    periods = None
    age_groups = None
    standard = None
    interval = None

    for l in lines:
        if l.startswith("Diagnose:"):
            diagnosis = l.split(":", 1)[1].strip()
        if l.startswith("Geschlecht:"):
            s = l.split(":", 1)[1].strip()
            sex = [x.strip() for x in s.split(",")]
        if l.startswith("Jahre:"):
            y = l.split(":", 1)[1].strip()
            if "," in y:
                periods = [x.strip() for x in y.split(",")]
            else:
                m2 = re.match(r"(\d{4})\s*-\s*(\d{4})", y)
                if m2:
                    start = int(m2.group(1))
                    end = int(m2.group(2))
                    years = list(range(start, end + 1))
                else:
                    try:
                        years = [int(y)]
                    except Exception:
                        years = None
        if l.startswith("Altersgruppen:"):
            a = l.split(":", 1)[1].strip()
            age_groups = [x.strip() for x in a.split(",")]
        if l.startswith("Bevölkerungsstandard:"):
            standard = l.split(":", 1)[1].strip()
        if l.startswith("Intervall-Länge in Jahren:"):
            iv = l.split(":", 1)[1].strip()
            interval = [x.strip() for x in iv.split(",")]

    return ExportMeta(
        export_id=export_id,
        folder=folder,
        last_update=last_update,
        statistik=statistik,
        kennzahl=kennzahl,
        unit=unit,
        diagnosis_label=diagnosis,
        sex_values=sex,
        years=years,
        periods=periods,
        age_groups=age_groups,
        standard_pop=standard,
        interval_length_years=interval,
    )
