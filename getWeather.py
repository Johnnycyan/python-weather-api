import requests
import requests_cache
import googlemaps
from cachetools import cached, LFUCache # pip install cachetools (for caching)
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

cache = LFUCache(maxsize=1000) # 1000 items max in cache at a time (will evict least recently used items)

lat = 40.7128
long = 74.0060
weatherApi = os.getenv("WEATHER_API")
gmapsKey = os.getenv("GMAPS_KEY")

locationDict = {}

def getWeather(lat, long, location, json=False):
    with requests_cache.enabled('weather_cache', backend='sqlite', expire_after=60):
        results = requests.get(f"https://api.weatherapi.com/v1/current.json?key={weatherApi}&q={lat},{long}&aqi=no").json()

    temp_c = results["current"]["temp_c"]
    temp_f = results["current"]["temp_f"]
    wind_dir = results["current"]["wind_dir"]
    if wind_dir == "N":
        wind_dir = "North"
    elif wind_dir == "S":
        wind_dir = "South"
    elif wind_dir == "E":
        wind_dir = "East"
    elif wind_dir == "W":
        wind_dir = "West"
    elif wind_dir == "NE":
        wind_dir = "North East"
    elif wind_dir == "NW":
        wind_dir = "North West"
    elif wind_dir == "SE":
        wind_dir = "South East"
    elif wind_dir == "SW":
        wind_dir = "South West"
    elif wind_dir == "NNE":
        wind_dir = "North East"
    elif wind_dir == "NNW":
        wind_dir = "North West"
    elif wind_dir == "ENE":
        wind_dir = "North East"
    elif wind_dir == "ESE":
        wind_dir = "South East"
    elif wind_dir == "SSE":
        wind_dir = "South East"
    elif wind_dir == "SSW":
        wind_dir = "South West"
    elif wind_dir == "WSW":
        wind_dir = "South West"
    elif wind_dir == "WNW":
        wind_dir = "North West"
    wind_kph = results["current"]["wind_kph"]
    wind_mph = results["current"]["wind_mph"]
    humidity = results["current"]["humidity"]
    condition = results["current"]["condition"]["text"]
    name = results["location"]["name"]
    country = results["location"]["country"]
    feelslike_c = results["current"]["feelslike_c"]
    feelslike_f = results["current"]["feelslike_f"]
    precip_mm = results["current"]["precip_mm"]
    precip_in = results["current"]["precip_in"]
    if precip_mm == 0:
        precip = ""
    else:
        precip = f" equaling {precip_mm}mm ({precip_in}in) of precipitation"

    if feelslike_c == temp_c:
        feelslike = ""
    else:
        feelslike = f" which feels like {feelslike_c}°C ({feelslike_f}°F)"

    if json:
        data = {
            "location": location,
            "condition": condition,
            "temperature celsius": temp_c,
            "temperature fahrenheit": temp_f,
            "wind direction": wind_dir,
            "wind in kph": wind_kph,
            "wind in mph": wind_mph,
            "humidity": humidity,
            "feelslike temperature celsius": feelslike_c,
            "feelslike temperature fahrenheit": feelslike_f,
            "precipitation in millimeters": precip_mm,
            "precipitation in inches": precip_in
        }
        return data
    else:
        return f"Weather for {location} - {condition}{precip} with a temperature of {temp_c}°C ({temp_f}°F){feelslike}. Wind is blowing from the {wind_dir} at {wind_kph} kph ({wind_mph} mph) and the humidity is {humidity}%"

def getCoordinates(location):
    with requests_cache.enabled('location_cache', backend='sqlite'):
        headers = {
            'User-Agent': 'Cyan Twitch Weather Grabber/1.0',
        }
        results = requests.get(f"https://nominatim.openstreetmap.org/search?format=json&limit=1&q={location}", headers=headers).json()

    lat = results[0]["lat"]
    long = results[0]["lon"]

    return lat, long

@cached(cache) # cache the result of this function
def getCoordinatesGoogle(location):
    with requests_cache.enabled('location_cache', backend='sqlite'):
        gmaps = googlemaps.Client(key=gmapsKey)
        geocode_result = gmaps.geocode(location)
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    long = geocode_result[0]["geometry"]["location"]["lng"]
    return lat, long

def main(location, json=False):
    try:
        lat, long = getCoordinatesGoogle(location)
    except:
        lat, long = getCoordinates(location)
    result = getWeather(lat, long, location, json)
    return result

if __name__ == "__main__":
    main()