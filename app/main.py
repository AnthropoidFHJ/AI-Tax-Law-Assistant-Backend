from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ai_endpoint import router as ai_router

app = FastAPI(title="AI Tax & Law Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AI Tax Law Agent is Running..."}
