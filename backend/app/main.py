from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import joblib
from app.agents.orchestrator import run_orchestrator_stream

app = FastAPI(title="TerraSight AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    budget: float | None = None
    preferences: list[str] | None = None

@app.get("/")
def read_root():
    return {"message": "Welcome to TerraSight AI API"}

@app.get("/health")
def check_health():
    """Health check validating if the CatBoost model is loaded."""
    model_path = os.path.join("app", "models", "artifacts", "catboost_appreciation_model.cbm")
    is_model_loaded = os.path.exists(model_path)
        
    if is_model_loaded:
        return {"status": "ok", "model_loaded": True}
    else:
        return {"status": "warning", "model_loaded": False, "message": "CatBoost Model not found."}

@app.post("/agent-query")
async def process_agent_query(request: QueryRequest):
    """
    Kullanıcı isteğini Orchestrator'a iletir ve her alt ajanın tamamlanma
    durumunu SSE (Server-Sent Events) ile stream eder.
    """
    try:
        # run_orchestrator_stream artık bir async generator dönüyor
        return StreamingResponse(
            run_orchestrator_stream(request.query, request.budget, request.preferences),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
