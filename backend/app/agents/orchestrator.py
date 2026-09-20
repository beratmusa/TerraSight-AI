import asyncio
import json
from typing import Dict, Any, List, TypedDict

from app.agents.data_retrieval import data_retrieval_agent
from app.agents.ml_prediction import ml_prediction_agent
from app.agents.rag_context import rag_context_agent

# LangGraph için kullanılacak State Şeması
class AgentState(TypedDict):
    query: str
    budget: float | None
    preferences: List[str] | None
    retrieved_data: Dict[str, Any]
    ml_prediction: Dict[str, Any]
    rag_context: Dict[str, Any]
    final_response: str | None

async def run_orchestrator_stream(query: str, budget: float = None, preferences: List[str] = None):
    """
    Kullanıcı isteğini alt ajanlara dağıtır.
    İşlem sürdükçe SSE (Server-Sent Events) için yield ile durum güncellemeleri gönderir.
    """
    
    # State'i ilklendir
    state: AgentState = {
        "query": query,
        "budget": budget,
        "preferences": preferences,
        "retrieved_data": {},
        "ml_prediction": {},
        "rag_context": {},
        "final_response": None
    }
    
    # 1. Başlangıç Bildirimi
    yield f"data: {json.dumps({'status': 'Analyzing query...', 'step': 'init'})}\n\n"
    await asyncio.sleep(1) # Simülasyon için bekleme
    
    # 2. RAG Bağlamı (Context)
    yield f"data: {json.dumps({'status': 'RAG Agent searching regulations...', 'step': 'rag'})}\n\n"
    state["rag_context"] = rag_context_agent.retrieve_context(state["query"])
    await asyncio.sleep(1)
    
    # NLP ile lokasyonların çıkarıldığını varsayıyoruz
    locations_to_analyze = ["JVC", "Arjan"]
    prediction_results = []
    
    # 3. Data Retrieval & ML Prediction
    for loc in locations_to_analyze:
        yield f"data: {json.dumps({'status': f'Data Retrieval Agent fetching GIS and Financial metrics for {loc}...', 'step': 'data'})}\n\n"
        data_res = data_retrieval_agent.fetch_all_features(loc)
        features = data_res.get("features", {})
        
        state["retrieved_data"][loc] = features
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'status': f'ML Agent running CatBoost to predict 12-month ROI for {loc}...', 'step': 'ml'})}\n\n"
        ml_prediction = ml_prediction_agent.predict_appreciation(
            location=loc, 
            features=features
        )
        
        state["ml_prediction"][loc] = ml_prediction
        prediction_results.append({
            "location": loc,
            "features": features,
            "predictions": ml_prediction.get("predictions", {})
        })
        await asyncio.sleep(0.5)
    
    # 4. Sentez (LLM)
    yield f"data: {json.dumps({'status': 'Orchestrator Agent synthesizing final response...', 'step': 'synthesis'})}\n\n"
    await asyncio.sleep(1)
    
    final_synthesis = (
        f"Data synthesis complete. Based on CatBoost ML Modeling:\n"
        f"- {state['rag_context']['context_summary']}\n"
        f"- Expected 12-month appreciation for JVC: +{prediction_results[0]['predictions'].get('12_month_appreciation_pct', 0)}%\n"
        f"- Expected 12-month appreciation for Arjan: +{prediction_results[1]['predictions'].get('12_month_appreciation_pct', 0)}%\n"
        "These predictions consider GIS proximity to the beach, development stage, ROI, and supply pressure."
    )
    
    state["final_response"] = final_synthesis
    
    # 5. Tamamlandı
    final_payload = {
        "status": "Done",
        "step": "done",
        "result": {
            "answer": state["final_response"],
            "prediction_data": prediction_results,
            "context_data": state["rag_context"]
        }
    }
    yield f"data: {json.dumps(final_payload)}\n\n"
