import io
import pdfplumber
import pandas as pd
from typing import Dict, Any


def parse_pdf(file_bytes: bytes) -> Dict[str, Any]:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return {"raw_text": text}
    except Exception as e:
        return {"error": str(e)}


def parse_spreadsheet(file_bytes: bytes, file_type: str) -> Dict[str, Any]:
    try:
        if file_type == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
        
        return {
            "columns": df.columns.tolist(),
            "rows": df.to_dict(orient="records"),
            "total_rows": len(df)
        }
    except Exception as e:
        return {"error": str(e)}