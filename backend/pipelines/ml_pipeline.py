import os
import shutil
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

def fetch_dubai_pulse_data():
    """
    Simulates fetching new daily transaction data from Dubai Pulse (DLD API)
    and calculating GIS metrics via OpenStreetMap (osmnx/Overpass).
    """
    print("[Pipeline] Fetching new transaction data from Dubai Pulse...")
    print("[Pipeline] Calculating OSM distances (beach, metro, amenities)...")
    
    # Mocking newly arrived data for this month
    new_data = pd.DataFrame({
        'distance_to_beach_km': [12.0, 1.2, 14.5, 10.0, 5.0],
        'drive_time_burj_khalifa_min': [24, 21, 26, 15, 10],
        'amenity_density_1km': [9, 21, 6, 12, 18],
        'momentum_3m': [1.3, 0.6, 2.2, 1.0, 0.9],
        'momentum_6m': [3.6, 1.6, 5.8, 2.5, 2.0],
        'momentum_12m': [8.1, 4.1, 12.2, 6.0, 5.0],
        'roi_pct': [6.6, 5.9, 7.2, 6.0, 5.5],
        'supply_pressure_2y': [1400, 320, 1950, 800, 500],
        'days_on_market': [43, 26, 48, 35, 30],
        'developer_tier': [2, 1, 3, 1, 1],
        'project_stage': [0, 1, 0, 0, 0],
        'sqft': [860, 1150, 780, 1200, 900],
        'floor_level': [6, 42, 4, 15, 10],
        'service_charge_aed': [13, 23, 11, 16, 15],
        'has_waterfront_view': [0, 1, 0, 0, 1],
        '12_month_appreciation_pct': [12.8, 4.5, 15.6, 8.0, 6.5] # Target
    })
    return new_data

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw data to prevent noise from poisoning the ML model.
    """
    print("[Pipeline] Preprocessing data (Noise reduction & Imputation)...")
    df_clean = df.copy()
    
    # 1. Missing Value Imputation
    # If service charge is missing, fill with median of the dataset (or ideally median of the district)
    if 'service_charge_aed' in df_clean.columns:
        df_clean['service_charge_aed'] = df_clean['service_charge_aed'].fillna(df_clean['service_charge_aed'].median())
        
    # Fill missing binary features with 0
    if 'has_waterfront_view' in df_clean.columns:
        df_clean['has_waterfront_view'] = df_clean['has_waterfront_view'].fillna(0)
        
    # 2. Outlier Removal using IQR (Interquartile Range)
    # Extremely high sqft or prices in real estate are often data entry errors or ultra-luxury outliers
    # that skew the model for standard properties.
    if 'sqft' in df_clean.columns:
        Q1 = df_clean['sqft'].quantile(0.25)
        Q3 = df_clean['sqft'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        # Filter out extreme outliers
        df_clean = df_clean[(df_clean['sqft'] >= lower_bound) & (df_clean['sqft'] <= upper_bound)]
        
    # 3. Target Variable Sanity Check
    # Remove any rows where appreciation is logically impossible (e.g., +300% in a year due to typos)
    if '12_month_appreciation_pct' in df_clean.columns:
        df_clean = df_clean[(df_clean['12_month_appreciation_pct'] > -50) & (df_clean['12_month_appreciation_pct'] < 100)]
        
    print(f"[Pipeline] Preprocessing complete. Rows retained: {len(df_clean)} / {len(df)}")
    return df_clean

def run_ml_training_pipeline():
    """
    MLOps Pipeline: Model Evaluation, Backup & Conditional Deploy
    """
    print("=== Starting MLOps Pipeline ===")
    
    # 1. Get new data and split for validation
    raw_data = fetch_dubai_pulse_data()
    
    # Apply Preprocessing (Noise Reduction)
    clean_data = preprocess_data(raw_data)
    
    X = clean_data.drop(columns=['12_month_appreciation_pct'])
    y = clean_data['12_month_appreciation_pct']
    
    # We keep a validation set to test the new model vs old model
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    artifacts_dir = os.path.join(os.getcwd(), "app", "models", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    model_path = os.path.join(artifacts_dir, "catboost_appreciation_model.cbm")
    backup_path = os.path.join(artifacts_dir, "catboost_appreciation_model.cbm.bak")
    
    old_model = CatBoostRegressor()
    new_model = CatBoostRegressor(iterations=50, learning_rate=0.05, depth=6, verbose=False)
    
    old_rmse = float('inf')
    
    if os.path.exists(model_path):
        print(f"[Pipeline] Existing model found. Evaluating current performance...")
        old_model.load_model(model_path)
        
        # Evaluate OLD model on the new validation data
        old_preds = old_model.predict(X_val)
        old_rmse = np.sqrt(mean_squared_error(y_val, old_preds))
        print(f"[Pipeline] Old Model RMSE: {old_rmse:.4f}")
        
        # 2. Train NEW model using Warm Start
        print("[Pipeline] Training NEW model (Warm Start)...")
        new_model.fit(X_train, y_train, init_model=model_path, eval_set=(X_val, y_val))
    else:
        print("[Pipeline] No existing model found. Training from scratch...")
        new_model.fit(X_train, y_train, eval_set=(X_val, y_val))
        
    # 3. Evaluate NEW model
    new_preds = new_model.predict(X_val)
    new_rmse = np.sqrt(mean_squared_error(y_val, new_preds))
    print(f"[Pipeline] New Model RMSE: {new_rmse:.4f}")
    
    # 4. Conditional Deploy (Champion vs Challenger)
    if new_rmse < old_rmse or not os.path.exists(model_path):
        print("[Pipeline] SUCCESS: New model outperformed old model (or is first model). Deploying...")
        
        # Create Backup of the old model just in case
        if os.path.exists(model_path):
            shutil.copy2(model_path, backup_path)
            print(f"[Pipeline] Backup created at {backup_path}")
            
        new_model.save_model(model_path)
        print(f"[Pipeline] Champion model saved to {model_path}")
    else:
        print("[Pipeline] WARNING: New model performed worse. Rejecting update. Old model kept.")
        
    print("=== MLOps Pipeline Complete ===")

if __name__ == "__main__":
    run_ml_training_pipeline()
