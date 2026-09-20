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
        
    def fetch_all_features(self, location: str) -> Dict[str, Any]:
        """Fetches all features from CSV for a specific location."""
        print(f"DataRetrievalAgent: Fetching GIS and financial data for '{location}'...")
        
        try:
            df = pd.read_csv(self.csv_path)
            loc_df = df[df['district'] == location]
            
            if loc_df.empty:
                return {"location": location, "error": "No data found"}
                
            # For simplicity, taking the mean of all transactions in that district 
            # to feed into the model as the 'average' property representation
            avg_features = loc_df.drop(columns=['district', '12_month_appreciation_pct']).mean().to_dict()
            
            return {
                "location": location,
                "features": avg_features
            }
        except Exception as e:
            return {"location": location, "error": str(e)}

data_retrieval_agent = DataRetrievalAgent()
