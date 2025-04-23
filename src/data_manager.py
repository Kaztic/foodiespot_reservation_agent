import json
import os
import datetime
import random
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any

class DataManager:
    """Class to manage restaurant data operations."""
    
    def __init__(self, data_file: str = None):
        """
        Initialize the DataManager.
        
        Args:
            data_file: Path to the restaurant data JSON file
        """
        if data_file is None:
            # Use default path relative to the project root
            current_dir = Path(__file__).parent
            self.data_file = current_dir.parent / "data" / "restaurants.json"
        else:
            self.data_file = Path(data_file)
        
        self.restaurants = self._load_data()
        # In-memory storage for reservations (not persisted)
        self.reservations = {}
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load restaurant data from JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading restaurant data: {e}")
            return []
    
    def get_restaurants(self, criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get restaurants based on optional filtering criteria.
        
        Args:
            criteria: Dict containing filter parameters like cuisine, location, etc.
            
        Returns:
            List of restaurant dictionaries matching criteria
        """
        if not criteria:
            return self.restaurants
        
        filtered_restaurants = self.restaurants
        
        # Filter by cuisine
        if 'cuisine' in criteria and criteria['cuisine']:
            cuisine = criteria['cuisine'].lower()
            filtered_restaurants = [r for r in filtered_restaurants 
                                  if r['cuisine'].lower() == cuisine or 
                                  cuisine in r['cuisine'].lower()]
        
        # Filter by location
        if 'location' in criteria and criteria['location']:
            location = criteria['location'].lower()
            filtered_restaurants = [r for r in filtered_restaurants 
                                  if r['location'].lower() == location or
                                  location in r['location'].lower() or
                                  location in r['address'].lower()]
        
        # Filter by party size (if it can accommodate)
        if 'party_size' in criteria and criteria['party_size']:
            try:
                party_size = int(criteria['party_size'])
                filtered_restaurants = [r for r in filtered_restaurants 
                                      if r['seating_capacity'] >= party_size]
            except (ValueError, TypeError):
                pass  # Ignore invalid party sizes
        
        # Additional text-based search in name or description
        if 'text' in criteria and criteria['text']:
            text = criteria['text'].lower()
            text_matches = []
            for r in filtered_restaurants:
                if (text in r['name'].lower() or 
                    text in r['description'].lower() or
                    any(text in tag.lower() for tag in r.get('tags', []))):
                    text_matches.append(r)
            filtered_restaurants = text_matches
            
        return filtered_restaurants
    
    def find_restaurant_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a specific restaurant by name (with partial matching).
        
        Args:
            name: The name of the restaurant to find
            
        Returns:
            Restaurant dictionary if found, None otherwise
        """
        if not name:
            return None
            
        # Try exact match first (case-insensitive)
        name_lower = name.lower()
        for restaurant in self.restaurants:
            if restaurant['name'].lower() == name_lower:
                return restaurant
        
        # Try partial match
        matches = []
        for restaurant in self.restaurants:
            if name_lower in restaurant['name'].lower():
                matches.append(restaurant)
        
        if matches:
            # Return the closest match if multiple found
            if len(matches) == 1:
                return matches[0]
            else:
                # Sort by length difference to find closest match
                matches.sort(key=lambda r: abs(len(r['name']) - len(name)))
                return matches[0]
                
        return None
    
    def check_availability(self, restaurant_name: str, date: str, time: str, party_size: int) -> Dict[str, Any]:
        """
        Check if a reservation is possible for the given parameters.
        
        Args:
            restaurant_name: Name of the restaurant
            date: Date in "YYYY-MM-DD" format
            time: Time in "HH:MM" format
            party_size: Number of people
            
        Returns:
            Dict with availability status and additional information
        """
        restaurant = self.find_restaurant_by_name(restaurant_name)
        if not restaurant:
            return {
                "available": False,
                "message": f"Restaurant '{restaurant_name}' not found."
            }
        
        try:
            # Parse date and time
            booking_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            booking_time = datetime.datetime.strptime(time, "%H:%M").time()
            
            # Check if party size exceeds capacity
            if party_size > restaurant['seating_capacity']:
                return {
                    "available": False,
                    "message": f"Party size of {party_size} exceeds the maximum capacity of {restaurant['seating_capacity']}.",
                    "restaurant": restaurant['name']
                }
            
            # Get day of week
            day_of_week = booking_date.strftime("%A").lower()
            
            # Check if restaurant is open that day
            if restaurant['opening_hours'].get(day_of_week) == "Closed":
                return {
                    "available": False, 
                    "message": f"{restaurant['name']} is closed on {day_of_week.capitalize()}.",
                    "restaurant": restaurant['name']
                }
            
            # Check if time is within opening hours
            hours = restaurant['opening_hours'].get(day_of_week, "")
            if "-" in hours:
                open_time_str, close_time_str = hours.split("-")
                open_time = datetime.datetime.strptime(open_time_str, "%H:%M").time()
                close_time = datetime.datetime.strptime(close_time_str, "%H:%M").time()
                
                if booking_time < open_time or booking_time > close_time:
                    return {
                        "available": False,
                        "message": f"{restaurant['name']} is only open from {open_time_str} to {close_time_str} on {day_of_week.capitalize()}.",
                        "restaurant": restaurant['name'],
                        "opening_hours": hours
                    }
            
            # For simulation purposes, we'll randomly decide if there's availability
            # In a real system, this would check against existing reservations
            is_available = random.random() > 0.2  # 80% chance of availability
            
            if is_available:
                return {
                    "available": True,
                    "message": f"Table for {party_size} is available at {restaurant['name']} on {date} at {time}.",
                    "restaurant": restaurant['name'],
                    "date": date,
                    "time": time,
                    "party_size": party_size
                }
            else:
                return {
                    "available": False,
                    "message": f"Sorry, {restaurant['name']} is fully booked at that time. Please try another time.",
                    "restaurant": restaurant['name']
                }
                
        except ValueError as e:
            return {
                "available": False,
                "message": f"Invalid date or time format: {str(e)}",
                "restaurant": restaurant_name
            }
    
    def make_reservation(self, restaurant_name: str, date: str, time: str, 
                        party_size: int, user_name: str, user_phone: str) -> Dict[str, Any]:
        """
        Make a reservation at the specified restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            date: Date in "YYYY-MM-DD" format
            time: Time in "HH:MM" format
            party_size: Number of people
            user_name: Name of the person making the reservation
            user_phone: Contact phone number
            
        Returns:
            Dict with reservation details including confirmation status
        """
        # First check availability
        availability = self.check_availability(restaurant_name, date, time, party_size)
        
        if not availability["available"]:
            return {
                "success": False,
                "message": availability["message"],
                "restaurant": restaurant_name
            }
        
        # Generate a confirmation code
        confirmation_code = f"RS-{random.randint(10000, 99999)}"
        
        # Store the reservation in memory
        reservation = {
            "confirmation_code": confirmation_code,
            "restaurant_name": restaurant_name,
            "date": date,
            "time": time,
            "party_size": party_size,
            "user_name": user_name,
            "user_phone": user_phone,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        self.reservations[confirmation_code] = reservation
        
        return {
            "success": True,
            "confirmation_code": confirmation_code,
            "message": f"Reservation confirmed at {restaurant_name} for {party_size} people on {date} at {time}.",
            "restaurant": restaurant_name,
            "date": date,
            "time": time,
            "party_size": party_size,
            "user_name": user_name
        }
    
    def get_reservation(self, confirmation_code: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a reservation by confirmation code.
        
        Args:
            confirmation_code: The reservation confirmation code
            
        Returns:
            Reservation details or None if not found
        """
        return self.reservations.get(confirmation_code) 