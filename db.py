"""
Database module for EV Charging Station Locator
Handles Supabase (PostgreSQL) connection and queries for stations and bookings
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
    """
    try:
        client = get_supabase_client()
        response = client.table("stations").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching stations: {e}")
        raise


def get_stations_by_connector(connector_type: str) -> list:
    """
    Fetch stations filtered by connector type.
    
    Args:
        connector_type: Type of connector (Tesla, CCS, Type2)
    
    Returns:
        list: List of stations matching the connector type
    """
    try:
        client = get_supabase_client()
        response = client.table("stations").select("*").eq("connector_type", connector_type).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching stations by connector: {e}")
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
        
        # Safely handle empty results
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching station {station_id}: {e}")
        raise


def get_booking_count(station_id: int) -> int:
    """
    Get the current number of bookings for a station.
    
    Args:
        station_id: The ID of the station
    
    Returns:
        int: Number of current bookings
    """
    try:
        client = get_supabase_client()
        response = client.table("bookings").select("id", count="exact").eq("station_id", station_id).execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        print(f"Error counting bookings: {e}")
        return 0


def get_available_slots(station_id: int) -> int:
    """
    Get the number of available slots for a station.
    
    Args:
        station_id: The ID of the station
    
    Returns:
        int: Number of available slots
    """
    try:
        station = get_station_by_id(station_id)
        if not station:
            return 0
        
        total_slots = station.get("total_slots", 0)
        current_bookings = get_booking_count(station_id)
        
        return max(0, total_slots - current_bookings)
    except Exception as e:
        print(f"Error calculating available slots: {e}")
        return 0


def create_booking(station_id: int, user_name: str) -> tuple:
    """
    Create a new booking for a station.
    
    Args:
        station_id: The ID of the station to book
        user_name: Name of the user making the booking
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Get station details
        station = get_station_by_id(station_id)
        if not station:
            return False, "Station not found"
        
        # Check available slots
        current_bookings = get_booking_count(station_id)
        total_slots = station.get("total_slots", 0)
        
        if current_bookings >= total_slots:
            return False, "Full"
        
        # Create the booking
        client = get_supabase_client()
        response = client.table("bookings").insert({
            "station_id": station_id,
            "user_name": user_name
        }).execute()
        
        if response.data:
            return True, "Success"
        else:
            return False, "Booking failed"
            
    except Exception as e:
        print(f"Error creating booking: {e}")
        return False, str(e)


def get_bookings_for_station(station_id: int) -> list:
    """
    Get all bookings for a specific station.
    
    Args:
        station_id: The ID of the station
    
    Returns:
        list: List of booking records
    """
    try:
        client = get_supabase_client()
        response = client.table("bookings").select("*").eq("station_id", station_id).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        return []
