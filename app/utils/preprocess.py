import io
import pdfplumber
import pandas as pd
from typing import List
from app.config.config import settings


def clean_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())


def parse_pdf(file_bytes: bytes) -> str:
    output = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                output.append(page.extract_text() or "")
    except Exception:
        pass
    return clean_text(" ".join(output))


def parse_csv(file_bytes: bytes) -> str:
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        return clean_text(df.to_csv(index=False))
    except Exception:
        return ""


def parse_excel(file_bytes: bytes) -> str:
    try:
        df = pd.read_excel(io.BytesIO(file_bytes))
        return clean_text(df.to_csv(index=False))
    except Exception:
        return ""


def chunk_text(text: str) -> List[str]:
    size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += size - overlap
        if start >= len(text):
            break
    return chunks
