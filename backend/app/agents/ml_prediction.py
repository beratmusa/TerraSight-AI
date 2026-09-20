import os
import pandas as pd
from typing import Dict, Any
from catboost import CatBoostRegressor

class MLPredictionAgent:
    """
    ML Prediction Subagent
    Uses trained CatBoost model to predict 12-month appreciation percentage.
    """
    def __init__(self):
        self.model = CatBoostRegressor()
        model_path = os.path.join(os.getcwd(), "app", "models", "artifacts", "catboost_appreciation_model.cbm")
        try:
            self.model.load_model(model_path)
            self.model_loaded = True
        except Exception as e:
            print(f"Failed to load CatBoost model: {e}")
            self.model_loaded = False
        
    def predict_appreciation(self, location: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts 12-month appreciation based on extracted features."""
        print(f"MLPredictionAgent: Running CatBoost prediction for '{location}'...")
        
        if not self.model_loaded:
            return {
                "location": location,
                "predictions": {"12_month_appreciation_pct": 0.0},
                "error": "Model not loaded"
            }
            
        try:
            # Convert dictionary back to DataFrame for inference
            df = pd.DataFrame([features])
            prediction = self.model.predict(df)[0]
            
            return {
                "location": location,
                "predictions": {
                    "12_month_appreciation_pct": round(prediction, 2)
                },
                "confidence_score": 0.88 # Example static score
            }
        except Exception as e:
            return {
                "location": location,
                "error": str(e)
            }

ml_prediction_agent = MLPredictionAgent()
