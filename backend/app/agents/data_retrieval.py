import os
import pandas as pd
from typing import Dict, Any

class DataRetrievalAgent:
    """
    Veri Ajanı (Data Retrieval Subagent)
    Görev: TimescaleDB ve Supabase'den (veya mock CSV'den) geçmiş emlak fiyat verilerini 
    ve coğrafi metrikleri (metroya uzaklık vb.) çeker.
    """
    
    def __init__(self):
        # CSV mock veritabanı yolu
        self.csv_path = os.path.join(os.getcwd(), "data", "transactions.csv")
        
    def fetch_historical_prices(self, location: str) -> Dict[str, Any]:
        """Belirli bir bölge için geçmiş fiyat verilerini CSV'den getir."""
        print(f"DataRetrievalAgent: '{location}' için geçmiş veriler çekiliyor...")
        
        try:
            df = pd.read_csv(self.csv_path)
            loc_df = df[df['district'] == location]
            
            if loc_df.empty:
                return {"location": location, "historical_trend": [], "error": "Veri bulunamadı"}
                
            trend = []
            for _, row in loc_df.iterrows():
                trend.append({
                    "year": int(row['year']),
                    "avg_price": float(row['avg_price_aed'])
                })
            
            return {
                "location": location,
                "historical_trend": trend
            }
        except Exception as e:
            return {"location": location, "error": str(e)}
        
    def fetch_geographic_metrics(self, location: str) -> Dict[str, Any]:
        """Metroya uzaklık, okul vb. coğrafi metrikleri CSV'den getir."""
        print(f"DataRetrievalAgent: '{location}' için coğrafi veriler çekiliyor...")
        try:
            df = pd.read_csv(self.csv_path)
            loc_df = df[df['district'] == location]
            
            if loc_df.empty:
                return {"distance_to_metro_km": None, "nearby_schools": None}
                
            # İlk satırdaki metrikleri alıyoruz (mock için yeterli)
            row = loc_df.iloc[0]
            return {
                "distance_to_metro_km": float(row['distance_to_metro_km']),
                "nearby_schools": int(row['nearby_schools'])
            }
        except Exception:
            return {"distance_to_metro_km": 1.5, "nearby_schools": 3}

data_retrieval_agent = DataRetrievalAgent()
