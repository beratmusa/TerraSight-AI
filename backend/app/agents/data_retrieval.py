import os
import pandas as pd
from typing import Dict, Any

class DataRetrievalAgent:
    """
    Data Retrieval Subagent
    Fetches complex GIS and Financial metrics for CatBoost modeling.
    """
    def __init__(self):
        self.csv_path = os.path.join(os.getcwd(), "data", "transactions.csv")
        
    def fetch_all_features(self, location: str, user_specs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetches all features from CSV for a specific location and merges user specs."""
        print(f"DataRetrievalAgent: Fetching GIS and financial data for '{location}'...")
        if user_specs is None:
            user_specs = {}
            
        try:
            df = pd.read_csv(self.csv_path)
            
            # Fuzzy match: case insensitive and substring
            # e.g. "Dubai Marina" matches "Marina" in CSV, "Downtown Dubai" matches "Downtown"
            search_loc = location.lower()
            mask = df['district'].str.lower().apply(lambda x: x in search_loc or search_loc in x)
            loc_df = df[mask]
            
            if loc_df.empty:
                print(f"DataRetrievalAgent: WARNING - No data found for '{location}'.")
                return {"location": location, "error": "No data found"}
                
            # For simplicity, taking the mean of all transactions in that district 
            # to feed into the model as the 'average' property representation
            avg_all = loc_df.drop(columns=['district', '12_month_appreciation_pct']).mean().to_dict()
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
