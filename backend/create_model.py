import os
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

# Basit bir mock model oluşturuyoruz
def train_and_save_mock_model():
    # Sahte veriler: X (yıl, metro uzaklık), y (fiyat)
    X = pd.DataFrame({
        'year': [2021, 2022, 2023, 2021, 2022],
        'distance_to_metro': [1.5, 1.5, 1.5, 0.5, 0.5]
    })
    y = [400000, 420000, 450000, 800000, 850000]

    model = LinearRegression()
    model.fit(X, y)

    # Modeli kaydet
    artifacts_dir = os.path.join("app", "models", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    model_path = os.path.join(artifacts_dir, "price_prediction_model.joblib")
    
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_mock_model()
