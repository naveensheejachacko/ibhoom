"""
Location utilities for geocoding and distance calculations
"""
import math
import requests
import json
from typing import Optional, Tuple, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Cache for loaded pincode data
_PINCODE_CACHE_LOADED = None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on earth (in kilometers)
    Using the Haversine formula
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
    
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def geocode_pincode(pincode: str) -> Optional[Tuple[float, float]]:
    """
    Convert Indian pincode to latitude and longitude using Postal Pin Code API
    
    Args:
        pincode: Indian postal code (6 digits)
    
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    try:
        # Clean pincode
        pincode = str(pincode).strip()
        
        # Option 1: Use Indian Postal Pin Code API (Free, no rate limit for India pincodes)
        # This is a public API specifically for Indian pincodes
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0 and data[0].get('Status') == 'Success':
                post_offices = data[0].get('PostOffice', [])
                if post_offices and len(post_offices) > 0:
                    # Get first post office location
                    # Note: This API doesn't return lat/long directly
                    # We need to use the district/state info with Nominatim
                    district = post_offices[0].get('District', '')
                    state = post_offices[0].get('State', '')
                    
                    # Use Nominatim with district and state for better accuracy
                    return _geocode_with_nominatim(pincode, district, state)
        
        # Fallback to basic Nominatim
        logger.warning(f"Postal API failed for {pincode}, trying Nominatim")
        return _geocode_with_nominatim(pincode)
        
    except Exception as e:
        logger.error(f"Error geocoding pincode {pincode}: {str(e)}")
        return None


def _geocode_with_nominatim(pincode: str, district: str = None, state: str = "Kerala") -> Optional[Tuple[float, float]]:
    """
    Geocode using Nominatim (OpenStreetMap) API
    
    Args:
        pincode: Postal code
        district: District name (optional, for better accuracy)
        state: State name (default: Kerala)
    
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        
        # Build query with available information
        if district:
            query = f"{pincode}, {district}, {state}, India"
        else:
            query = f"{pincode}, {state}, India"
        
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "in"
        }
        headers = {
            "User-Agent": "Ibhoom-Marketplace/1.0 (Kerala, India)"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                logger.info(f"Geocoded pincode {pincode}: ({lat}, {lon})")
                return (lat, lon)
        
        logger.warning(f"Could not geocode pincode: {pincode}")
        return None
        
    except Exception as e:
        logger.error(f"Error with Nominatim for {pincode}: {str(e)}")
        return None


def load_kerala_pincodes() -> Dict[str, Tuple[float, float, str]]:
    """
    Load Kerala pincode database from JSON file
    Returns a dictionary: pincode -> (latitude, longitude, area_name)
    """
    global _PINCODE_CACHE_LOADED
    
    # Return cached data if already loaded
    if _PINCODE_CACHE_LOADED is not None:
        return _PINCODE_CACHE_LOADED
    
    try:
        # Get path to JSON file
        json_path = Path(__file__).parent.parent.parent / "kerala_pincodes.json"
        
        # Load JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to flat dictionary format
        pincode_db = {}
        for district, pincodes in data.items():
            for pincode, info in pincodes.items():
                pincode_db[pincode] = (info['lat'], info['lon'], info['area'])
        
        # Cache it
        _PINCODE_CACHE_LOADED = pincode_db
        logger.info(f"Loaded {len(pincode_db)} Kerala pincodes from JSON file")
        
        return pincode_db
        
    except FileNotFoundError:
        logger.warning("kerala_pincodes.json not found, using empty pincode database")
        _PINCODE_CACHE_LOADED = {}
        return {}
    except Exception as e:
        logger.error(f"Error loading kerala_pincodes.json: {str(e)}")
        _PINCODE_CACHE_LOADED = {}
        return {}


def geocode_pincode_kerala(pincode: str, db_session=None) -> Optional[Tuple[float, float]]:
    """
    Geocode Kerala pincode using cache-first approach:
    1. Check database cache
    2. Check static database
    3. Geocode via API and cache result
    
    Args:
        pincode: Indian postal code (6 digits)
        db_session: Database session (optional, for caching)
    
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    # Step 1: Try database cache first (fastest)
    if db_session:
        try:
            from ..models.pincode_cache import PincodeCache
            cached = db_session.query(PincodeCache).filter(
                PincodeCache.pincode == pincode
            ).first()
            
            if cached:
                logger.info(f"Geocoded {pincode} from DB cache: ({cached.latitude}, {cached.longitude})")
                return (cached.latitude, cached.longitude)
        except Exception as e:
            logger.warning(f"Cache lookup failed for {pincode}: {str(e)}")
    
    # Step 2: Try local static database (fast, no API call)
    pincode_db = load_kerala_pincodes()
    if pincode in pincode_db:
        lat, lon, city = pincode_db[pincode]
        logger.info(f"Geocoded {pincode} from static DB: {city} ({lat}, {lon})")
        
        # Cache it in database for next time
        if db_session:
            try:
                from ..models.pincode_cache import PincodeCache
                cache_entry = PincodeCache(
                    pincode=pincode,
                    latitude=lat,
                    longitude=lon,
                    district=city,
                    state="Kerala",
                    country="India"
                )
                db_session.add(cache_entry)
                db_session.commit()
            except Exception as e:
                logger.warning(f"Failed to cache {pincode}: {str(e)}")
        
        return (lat, lon)
    
    # Step 3: Geocode via API (slower, but works for any pincode)
    coords = geocode_pincode(pincode)
    
    # Cache the result in database
    if coords and db_session:
        try:
            from ..models.pincode_cache import PincodeCache
            lat, lon = coords
            cache_entry = PincodeCache(
                pincode=pincode,
                latitude=lat,
                longitude=lon,
                state="Kerala",
                country="India"
            )
            db_session.add(cache_entry)
            db_session.commit()
            logger.info(f"Cached geocoded pincode {pincode} in database")
        except Exception as e:
            logger.warning(f"Failed to cache {pincode}: {str(e)}")
    
    return coords


def is_within_radius(
    seller_lat: float, 
    seller_lon: float, 
    customer_lat: float, 
    customer_lon: float, 
    radius_km: float
) -> bool:
    """
    Check if seller is within specified radius of customer
    
    Args:
        seller_lat, seller_lon: Seller's coordinates
        customer_lat, customer_lon: Customer's coordinates
        radius_km: Maximum distance in kilometers
    
    Returns:
        True if seller is within radius, False otherwise
    """
    distance = haversine_distance(seller_lat, seller_lon, customer_lat, customer_lon)
    return distance <= radius_km


def get_city_coordinates(city_name: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates for a city name
    
    Args:
        city_name: Name of the city
    
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "city": city_name,
            "state": "Kerala",
            "country": "India",
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "Ibhoom-Marketplace/1.0 (Kerala, India)"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                logger.info(f"Geocoded city {city_name}: ({lat}, {lon})")
                return (lat, lon)
        
        logger.warning(f"Could not geocode city: {city_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error geocoding city {city_name}: {str(e)}")
        return None

