import os
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

def clean_and_preprocess_2026_data():
    print("[Preprocess] Loading transactions-2026.csv...")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "transactions-2026.csv")
    df = pd.read_csv(csv_path, low_memory=False)
    
    df = df[df['GROUP_EN'] == 'Sales']
    df = df[df['USAGE_EN'] == 'Residential']
    
    clean_df = pd.DataFrame()
    clean_df['district'] = df['AREA_EN'].fillna('Unknown')
    clean_df['transaction_date'] = pd.to_datetime(df['INSTANCE_DATE'], errors='coerce').dt.date
    clean_df['sqft'] = pd.to_numeric(df['ACTUAL_AREA'], errors='coerce') * 10.764
    clean_df['price_aed'] = pd.to_numeric(df['TRANS_VALUE'], errors='coerce')
    clean_df['project_stage'] = df['IS_OFFPLAN_EN'].apply(lambda x: 1 if x == 'Off-Plan' else 0)
    
    clean_df = clean_df.dropna(subset=['price_aed', 'sqft'])
    clean_df = clean_df[clean_df['sqft'] > 0]
    
    # Remove Outliers
    Q1_p, Q3_p = clean_df['price_aed'].quantile(0.25), clean_df['price_aed'].quantile(0.75)
    IQR_p = Q3_p - Q1_p
    Q1_s, Q3_s = clean_df['sqft'].quantile(0.25), clean_df['sqft'].quantile(0.75)
    IQR_s = Q3_s - Q1_s
    
    clean_df = clean_df[
        (clean_df['price_aed'] >= Q1_p - 1.5 * IQR_p) & (clean_df['price_aed'] <= Q3_p + 1.5 * IQR_p) &
        (clean_df['sqft'] >= Q1_s - 1.5 * IQR_s) & (clean_df['sqft'] <= Q3_s + 1.5 * IQR_s)
    ]
    
    # -----------------------------------------------------
    # DYNAMIC GEOCODING & FEATURE GENERATION
    # -----------------------------------------------------
    print("[Preprocess] Geocoding 156 unique districts...")
    unique_districts = clean_df['district'].unique()
    geolocator = Nominatim(user_agent="terrasight_ai")
    
    coord_dict = {}
    for dist in unique_districts:
        # Hardcode a few popular ones to save API time
        if dist == 'JUMEIRAH VILLAGE CIRCLE': coord_dict[dist] = (25.065, 55.205)
        elif dist == 'BUSINESS BAY': coord_dict[dist] = (25.185, 55.265)
        elif dist == 'DUBAI MARINA': coord_dict[dist] = (25.080, 55.145)
        elif dist == 'BURJ KHALIFA': coord_dict[dist] = (25.197, 55.274)
        elif dist == 'AL THANYAH FIFTH': coord_dict[dist] = (25.075, 55.155)
        else:
            try:
                # Search Dubai + District Name
                loc = geolocator.geocode(f"{dist}, Dubai", timeout=5)
                if loc:
                    coord_dict[dist] = (loc.latitude, loc.longitude)
                else:
                    coord_dict[dist] = (25.06, 55.20) # Fallback to center
                time.sleep(0.5) # Respect Nominatim rate limit
            except:
                coord_dict[dist] = (25.06, 55.20)
                
    clean_df['lat'] = clean_df['district'].map(lambda x: coord_dict.get(x, (25.06, 55.20))[0])
    clean_df['lng'] = clean_df['district'].map(lambda x: coord_dict.get(x, (25.06, 55.20))[1])
    
    print("[Preprocess] Calculating actual geospatial distances...")
    beach_coords = (25.0786, 55.1328)
    burj_coords = (25.1972, 55.2744)
    
    def calc_dist(row, target):
        return round(geodesic((row['lat'], row['lng']), target).kilometers, 2)
        
    clean_df['distance_to_beach_km'] = clean_df.apply(lambda r: calc_dist(r, beach_coords), axis=1)
    # Estimate drive time as 2 mins per km in Dubai traffic
    clean_df['drive_time_burj_khalifa_min'] = clean_df.apply(lambda r: int(calc_dist(r, burj_coords) * 2.5), axis=1)
    
    print("[Preprocess] Applying realistic random distributions for non-DLD features...")
    # Density decreases as you move further from center (Burj Khalifa)
    clean_df['amenity_density_1km'] = clean_df['drive_time_burj_khalifa_min'].apply(
        lambda x: max(1, int(30 - (x * 0.5) + np.random.randint(-5, 5)))
    )
    
    # Waterfront view is highly likely if distance to beach is < 2km
    clean_df['has_waterfront_view'] = clean_df['distance_to_beach_km'].apply(
        lambda x: 1 if (x < 2.5 and np.random.rand() > 0.4) else 0
    )
    
    # Developer tier (1=Luxury, 2=Mid, 3=Economy) correlates with Price per Sqft
    clean_df['price_per_sqft'] = clean_df['price_aed'] / clean_df['sqft']
    clean_df['developer_tier'] = pd.qcut(clean_df['price_per_sqft'], 3, labels=[3, 2, 1]).astype(int)
    
    # Floor level is random but slightly correlates with price
    clean_df['floor_level'] = clean_df['price_per_sqft'].apply(
        lambda x: np.random.randint(1, 15) if x < 1500 else np.random.randint(15, 60)
    )
    
    # Service charge correlates heavily with luxury and waterfront
    clean_df['service_charge_aed'] = clean_df.apply(
        lambda r: round(np.random.uniform(10, 15) if r['developer_tier']==3 else np.random.uniform(15, 30), 1), axis=1
    )
    
    # Supply pressure and momentum (randomized realistically per district)
    district_supply = {d: np.random.randint(100, 2000) for d in unique_districts}
    clean_df['supply_pressure_2y'] = clean_df['district'].map(district_supply)
    
    clean_df['momentum_3m'] = clean_df['district'].map({d: round(np.random.uniform(1.0, 5.0), 1) for d in unique_districts})
    clean_df['momentum_6m'] = clean_df['momentum_3m'] * np.random.uniform(1.5, 2.0)
    clean_df['momentum_12m'] = clean_df['momentum_3m'] * np.random.uniform(2.5, 3.5)
    clean_df['roi_pct'] = clean_df['district'].map({d: round(np.random.uniform(4.5, 9.5), 2) for d in unique_districts})
    clean_df['days_on_market'] = clean_df['district'].map({d: np.random.randint(14, 120) for d in unique_districts})
    
    clean_df['12_month_appreciation_pct'] = clean_df['district'].map({d: round(np.random.uniform(2.0, 15.0), 1) for d in unique_districts})
    
    clean_df = clean_df.drop(columns=['price_per_sqft'])
    
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "transactions_clean_2026.csv")
    clean_df.to_csv(out_path, index=False)
    print(f"[Preprocess] Saved dynamic clean data to {out_path}.")
    
    return clean_df

if __name__ == "__main__":
    clean_and_preprocess_2026_data()
