"""
EV Charging Station Locator - Main Flask Application
A web application to display nearby EV charging stations on an interactive map.
"""

from flask import Flask, render_template, jsonify, request
from db import get_all_stations, add_station

# Initialize Flask application
app = Flask(__name__)


@app.route("/")
def index():
    """
    Render the main page with the map and station list.
    
    Returns:
        Rendered HTML template
    """
    return render_template("index.html")


@app.route("/api/stations", methods=["GET"])
def api_get_stations():
    """
    API endpoint to fetch all EV charging stations.
    
    Returns:
        JSON response containing list of stations or error message
    
    Response format:
        Success: {"success": true, "data": [...stations], "count": n}
        Error: {"success": false, "error": "error message"}
    """
    try:
        stations = get_all_stations()
        return jsonify({
            "success": True,
            "data": stations,
            "count": len(stations)
        })
    except ValueError as e:
        # Configuration error (missing credentials)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    except Exception as e:
        # Database or other errors
        return jsonify({
            "success": False,
            "error": f"Failed to fetch stations: {str(e)}"
        }), 500


@app.route("/api/stations", methods=["POST"])
def api_add_station():
    """
    API endpoint to add a new EV charging station.
    
    Request body should contain:
        - name: Station name
        - latitude: Latitude coordinate
        - longitude: Longitude coordinate
        - charger_type: Type of charger
        - price: Price per kWh
        - status: Station status (Available, Busy, Maintenance)
    
    Returns:
        JSON response with created station or error message
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'latitude', 'longitude', 'charger_type', 'price', 'status']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate latitude and longitude
        try:
            lat = float(data['latitude'])
            lon = float(data['longitude'])
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")
            data['latitude'] = lat
            data['longitude'] = lon
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid latitude or longitude values"
            }), 400
        
        # Add station to database
        new_station = add_station(data)
        
        return jsonify({
            "success": True,
            "data": new_station,
            "message": "Station added successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to add station: {str(e)}"
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify server status.
    
    Returns:
        JSON response with server status
    """
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
    # In production, use a proper WSGI server like Gunicorn
    app.run(host="0.0.0.0", port=5000, debug=True)
