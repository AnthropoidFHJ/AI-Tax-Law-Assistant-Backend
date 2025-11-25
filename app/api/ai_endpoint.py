from fastapi import APIRouter, UploadFile, HTTPException
from app.services.ai_service import AIService
from app.schemas.schema import DocumentResponse, ChatRequest, ChatResponse

router = APIRouter()
service = AIService()

@router.post("/upload", response_model=DocumentResponse)
async def upload(file: UploadFile):
    """Parse salary sheet (CSV, Excel, PDF) and return data for dashboard."""
    if not file:
        raise HTTPException(400, "No file uploaded")
    return service.parse_document(file)

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with AI tax assistant."""
    return ChatResponse(answer=service.chat([m.dict() for m in req.messages], req.temperature))
