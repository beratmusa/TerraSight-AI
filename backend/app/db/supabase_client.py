import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# We will fill these in once the Supabase project is created
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_supabase_client() -> Client | None:
    """
    Returns a configured Supabase client.
    Requires SUPABASE_URL and SUPABASE_KEY to be set in the environment.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("WARNING: SUPABASE_URL or SUPABASE_KEY is missing in .env file.")
        return None
        
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
        return None

# Database Initialization / Schema functions
def setup_database_schema(supabase: Client):
    """
    Example function that would be run once to set up the necessary tables.
    In a real project, this is usually done via Supabase SQL Editor or migrations.
    
    Required Tables:
    1. transactions: To store DLD real estate data.
    2. rag_documents: To store pgvector embeddings for the 2040 Master Plan.
    """
    pass
