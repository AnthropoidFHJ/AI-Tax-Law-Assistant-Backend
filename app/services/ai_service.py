from typing import List, Dict, Any
from fastapi import UploadFile
from app.utils.preprocess import parse_pdf, parse_csv, parse_excel, chunk_text, clean_text
from app.utils.data_clean import encrypt_bytes
from app.config.config import settings, SYSTEM_PROMPT
from app.schemas.schema import TaxInput, TaxComputation, TaxReturnResult
from app.models.model import TaxReturn, AuditLog
from sqlalchemy.orm import Session
import openai
from pinecone import Pinecone
import json
import os

# Initialize external clients lazily
_openai_initialized = False
_pinecone_initialized = False
_pc_client = None
_openai_client = None


def _init_openai():
    global _openai_initialized, _openai_client
    if not _openai_initialized and settings.OPENAI_API_KEY:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        _openai_initialized = True


def _init_pinecone():
    global _pinecone_initialized, _pc_client
    if not _pinecone_initialized and settings.PINECONE_API_KEY:
        _pc_client = Pinecone(api_key=settings.PINECONE_API_KEY)
        # Create index if not exists
        existing_indexes = [idx.name for idx in _pc_client.list_indexes()]
        if settings.PINECONE_INDEX not in existing_indexes:
            _pc_client.create_index(
                name=settings.PINECONE_INDEX,
                dimension=1536,  # OpenAI embedding size
                metric="cosine",
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
            )
        _pinecone_initialized = True


def _embed_texts(texts: List[str]) -> List[List[float]]:
    _init_openai()
    if not _openai_initialized or not _openai_client:
        return [[0.0] * 1536 for _ in texts]  # fallback zeros
    resp = _openai_client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in resp.data]


class AIService:
    def __init__(self):
        _init_openai()
        _init_pinecone()
        self.index = _pc_client.Index(settings.PINECONE_INDEX) if _pinecone_initialized else None

    def ingest_document(self, file: UploadFile) -> Dict[str, Any]:
        raw = file.file.read()
        text = ""
        if file.filename.lower().endswith(".pdf"):
            text = parse_pdf(raw)
        elif file.filename.lower().endswith(".csv"):
            text = parse_csv(raw)
        elif file.filename.lower().endswith(".xlsx"):
            text = parse_excel(raw)
        else:
            text = clean_text(raw.decode(errors="ignore"))
        chunks = chunk_text(text)
        embeddings = _embed_texts(chunks)
        if self.index:
            vectors = [(f"{file.filename}-{i}", embeddings[i], {"source": file.filename}) for i in range(len(chunks))]
            self.index.upsert(vectors=vectors)
        # Encrypt and discard raw
        nonce, ct = encrypt_bytes(raw)
        return {
            "filename": file.filename,
            "extracted_text_preview": text[:250],
            "chunks": len(chunks),
            "encrypted_nonce": nonce.hex(),
            "encrypted_blob": ct.hex(),
            "status": "ingested"
        }

    def semantic_search(self, query: str, top_k: int = 5) -> List[str]:
        if not self.index:
            return []
        emb = _embed_texts([query])[0]
        res = self.index.query(vector=emb, top_k=top_k, include_metadata=True)
        return [m.metadata.get("source", "") for m in res.matches]

    def compute_tax(self, data: TaxInput) -> TaxComputation:
        # Simplified slab logic example (figures illustrative; adjust to actual BD slabs)
        income = sum(data.income_items.values())
        deductions = sum(data.deductions.values())
        taxable = max(income - deductions, 0)
        remaining = taxable
        slab_tax = 0.0
        slabs = [
            (350000, 0.0),  # basic exemption (example only)
            (100000, 0.05),
            (400000, 0.10),
            (500000, 0.15),
            (float('inf'), 0.20)
        ]
        for limit, rate in slabs:
            if remaining <= 0:
                break
            apply_amount = min(remaining, limit)
            slab_tax += apply_amount * rate
            remaining -= apply_amount
        surcharge = 0.0  # placeholder for high-income surcharge
        inv_total = sum(data.investments.values())
        rebate = min(inv_total * 0.15, slab_tax * 0.15)  # placeholder rule
        payable = max(slab_tax + surcharge - rebate, 0)
        refundable = 0.0  # implement if advance tax > payable
        breakdown = {
            "income_items": data.income_items,
            "deductions": data.deductions,
            "investments": data.investments,
            "slab_tax_raw": slab_tax,
        }
        return TaxComputation(
            gross_income=income,
            total_deductions=deductions,
            taxable_income=taxable,
            slab_tax=slab_tax,
            surcharge=surcharge,
            rebate=rebate,
            payable=payable,
            refundable=refundable,
            breakdown=breakdown,
        )

    def generate_return(self, db: Session, data: TaxInput) -> TaxReturnResult:
        comp = self.compute_tax(data)
        flags = []
        required_fields = [data.tin, data.assessment_year]
        if not all(required_fields):
            flags.append("Missing mandatory identifiers (TIN or assessment year)")
        if not data.income_items.get("salary"):
            flags.append("Salary component missing or zero")
        citations = ["Section 44(2)(b)", "Income Tax Ordinance 1984"]  # placeholders
        result = TaxReturnResult(
            tin=data.tin,
            assessment_year=data.assessment_year,
            computation=comp,
            compliance_flags=flags,
            citations=citations,
            disclaimer="AI-generated; not a substitute for certified tax lawyer. User responsible for final submission.",
        )
        record = TaxReturn(
            tin=data.tin,
            assessment_year=data.assessment_year,
            payable=comp.payable,
            refundable=comp.refundable,
            computation=json.loads(result.computation.json()),
            citations=citations,
        )
        db.add(record)
        db.add(AuditLog(event_type="GENERATE_RETURN", details={"tin": data.tin}, user_tin=data.tin))
        db.commit()
        db.refresh(record)
        return result

    def chat(self, messages: List[Dict[str, str]], temperature: float | None = None) -> str:
        _init_openai()
        if not _openai_initialized or not _openai_client:
            return "OpenAI key missing; cannot generate answer."
        # separate system + user messages
        temp = temperature or settings.LAW_TEMPERATURE
        # Compose prompt
        formatted = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        resp = _openai_client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=formatted,
            temperature=temp,
            max_tokens=settings.MAX_RESPONSE_TOKENS,
        )
        return resp.choices[0].message.content
