from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.ai_service import AIService
from app.models.model import get_db, TaxReturn
from app.schemas.schema import UploadResult, ChatRequest, ChatResponse, TaxInput, TaxReturnResult, ReturnsList, ReturnRecord
from typing import List

router = APIRouter()
service = AIService()

@router.post("/upload", response_model=UploadResult)
async def upload_document(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    result = service.ingest_document(file)
    return UploadResult(**result)

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer = service.chat([m.dict() for m in req.messages], temperature=req.temperature)
    # Simple citation extraction placeholder
    citations = []
    for token in ["Section", "Rule", "SRO"]:
        if token in answer:
            citations.append(token)
    return ChatResponse(answer=answer, citations=citations)

@router.post("/generate-return", response_model=TaxReturnResult)
async def generate_return(data: TaxInput, db: Session = Depends(get_db)):
    result = service.generate_return(db, data)
    return result

@router.get("/returns", response_model=ReturnsList)
async def list_returns(db: Session = Depends(get_db)):
    rows = db.query(TaxReturn).order_by(TaxReturn.id.desc()).limit(100).all()
    items: List[ReturnRecord] = [
        ReturnRecord(id=r.id, tin=r.tin, assessment_year=r.assessment_year, payable=r.payable)
        for r in rows
    ]
    return ReturnsList(returns=items)

@router.get("/returns/{return_id}", response_model=TaxReturnResult)
async def get_return(return_id: int, db: Session = Depends(get_db)):
    r = db.query(TaxReturn).filter(TaxReturn.id == return_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Return not found")
    comp = r.computation
    result = TaxReturnResult(
        tin=r.tin,
        assessment_year=r.assessment_year,
        computation=comp,  # Pydantic will validate dict -> TaxComputation
        compliance_flags=[],
        citations=r.citations,
        disclaimer="AI-generated; not a substitute for certified tax lawyer. User responsible for final submission.",
    )
    return result
