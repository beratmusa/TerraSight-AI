import os
import pandas as pd
from catboost import CatBoostRegressor

def train_and_save_mock_model():
    csv_path = os.path.join("data", "transactions.csv")
    df = pd.read_csv(csv_path)

    # Features (X) and Target (y)
    # Exclude non-numeric or target variables
    X = df.drop(columns=['district', '12_month_appreciation_pct'])
    y = df['12_month_appreciation_pct']

    # Initialize CatBoostRegressor
    model = CatBoostRegressor(
        iterations=100,
        learning_rate=0.1,
        depth=6,
        verbose=False
    )
    
    # Train model
    model.fit(X, y)

    # Save model
    artifacts_dir = os.path.join("app", "models", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Using CatBoost's native save format (often better for deployment)
    model_path = os.path.join(artifacts_dir, "catboost_appreciation_model.cbm")
    model.save_model(model_path)
    print(f"CatBoost model successfully trained and saved to {model_path}")

if __name__ == "__main__":
    train_and_save_mock_model()
