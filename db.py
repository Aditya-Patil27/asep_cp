"""
Database connection module for Supabase.
Handles all database operations for the EV Charging Station Locator.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client
supabase: Client = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    Uses singleton pattern to avoid multiple connections.
    
    Returns:
        Client: Supabase client instance
    
    Raises:
        ValueError: If Supabase credentials are not configured
    """
    global supabase
    
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Supabase credentials not found. "
                "Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
            )
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    return supabase


def get_all_stations() -> list:
    """
    Fetch all EV charging stations from the database.
    
    Returns:
        list: List of dictionaries containing station data.
              Each dictionary has: id, name, latitude, longitude, 
              charger_type, price, status
    
    Raises:
        Exception: If database query fails
    """
    try:
        client = get_supabase_client()
        response = client.table("stations").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching stations: {e}")
        raise


def get_station_by_id(station_id: int) -> dict:
    """
    Fetch a single station by its ID.
    
    Args:
        station_id: The ID of the station to fetch
    
    Returns:
        dict: Station data or None if not found
    """
    try:
        client = get_supabase_client()
        response = client.table("stations").select("*").eq("id", station_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching station {station_id}: {e}")
        raise


def get_available_stations() -> list:
    """
    Fetch only available EV charging stations.
    
    Returns:
        list: List of available stations
    """
    try:
        client = get_supabase_client()
        response = client.table("stations").select("*").eq("status", "Available").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching available stations: {e}")
        raise


def add_station(station_data: dict) -> dict:
    """
    Add a new EV charging station to the database.
    
    Args:
        station_data: Dictionary containing station information
                     (name, latitude, longitude, charger_type, price, status)
    
    Returns:
        dict: The newly created station data
    
    Raises:
        Exception: If database insert fails
    """
    try:
        client = get_supabase_client()
        response = client.table("stations").insert(station_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding station: {e}")
        raise
