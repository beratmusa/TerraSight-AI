import os
import pandas as pd
from typing import Dict, Any

from app.db.supabase_client import get_supabase_client

class DataRetrievalAgent:
    """
    Data Retrieval Subagent
    Fetches complex GIS and Financial metrics for CatBoost modeling from Supabase.
    """
    def __init__(self):
        self.supabase = get_supabase_client()
        
    def fetch_all_features(self, location: str, user_specs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetches all features from Supabase for a specific location and merges user specs."""
        print(f"DataRetrievalAgent: Fetching GIS and financial data for '{location}' from Supabase...")
        if user_specs is None:
            user_specs = {}
            
        try:
            if not self.supabase:
                raise Exception("Supabase client not configured.")
                
            # Fetch all transactions to do fuzzy matching in python, 
            # or in a real scenario, use Supabase text search / ilike
            # For MVP, fetching all and filtering in pandas is fine since data is small,
            # but let's query directly with ilike!
            search_loc = f"%{location}%"
            response = self.supabase.table("transactions").select("*").ilike("district", search_loc).execute()
            
            data = response.data
            if not data:
                print(f"DataRetrievalAgent: WARNING - No data found for '{location}'.")
                return {"location": location, "error": "No data found"}
                
            df = pd.DataFrame(data)
            
            # Drop unnecessary columns before taking the mean
            cols_to_drop = ['id', 'district', '12_month_appreciation_pct', 'transaction_date']
            df_numeric = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
            
            avg_all = df_numeric.mean().to_dict()
            lat = avg_all.pop("lat", 25.06)
            lng = avg_all.pop("lng", 55.20)
            
            # OVERWRITE average features with user-specific specs if provided
            for key, val in user_specs.items():
                if val is not None and key in avg_all:
                    avg_all[key] = val
            
            # Mock Buy/Sell volumes based on available metrics
            weekly_buy_volume = int(avg_all.get('momentum_3m', 1) * 120 + 50)
            weekly_sell_volume = int(avg_all.get('days_on_market', 30) * 8)
            
            return {
                "location": location,
                "lat": lat,
                "lng": lng,
                "weekly_buy_volume": weekly_buy_volume,
                "weekly_sell_volume": weekly_sell_volume,
                "features": avg_all
            }
        except Exception as e:
            return {"location": location, "error": str(e)}

data_retrieval_agent = DataRetrievalAgent()
