"""
EV Charging Station Locator - Flask Backend
Features: Station locating, filtering by connector type, range calculation, and slot booking
Uses Haversine formula for distance calculation
"""

from flask import Flask, render_template, request, jsonify
from math import radians, sin, cos, sqrt, atan2
import db

# Initialize Flask application
app = Flask(__name__)

# Maximum range of EV in kilometers (at 100% battery)
MAX_RANGE_KM = 300


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth
    using the Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of point 1 (in degrees)
        lat2, lon2: Latitude and longitude of point 2 (in degrees)
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    lon1_rad = radians(lon1)
    lon2_rad = radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def calculate_range(battery_percent: float) -> float:
    """
    Calculate the maximum reachable range based on battery percentage.
    
    Args:
        battery_percent: Current battery percentage (0-100)
    
    Returns:
        Maximum range in kilometers
    """
    return MAX_RANGE_KM * (battery_percent / 100)


@app.route("/")
def index():
    """Render the main page with the map interface."""
    return render_template("index.html")


@app.route("/api/stations", methods=["GET"])
def get_stations():
    """
    API endpoint to fetch and filter charging stations.
    
    Query Parameters:
        lat: User's latitude
        long: User's longitude
        battery_percent: Current battery percentage (0-100)
        connector_type: Type of connector (Tesla, CCS, Type2, or 'all')
    
    Returns:
        JSON array of stations sorted by distance, with reachability info
    """
    try:
        # Get query parameters
        user_lat = request.args.get("lat", type=float)
        user_lon = request.args.get("long", type=float)
        battery_percent = request.args.get("battery_percent", default=100, type=float)
        connector_type = request.args.get("connector_type", type=str)
        
        # Fetch stations based on connector type
        if connector_type and connector_type != "all":
            stations = db.get_stations_by_connector(connector_type)
        else:
            stations = db.get_all_stations()
        
        # Calculate max range based on battery
        max_range = calculate_range(battery_percent)
        
        # Process each station
        stations_with_distance = []
        for station in stations:
            station_data = dict(station)
            
            # Calculate distance if user location is provided
            if user_lat is not None and user_lon is not None:
                distance = haversine_distance(
                    user_lat, user_lon,
                    station["latitude"], station["longitude"]
                )
                station_data["distance"] = distance
                station_data["is_reachable"] = distance <= max_range
            else:
                station_data["distance"] = None
                station_data["is_reachable"] = True
            
            # Get available slots
            station_data["available_slots"] = db.get_available_slots(station["id"])
            
            stations_with_distance.append(station_data)
        
        # Sort by distance if user location is provided
        if user_lat is not None and user_lon is not None:
            stations_with_distance.sort(key=lambda x: x["distance"])
        
        return jsonify({
            "success": True,
            "max_range": max_range,
            "stations": stations_with_distance,
            "count": len(stations_with_distance)
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch stations: {str(e)}"
        }), 500


@app.route("/api/book_slot", methods=["POST"])
def book_slot():
    """
    API endpoint to book a slot at a charging station.
    
    Request Body (JSON):
        station_id: ID of the station
        user_name: Name of the user making the booking
    
    Returns:
        JSON with success status and message
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400
        
        station_id = data.get("station_id")
        user_name = data.get("user_name")
        
        # Validate inputs
        if not station_id:
            return jsonify({
                "success": False,
                "message": "Station ID is required"
            }), 400
        
        if not user_name or not user_name.strip():
            return jsonify({
                "success": False,
                "message": "User name is required"
            }), 400
        
        # Attempt to create booking
        success, message = db.create_booking(station_id, user_name.strip())
        
        if success:
            # Get updated slot info
            available_slots = db.get_available_slots(station_id)
            return jsonify({
                "success": True,
                "message": message,
                "available_slots": available_slots
            })
        else:
            status_code = 400 if message == "Full" else 500
            return jsonify({
                "success": False,
                "message": message
            }), status_code
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/station/<int:station_id>", methods=["GET"])
def get_station_details(station_id):
    """
    API endpoint to get details of a specific station.
    
    Returns:
        JSON with station details and booking info
    """
    try:
        station = db.get_station_by_id(station_id)
        
        if not station:
            return jsonify({
                "success": False,
                "message": "Station not found"
            }), 404
        
        station_data = dict(station)
        station_data["available_slots"] = db.get_available_slots(station_id)
        station_data["bookings"] = db.get_bookings_for_station(station_id)
        
        return jsonify({
            "success": True,
            "station": station_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify server status."""
    return jsonify({
        "status": "healthy",
        "service": "EV Charging Station Locator"
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "success": False,
        "error": "Resource not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)
