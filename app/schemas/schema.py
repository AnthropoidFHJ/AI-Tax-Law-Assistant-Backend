from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DocumentResponse(BaseModel):
    filename: str
    file_type: str
    data: Dict[str, Any]
    status: str

class ChatMessage(BaseModel):
    role: str   
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str