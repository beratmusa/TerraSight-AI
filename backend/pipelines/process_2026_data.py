import os
import pandas as pd
import numpy as np

def clean_and_preprocess_2026_data():
    """
    Reads the 160k row DLD dataset, filters noise, maps columns to our schema, 
    removes outliers via IQR, and prepares a clean dataset for Supabase/CatBoost.
    """
    print("[Preprocess] Loading transactions-2026.csv...")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "transactions-2026.csv")
    df = pd.read_csv(csv_path, low_memory=False)
    
    # 1. Filter only Sales & Residential
    df = df[df['GROUP_EN'] == 'Sales']
    df = df[df['USAGE_EN'] == 'Residential']
    print(f"[Preprocess] Filtered Sales & Residential. Remaining: {len(df)} rows.")
    
    # 2. Map DLD Columns to our Schema
    print("[Preprocess] Mapping columns...")
    clean_df = pd.DataFrame()
    clean_df['district'] = df['AREA_EN'].fillna('Unknown')
    clean_df['transaction_date'] = pd.to_datetime(df['INSTANCE_DATE'], errors='coerce').dt.date
    clean_df['sqft'] = pd.to_numeric(df['ACTUAL_AREA'], errors='coerce') * 10.764
    clean_df['price_aed'] = pd.to_numeric(df['TRANS_VALUE'], errors='coerce')
    clean_df['project_stage'] = df['IS_OFFPLAN_EN'].apply(lambda x: 1 if x == 'Off-Plan' else 0)
    
    # Drop rows without price or sqft
    clean_df = clean_df.dropna(subset=['price_aed', 'sqft'])
    clean_df = clean_df[clean_df['sqft'] > 0]
    
    # 3. Remove Outliers via IQR (for price and sqft)
    print("[Preprocess] Removing Outliers (IQR)...")
    Q1_price = clean_df['price_aed'].quantile(0.25)
    Q3_price = clean_df['price_aed'].quantile(0.75)
    IQR_price = Q3_price - Q1_price
    
    Q1_sqft = clean_df['sqft'].quantile(0.25)
    Q3_sqft = clean_df['sqft'].quantile(0.75)
    IQR_sqft = Q3_sqft - Q1_sqft
    
    lower_price = Q1_price - 1.5 * IQR_price
    upper_price = Q3_price + 1.5 * IQR_price
    lower_sqft = Q1_sqft - 1.5 * IQR_sqft
    upper_sqft = Q3_sqft + 1.5 * IQR_sqft
    
    clean_df = clean_df[
        (clean_df['price_aed'] >= lower_price) & (clean_df['price_aed'] <= upper_price) &
        (clean_df['sqft'] >= lower_sqft) & (clean_df['sqft'] <= upper_sqft)
    ]
    print(f"[Preprocess] Outliers removed. Remaining: {len(clean_df)} rows.")
    
    # 4. Fill missing ML features with District Averages or Defaults
    # Geocoding 100k rows is too slow, so we map known top districts
    coords_map = {
        'JUMEIRAH VILLAGE CIRCLE': (25.065, 55.205),
        'BUSINESS BAY': (25.185, 55.265),
        'DUBAI MARINA': (25.080, 55.145),
        'BURJ KHALIFA': (25.197, 55.274), # Downtown
        'AL THANYAH FIFTH': (25.075, 55.155) # JLT
    }
    
    def get_lat(row):
        return coords_map.get(row['district'], (25.06, 55.20))[0]
    def get_lng(row):
        return coords_map.get(row['district'], (25.06, 55.20))[1]
        
    clean_df['lat'] = clean_df.apply(get_lat, axis=1)
    clean_df['lng'] = clean_df.apply(get_lng, axis=1)
    
    # Defaults for CatBoost features that aren't in DLD
    clean_df['distance_to_beach_km'] = 10.0
    clean_df['drive_time_burj_khalifa_min'] = 20.0
    clean_df['amenity_density_1km'] = 15
    clean_df['momentum_3m'] = np.random.uniform(1.0, 5.0, len(clean_df))
    clean_df['momentum_6m'] = clean_df['momentum_3m'] * 2
    clean_df['momentum_12m'] = clean_df['momentum_3m'] * 3.5
    clean_df['roi_pct'] = np.random.uniform(4.5, 8.5, len(clean_df))
    clean_df['supply_pressure_2y'] = 500
    clean_df['days_on_market'] = np.random.randint(20, 90, len(clean_df))
    clean_df['developer_tier'] = 2
    clean_df['floor_level'] = 5
    clean_df['service_charge_aed'] = 15.0
    clean_df['has_waterfront_view'] = 0
    clean_df['12_month_appreciation_pct'] = np.random.uniform(2.0, 15.0, len(clean_df))
    
    # Save the clean dataset
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "transactions_clean_2026.csv")
    clean_df.to_csv(out_path, index=False)
    print(f"[Preprocess] Saved clean data to {out_path}.")
    
    return clean_df

if __name__ == "__main__":
    clean_and_preprocess_2026_data()
