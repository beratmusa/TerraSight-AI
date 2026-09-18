import asyncio
from typing import Dict, Any, List

from app.agents.data_retrieval import data_retrieval_agent
from app.agents.ml_prediction import ml_prediction_agent
from app.agents.rag_context import rag_context_agent

async def run_orchestrator(query: str, budget: float = None, preferences: List[str] = None) -> Dict[str, Any]:
    """
    Yönetici Ajan (Orchestrator Agent / Supervisor)
    Görev: Kullanıcı isteğini ("500k AED bütçem var, JVC mi Arjan mı?") alt ajanlara dağıtır, 
    sayısal tahminler ile RAG'dan gelen bağlamsal bilgileri sentezleyerek 
    yapılandırılmış bir JSON döndürür.
    
    Not: Bu örnek, ajanların basit fonksiyon çağrıları şeklinde orkestre edildiği bir yapıdır.
    Gerçek bir MVP'de burası LangGraph (StateGraph) veya CrewAI ile bir workflow'a dönüştürülmelidir.
    """
    
    print(f"OrchestratorAgent: Yeni sorgu alındı -> '{query}'")
    
    # 1. RAG Ajanı ile Genel Bağlamı (Context) Çıkar
    # Kullanıcının sorusundaki JVC veya Arjan gibi yerler için master plan veya regülasyonları analiz et
    rag_result = rag_context_agent.retrieve_context(query)
    
    # NLP ile lokasyonların çıkarıldığını varsayıyoruz (Mock NLP çıkarımı)
    locations_to_analyze = ["JVC", "Arjan"]
    
    prediction_results = []
    
    for loc in locations_to_analyze:
        # 2. Veri Ajanı ile Geçmiş Verileri Çek
        historical_data = data_retrieval_agent.fetch_historical_prices(loc)
        geo_data = data_retrieval_agent.fetch_geographic_metrics(loc)
        
        # 3. ML Tahmin Ajanı ile Gelecek Fiyatları Tahmin Et
        ml_prediction = ml_prediction_agent.predict_appreciation(
            location=loc, 
            historical_data=historical_data
        )
        
        prediction_results.append({
            "location": loc,
            "current_metrics": historical_data,
            "geo_data": geo_data,
            "predictions": ml_prediction["predictions"]
        })
    
    # 4. LLM (Orkestratörün Son Sentezi) 
    # Normalde burada OpenAI / Anthropic API çağrısı yapılarak tüm veriler (RAG + ML + Veri)
    # bir araya getirilip kullanıcıya mantıklı bir yanıt üretilir.
    
    final_synthesis = (
        f"Veriler sentezlendi. Bütçeniz ({budget} AED) dahilinde yapılan analize göre:\n"
        f"- {rag_result['context_summary']}\n"
        f"- JVC için beklenen 5 yıllık artış: %{prediction_results[0]['predictions']['5_year_appreciation_pct']}\n"
        f"- Arjan için beklenen 5 yıllık artış: %{prediction_results[1]['predictions']['5_year_appreciation_pct']}\n"
        "Uzun vadeli yatırım için JVC, kısa vadeli teşvikler için Arjan tercih edilebilir."
    )
    
    # Frontend'in kullanacağı yapılandırılmış JSON formatı
    return {
        "answer": final_synthesis,
        "prediction_data": prediction_results,
        "context_data": rag_result
    }
