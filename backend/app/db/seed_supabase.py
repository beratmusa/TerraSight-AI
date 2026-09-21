import os
import pandas as pd
from supabase_client import get_supabase_client

def seed_transactions():
    supabase = get_supabase_client()
    if not supabase:
        print("Supabase client not initialized.")
        return
        
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "transactions.csv")
    if not os.path.exists(csv_path):
        print(f"CSV not found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # Insert rows one by one or in batch
    records = df.to_dict(orient="records")
    
    try:
        # Clear existing data to prevent duplicates (optional)
        # supabase.table("transactions").delete().neq("id", 0).execute()
        
        response = supabase.table("transactions").insert(records).execute()
        print(f"Successfully seeded {len(response.data)} transactions to Supabase!")
    except Exception as e:
        print(f"Error seeding Supabase: {e}")

if __name__ == "__main__":
    seed_transactions()
