from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UploadResult(BaseModel):
    filename: str
    extracted_text_preview: str
    chunks: int
    status: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[str] = []

class TaxInput(BaseModel):
    tin: str
    assessment_year: str
    income_items: Dict[str, float]  # e.g., {"salary": 1200000, "business": 200000}
    deductions: Dict[str, float] = {}
    investments: Dict[str, float] = {}  # eligible rebate categories

class TaxComputation(BaseModel):
    gross_income: float
    total_deductions: float
    taxable_income: float
    slab_tax: float
    surcharge: float
    rebate: float
    payable: float
    refundable: float
    breakdown: Dict[str, Any]

class TaxReturnResult(BaseModel):
    tin: str
    assessment_year: str
    computation: TaxComputation
    compliance_flags: List[str]
    citations: List[str]
    disclaimer: str

class ReturnRecord(BaseModel):
    id: int
    tin: str
    assessment_year: str
    payable: float

class ReturnsList(BaseModel):
    returns: List[ReturnRecord]
