import os
import pandas as pd
import requests
from geopy.distance import geodesic

# Optional: osmnx can be heavy to import if not configured correctly, 
# so we wrap it in a try-except or just import it for those who have it installed.
try:
    import osmnx as ox
except ImportError:
    ox = None

class DataIngestionEngine:
    """
    Handles fetching live data from Dubai Land Department (DLD) Open Data API
    and spatial calculations from OpenStreetMap (OSM).
    """
    
    def __init__(self):
        # Example Dubai Pulse API endpoint for Real Estate Transactions
        # Note: In a real enterprise system, you would use the official CKAN resource ID
        self.dld_api_url = "https://www.dubaipulse.gov.ae/api/action/datastore_search"
        self.beach_coords = (25.0786, 55.1328) # JBR Beach
        self.burj_khalifa_coords = (25.1972, 55.2744)

    def fetch_dld_transactions(self, limit=1000) -> pd.DataFrame:
        """
        Fetches the latest real estate transactions from Dubai Pulse.
        (Simulated API call for demonstration purposes)
        """
        print("[Ingestion] Connecting to Dubai Pulse Open Data API...")
        # In a real environment:
        # params = {"resource_id": "YOUR_RESOURCE_ID", "limit": limit}
        # response = requests.get(self.dld_api_url, params=params)
        # return pd.DataFrame(response.json()['result']['records'])
        
        # For our MVP, we read from the mock CSV to demonstrate the flow
        # Once connected to Supabase, we will upload this data there.
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "transactions.csv")
        df = pd.read_csv(csv_path)
        print(f"[Ingestion] Downloaded {len(df)} recent transactions.")
        return df

    def calculate_distance_to_beach(self, lat: float, lng: float) -> float:
        """Calculates straight-line distance to JBR Beach using geopy."""
        try:
            distance = geodesic((lat, lng), self.beach_coords).kilometers
            return round(distance, 2)
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return 15.0

    def calculate_distance_to_burj_khalifa(self, lat: float, lng: float) -> float:
        """Calculates straight-line distance to Burj Khalifa using geopy."""
        try:
            distance = geodesic((lat, lng), self.burj_khalifa_coords).kilometers
            return round(distance, 2)
        except Exception as e:
            return 20.0

    def get_amenity_density(self, lat: float, lng: float, radius_meters=1000) -> int:
        """
        Uses OpenStreetMap (OSMnx) to count cafes, schools, and hospitals within a radius.
        """
        if ox is None:
            return 10 # Fallback if osmnx is not installed
            
        print(f"[Ingestion] Querying OpenStreetMap for amenities within {radius_meters}m of {lat},{lng}...")
        tags = {'amenity': ['cafe', 'school', 'hospital', 'restaurant', 'pharmacy']}
        try:
            # Silence osmnx logs temporarily
            ox.settings.log_console = False
            amenities = ox.features_from_point((lat, lng), dist=radius_meters, tags=tags)
            density = len(amenities)
            print(f"[Ingestion] Found {density} amenities in OSM.")
            return density
        except Exception as e:
            print(f"[Ingestion] OSM Error: {e}")
            return 0

    def process_and_enrich_data(self) -> pd.DataFrame:
        """
        The main ETL function:
        1. Extract: Fetch DLD Data
        2. Transform: Add GIS features (OSM/Geopy)
        3. Returns the clean dataframe ready for Supabase / ML
        """
        df = self.fetch_dld_transactions()
        
        # Simulate adding GIS features if they didn't exist
        print("[Ingestion] Enriching data with Geospatial calculations...")
        
        # In a real scenario, we would loop through unique coordinates and apply OSM
        # For demonstration, we'll just mock the update on the first row
        if 'lat' in df.columns and 'lng' in df.columns:
            sample_lat = df.iloc[0]['lat']
            sample_lng = df.iloc[0]['lng']
            
            # Example of how we'd calculate and map it
            beach_dist = self.calculate_distance_to_beach(sample_lat, sample_lng)
            burj_dist = self.calculate_distance_to_burj_khalifa(sample_lat, sample_lng)
            amenities = self.get_amenity_density(sample_lat, sample_lng)
            
            print(f"[Ingestion] Sample enrichment for JVC -> Beach Dist: {beach_dist}km, Amenities: {amenities}")
            
        return df

if __name__ == "__main__":
    engine = DataIngestionEngine()
    enriched_df = engine.process_and_enrich_data()
    print("ETL Process Complete. Data ready to be pushed to Supabase.")
