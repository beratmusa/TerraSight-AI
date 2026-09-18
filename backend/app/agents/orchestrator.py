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
        yield f"data: {json.dumps({'status': f'Data Retrieval Agent fetching transactions for {loc}...', 'step': 'data'})}\n\n"
        historical_data = data_retrieval_agent.fetch_historical_prices(loc)
        geo_data = data_retrieval_agent.fetch_geographic_metrics(loc)
        
        state["retrieved_data"][loc] = {
            "historical": historical_data,
            "geo": geo_data
        }
        await asyncio.sleep(0.5)
        
        yield f"data: {json.dumps({'status': f'ML Agent predicting 5-year ROI for {loc}...', 'step': 'ml'})}\n\n"
        ml_prediction = ml_prediction_agent.predict_appreciation(
            location=loc, 
            historical_data=historical_data
        )
        
        state["ml_prediction"][loc] = ml_prediction
        prediction_results.append({
            "location": loc,
            "current_metrics": historical_data,
            "geo_data": geo_data,
            "predictions": ml_prediction["predictions"]
        })
        await asyncio.sleep(0.5)
    
    # 4. Sentez (LLM)
    yield f"data: {json.dumps({'status': 'Orchestrator Agent synthesizing final response...', 'step': 'synthesis'})}\n\n"
    await asyncio.sleep(1)
    
    final_synthesis = (
        f"Veriler sentezlendi. Bütçeniz ({budget} AED) dahilinde yapılan analize göre:\n"
        f"- {state['rag_context']['context_summary']}\n"
        f"- JVC için beklenen 5 yıllık artış: %{prediction_results[0]['predictions']['5_year_appreciation_pct']}\n"
        f"- Arjan için beklenen 5 yıllık artış: %{prediction_results[1]['predictions']['5_year_appreciation_pct']}\n"
        "Uzun vadeli yatırım için JVC, kısa vadeli teşvikler için Arjan tercih edilebilir."
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
