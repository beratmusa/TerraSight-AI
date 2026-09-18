from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents.orchestrator import run_orchestrator

app = FastAPI(title="TerraSight AI Backend", version="0.1.0")

class QueryRequest(BaseModel):
    query: str
    budget: float | None = None
    preferences: list[str] | None = None

class QueryResponse(BaseModel):
    answer: str
    prediction_data: dict | None = None
    context_data: dict | None = None

@app.get("/")
def read_root():
    return {"message": "Welcome to TerraSight AI API"}

@app.post("/agent-query", response_model=QueryResponse)
async def process_agent_query(request: QueryRequest):
    """
    Kullanıcıdan gelen isteği (Örn: "500k AED bütçem var, JVC mi Arjan mı?") 
    Orkestratör Ajan'a (Supervisor) yönlendirir.
    """
    try:
        # Orkestratör Ajanı çalıştırıyoruz.
        # Bu fonksiyon, LangGraph veya CrewAI ile alt ajanları (Subagents) koordine eder.
        result = await run_orchestrator(request.query, request.budget, request.preferences)
        
        return QueryResponse(
            answer=result.get("answer", "No answer found"),
            prediction_data=result.get("prediction_data"),
            context_data=result.get("context_data")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
