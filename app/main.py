from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.config import settings
from app.api.health_check import router as health_router
from app.api.ai_endpoint import router as ai_router

app = FastAPI(title="AI Tax Law Agent BD", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(ai_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AI Tax Law Agent BD Backend Running"}

# Run with: uvicorn app.main:app --reload
