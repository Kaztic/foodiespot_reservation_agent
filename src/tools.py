from typing import List, Dict, Any, Optional
from data_manager import DataManager

# Initialize the data manager
data_manager = DataManager()

def list_restaurants(cuisine: Optional[str] = None, 
                    location: Optional[str] = None, 
                    party_size: Optional[int] = None,
                    date: Optional[str] = None,
                    time: Optional[str] = None,
                    text: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for restaurants based on the provided criteria.
    
    Args:
        cuisine: Type of cuisine (e.g., Italian, Japanese)
        location: Area or neighborhood (e.g., Downtown, Westside)
        party_size: Number of people in the party
        date: Date for reservation in YYYY-MM-DD format (for filtering)
        time: Time for reservation in HH:MM format (for filtering)
        text: Additional search text to match against name or description
        
    Returns:
        Dictionary with list of matching restaurants and metadata
    """
    criteria = {}
    if cuisine:
        criteria['cuisine'] = cuisine
    if location:
        criteria['location'] = location
    if party_size:
        criteria['party_size'] = party_size
    if text:
        criteria['text'] = text
    
    restaurants = data_manager.get_restaurants(criteria)
    
    # Format the results for display
    results = []
    for restaurant in restaurants:
        result = {
            "id": restaurant["id"],
            "name": restaurant["name"],
            "cuisine": restaurant["cuisine"],
            "location": restaurant["location"],
            "address": restaurant["address"],
            "seating_capacity": restaurant["seating_capacity"],
            "rating": restaurant["rating"]
        }
        results.append(result)
    
    return {
        "count": len(results),
        "restaurants": results
    }

def get_restaurant_details(restaurant_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific restaurant.
    
    Args:
        restaurant_name: The name of the restaurant
        
    Returns:
        Dictionary with complete restaurant details
    """
    restaurant = data_manager.find_restaurant_by_name(restaurant_name)
    
    if not restaurant:
        return {
            "found": False,
            "message": f"Restaurant '{restaurant_name}' not found."
        }
    
    # Format opening hours for display
    hours_display = {}
    for day, hours in restaurant["opening_hours"].items():
        hours_display[day.capitalize()] = hours
    
    return {
        "found": True,
        "restaurant": {
            "id": restaurant["id"],
            "name": restaurant["name"],
            "cuisine": restaurant["cuisine"],
            "location": restaurant["location"],
            "address": restaurant["address"],
            "seating_capacity": restaurant["seating_capacity"],
            "opening_hours": hours_display,
            "rating": restaurant["rating"],
            "description": restaurant["description"]
        }
    }

def check_availability(restaurant_name: str, date: str, time: str, party_size: int) -> Dict[str, Any]:
    """
    Check if a restaurant has availability for a reservation.
    
    Args:
        restaurant_name: The name of the restaurant
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        party_size: Number of people
        
    Returns:
        Dictionary with availability status and message
    """
    try:
        party_size = int(party_size)
        if party_size <= 0:
            return {
                "error": True,
                "message": "Party size must be a positive number."
            }
    except (ValueError, TypeError):
        return {
            "error": True,
            "message": "Invalid party size. Please provide a number."
        }
    
    # Check date format
    if not date or len(date.split('-')) != 3:
        return {
            "error": True,
            "message": "Invalid date format. Please use YYYY-MM-DD format."
        }
    
    # Check time format
    if not time or len(time.split(':')) != 2:
        return {
            "error": True,
            "message": "Invalid time format. Please use HH:MM format (24-hour)."
        }
    
    availability = data_manager.check_availability(restaurant_name, date, time, party_size)
    return availability

def make_reservation(restaurant_name: str, date: str, time: str, 
                    party_size: int, user_name: str, user_phone: str) -> Dict[str, Any]:
    """
    Book a reservation at a restaurant.
    
    Args:
        restaurant_name: The name of the restaurant
        date: Date in YYYY-MM-DD format
        time: Time in HH:MM format (24-hour)
        party_size: Number of people
        user_name: Name of the person making the reservation
        user_phone: Contact phone number
        
    Returns:
        Dictionary with reservation confirmation details
    """
    # Validate inputs
    try:
        party_size = int(party_size)
        if party_size <= 0:
            return {
                "error": True,
                "message": "Party size must be a positive number."
            }
    except (ValueError, TypeError):
        return {
            "error": True,
            "message": "Invalid party size. Please provide a number."
        }
    
    if not user_name:
        return {
            "error": True,
            "message": "Please provide your name for the reservation."
        }
    
    if not user_phone:
        return {
            "error": True,
            "message": "Please provide a contact phone number for the reservation."
        }
    
    # Check date format
    if not date or len(date.split('-')) != 3:
        return {
            "error": True,
            "message": "Invalid date format. Please use YYYY-MM-DD format."
        }
    
    # Check time format
    if not time or len(time.split(':')) != 2:
        return {
            "error": True,
            "message": "Invalid time format. Please use HH:MM format (24-hour)."
        }
    
    result = data_manager.make_reservation(
        restaurant_name, date, time, party_size, user_name, user_phone
    )
    
    return result

# Define tool schemas for Gemini API
TOOL_SCHEMAS = [
    {
        "name": "list_restaurants",
        "description": "Search for restaurants based on criteria like cuisine, location, or party size.",
        "parameters": {
            "type": "object",
            "properties": {
                "cuisine": {
                    "type": "string",
                    "description": "Type of cuisine (e.g., Italian, Japanese, Indian)"
                },
                "location": {
                    "type": "string",
                    "description": "Area or neighborhood (e.g., Downtown, Westside)"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of people in the party"
                },
                "text": {
                    "type": "string",
                    "description": "Additional search text to match against restaurant name or description"
                },
                "date": {
                    "type": "string",
                    "description": "Date for reservation in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "description": "Time for reservation in HH:MM format (24-hour)"
                }
            }
        }
    },
    {
        "name": "get_restaurant_details",
        "description": "Get detailed information about a specific restaurant.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_name": {
                    "type": "string",
                    "description": "Name of the restaurant to get details for"
                }
            },
            "required": ["restaurant_name"]
        }
    },
    {
        "name": "check_availability",
        "description": "Check if a restaurant has availability for a reservation.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_name": {
                    "type": "string",
                    "description": "Name of the restaurant to check availability"
                },
                "date": {
                    "type": "string",
                    "description": "Date for reservation in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "description": "Time for reservation in HH:MM format (24-hour)"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of people in the party"
                }
            },
            "required": ["restaurant_name", "date", "time", "party_size"]
        }
    },
    {
        "name": "make_reservation",
        "description": "Book a reservation at a restaurant.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_name": {
                    "type": "string",
                    "description": "Name of the restaurant to book"
                },
                "date": {
                    "type": "string",
                    "description": "Date for reservation in YYYY-MM-DD format"
                },
                "time": {
                    "type": "string",
                    "description": "Time for reservation in HH:MM format (24-hour)"
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of people in the party"
                },
                "user_name": {
                    "type": "string",
                    "description": "Name of the person making the reservation"
                },
                "user_phone": {
                    "type": "string",
                    "description": "Contact phone number"
                }
            },
            "required": ["restaurant_name", "date", "time", "party_size", "user_name", "user_phone"]
        }
    }
]

# Maps function names to actual functions
TOOL_MAP = {
    "list_restaurants": list_restaurants,
    "get_restaurant_details": get_restaurant_details,
    "check_availability": check_availability,
    "make_reservation": make_reservation
} 