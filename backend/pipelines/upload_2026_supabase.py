import os
import pandas as pd
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.db.supabase_client import get_supabase_client

def upload_in_batches(df, table_name="transactions", batch_size=1000):
    """
    Uploads a pandas DataFrame to Supabase in chunks to avoid payload size limits.
    """
    supabase = get_supabase_client()
    if not supabase:
        print("Supabase client not configured.")
        return
        
    records = df.drop(columns=['transaction_date'], errors='ignore').to_dict(orient="records")
    total_records = len(records)
    print(f"[Upload] Starting upload of {total_records} rows to '{table_name}' in batches of {batch_size}...")
    
    for i in range(0, total_records, batch_size):
        batch = records[i:i + batch_size]
        try:
            supabase.table(table_name).insert(batch).execute()
            print(f"[Upload] Pushed batch {i} to {i + len(batch)} ({len(batch)} rows).")
            time.sleep(0.5) # Rate limit safety
        except Exception as e:
            print(f"[Upload] Error on batch {i}: {e}")

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "transactions_clean_2026.csv")
    df = pd.read_csv(csv_path)
    
    # We will upload only 5,000 rows for the MVP to avoid wasting time/bandwidth on the free tier
    # In a real pipeline you might upload all 105k
    df_sample = df.sample(n=5000, random_state=42) 
    
    upload_in_batches(df_sample, batch_size=1000)
    print("[Upload] Process complete!")
