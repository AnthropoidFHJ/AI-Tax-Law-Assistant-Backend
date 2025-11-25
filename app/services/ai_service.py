from typing import List, Dict, Any
from fastapi import UploadFile
from openai import OpenAI
from app.utils.preprocess import parse_pdf, parse_spreadsheet
from app.config.config import settings, SYSTEM_PROMPT

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def parse_document(self, file: UploadFile) -> Dict[str, Any]:
        content = file.file.read()
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            data = parse_pdf(content)
            file_type = "pdf"
        elif filename.endswith(".csv"):
            data = parse_spreadsheet(content, "csv")
            file_type = "csv"
        elif filename.endswith((".xlsx", ".xls")):
            data = parse_spreadsheet(content, "excel")
            file_type = "excel"
        else:
            data = {"raw_text": content.decode(errors="ignore")}
            file_type = "text"

        return {
            "filename": file.filename,
            "file_type": file_type,
            "data": data,
            "status": "success"
        }

    def chat(self, messages: List[Dict[str, str]], temperature: float = None) -> str:
        if not self.client:
            return "Error: OpenAI API key not configured."

        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=temperature or settings.LAW_TEMPERATURE,
            max_tokens=settings.MAX_RESPONSE_TOKENS,
        )
        return response.choices[0].message.content