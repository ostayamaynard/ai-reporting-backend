from pathlib import Path
import pandas as pd
from PyPDF2 import PdfReader
from .mapping import default_mapping, resolve_kpi_for_column

def parse_file(file_path: str):
    suffix = Path(file_path).suffix.lower()
    if suffix in [".csv",".tsv"]:
        df = pd.read_csv(file_path)
    elif suffix in [".xlsx",".xls"]:
        df = pd.read_excel(file_path)
    elif suffix == ".pdf":
        text = ""
        for p in PdfReader(file_path).pages:
            text += p.extract_text() or ""
        rows=[]
        for line in text.splitlines():
            if ":" in line:
                k,v = line.split(":",1)
                k,v = k.strip(), v.strip().replace(",","")
                try: rows.append({k: float(v)})
                except: pass
        df = pd.DataFrame(rows) if rows else pd.DataFrame()
    else:
        raise ValueError("Unsupported file type")
    date_col=None
    for c in ["date","Date","Created Date","Created_Date"]:
        if c in df.columns: date_col=c; break
    if date_col is None:
        df["date"]=pd.Timestamp.today().normalize(); date_col="date"
    df[date_col]=pd.to_datetime(df[date_col], errors="coerce").dt.date
    mapping=default_mapping(); kpi_cols={}
    for col in df.columns:
        kpi=resolve_kpi_for_column(col, mapping)
        if kpi: kpi_cols[kpi]=col
    metrics=[]
    if not kpi_cols:
        for col in df.select_dtypes(include="number").columns:
            metrics.append({"kpi": col, "values": df.groupby(date_col)[col].sum().to_dict()})
    else:
        for kpi,col in kpi_cols.items():
            metrics.append({"kpi": kpi, "values": df.groupby(date_col)[col].sum().to_dict()})
    return metrics
