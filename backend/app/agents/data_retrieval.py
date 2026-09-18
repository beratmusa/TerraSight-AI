from typing import Dict, Any

class DataRetrievalAgent:
    """
    Veri Ajanı (Data Retrieval Subagent)
    Görev: TimescaleDB ve Supabase'den geçmiş emlak fiyat verilerini 
    ve coğrafi metrikleri (metroya uzaklık vb.) çeker.
    """
    
    def __init__(self):
        # Supabase client veya veritabanı bağlantısı burada başlatılabilir
        pass
        
    def fetch_historical_prices(self, location: str) -> Dict[str, Any]:
        """Belirli bir bölge için geçmiş fiyat verilerini TimescaleDB/Supabase'den getir."""
        # TODO: Gerçek veritabanı sorguları buraya gelecek
        print(f"DataRetrievalAgent: '{location}' için geçmiş veriler çekiliyor...")
        
        # Mock Veri
        return {
            "location": location,
            "historical_trend": [
                {"year": 2021, "avg_price": 400000},
                {"year": 2022, "avg_price": 420000},
                {"year": 2023, "avg_price": 460000},
            ]
        }
        
    def fetch_geographic_metrics(self, location: str) -> Dict[str, Any]:
        """Metroya uzaklık, okul vb. coğrafi metrikleri getir."""
        print(f"DataRetrievalAgent: '{location}' için coğrafi veriler çekiliyor...")
        # Mock Veri
        return {
            "distance_to_metro_km": 1.5,
            "nearby_schools": 3
        }

# Agent'ı dışa aktarma (LangGraph veya framework node'u olarak sarmalanabilir)
data_retrieval_agent = DataRetrievalAgent()
