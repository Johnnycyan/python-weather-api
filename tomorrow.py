import requests
import requests_cache
from weatherCodes import getWeatherInfo
import googlemaps
from cachetools import cached, LFUCache # pip install cachetools (for caching)
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

tomorrowAPI = os.getenv("TOMORROW_API")
gmapsKey = os.getenv("GMAPS_KEY")

cache = LFUCache(maxsize=1000) # 1000 items max in cache at a time (will evict least recently used items)

def getWeather(lat, long, location, json=False):
    with requests_cache.enabled('tomorrow_cache', backend='sqlite', expire_after=300):
        headers = {"accept": "application/json"}
        resultsMain = requests.get(f"https://api.tomorrow.io/v4/weather/realtime?location={lat}%2C{long}&apikey={tomorrowAPI}&units=metric", headers=headers)
        if resultsMain.status_code == 200:
            pass
        else:
            print("Error: " + resultsMain.status_code)
            return False
        results = resultsMain.json()

    temp_c = round(results["data"]["values"]["temperature"], 1)
    temp_f = round(temp_c * 1.8 + 32, 1)
    wind_dir = results["data"]["values"]["windDirection"]
    if float(wind_dir) >= 348.75 or float(wind_dir) <= 11.25:
        wind_dir = "North"
    elif float(wind_dir) >= 11.25 and float(wind_dir) <= 33.75:
        wind_dir = "North East"
    elif float(wind_dir) >= 33.75 and float(wind_dir) <= 56.25:
        wind_dir = "North East"
    elif float(wind_dir) >= 56.25 and float(wind_dir) <= 78.75:
        wind_dir = "North East"
    elif float(wind_dir) >= 78.75 and float(wind_dir) <= 101.25:
        wind_dir = "East"
    elif float(wind_dir) >= 101.25 and float(wind_dir) <= 123.75:
        wind_dir = "South East"
    elif float(wind_dir) >= 123.75 and float(wind_dir) <= 146.25:
        wind_dir = "South East"
    elif float(wind_dir) >= 146.25 and float(wind_dir) <= 168.75:
        wind_dir = "South East"
    elif float(wind_dir) >= 168.75 and float(wind_dir) <= 191.25:
        wind_dir = "South"
    elif float(wind_dir) >= 191.25 and float(wind_dir) <= 213.75:
        wind_dir = "South West"
    elif float(wind_dir) >= 213.75 and float(wind_dir) <= 236.25:
        wind_dir = "South West"
    elif float(wind_dir) >= 236.25 and float(wind_dir) <= 258.75:
        wind_dir = "South West"
    elif float(wind_dir) >= 258.75 and float(wind_dir) <= 281.25:
        wind_dir = "West"
    elif float(wind_dir) >= 281.25 and float(wind_dir) <= 303.75:
        wind_dir = "North West"
    elif float(wind_dir) >= 303.75 and float(wind_dir) <= 326.25:
        wind_dir = "North West"
    elif float(wind_dir) >= 326.25 and float(wind_dir) <= 348.75:
        wind_dir = "North West"
    wind_kph = results["data"]["values"]["windSpeed"]
    wind_mph = round(wind_kph * 0.621371, 2)
    humidity = round(results["data"]["values"]["humidity"])
    condition = getWeatherInfo(str(results["data"]["values"]["weatherCode"]))
    if condition == "Invalid weather code":
        condition = "Hell on Earth"
    feelslike_c = round(float(results["data"]["values"]["temperatureApparent"]), 1)
    feelslike_f = round(feelslike_c * 1.8 + 32, 1)
    rain_mm = results["data"]["values"]["rainIntensity"]
    rain_in = round(rain_mm * 0.0393701, 2)
    snow_mm = results["data"]["values"]["snowIntensity"]
    snow_in = round(snow_mm * 0.0393701, 2)
    precip_mm = rain_mm + snow_mm
    precip_in = rain_in + snow_in
    if precip_mm == 0:
        precip = ""
    else:
        precip = f", {precip_mm}mm ({precip_in}in) of precipitation"
    
    if feelslike_c == temp_c:
        feelslike = ""
    else:
        feelslike = f" which feels like {feelslike_c}°C ({feelslike_f}°F)"

    if json == True:
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
            "rain in millimeters": rain_mm,
            "rain in inches": rain_in,
            "snow in millimeters": snow_mm,
            "snow in inches": snow_in,
            "precipitation in millimeters": precip_mm,
            "precipitation in inches": precip_in
        }
        return data
    else:
        return f"Weather for {location} - {condition}{precip} with a temperature of {temp_c}°C ({temp_f}°F){feelslike}. Wind is blowing from the {wind_dir} at {wind_kph} kph ({wind_mph} mph) and the humidity is {humidity}%"

def getForecast(lat, long, location):
    with requests_cache.enabled('forecast_cache', backend='sqlite', expire_after=300):
        headers = {"accept": "application/json"}
        resultsMain = requests.get(f"https://api.tomorrow.io/v4/weather/forecast?location={lat}%2C{long}&timesteps=daily&units=metric&apikey={tomorrowAPI}&timezone=Europe%2FLondon", headers=headers)
        if resultsMain.status_code == 200:
            pass
        elif resultsMain.status_code == 429:
            print("Error: " + resultsMain.status_code + " - Too many requests. Please try again later.")
            return False
        else:
            print("Error: " + resultsMain.status_code)
            return False
        results = resultsMain.json()

    forecast = []
    for i in range(0, 5): # 5 days of forecast (0 = today)
        date = results["timelines"]["daily"][i]["time"]
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        day_of_week = date.strftime("%A")
        condition = getWeatherInfo(str(results["timelines"]["daily"][i]["values"]["weatherCodeMax"]))
        if condition == "Invalid weather code":
            condition = "Hell on Earth"
        temp_c_high = round(results["timelines"]["daily"][i]["values"]["temperatureMax"], 1)
        temp_f_high = round(temp_c_high * 1.8 + 32, 1)
        temp_c_low = round(results["timelines"]["daily"][i]["values"]["temperatureMin"], 1)
        temp_f_low = round(temp_c_low * 1.8 + 32, 1)

        forecast.append(f"{day_of_week}: {condition} {temp_c_high}°C / {temp_c_low}°C █ ")

    return f"Forecast for {location} █ " + "".join(forecast)

def getForecastF(lat, long, location):
    with requests_cache.enabled('forecast_cache', backend='sqlite', expire_after=300):
        headers = {"accept": "application/json"}
        resultsMain = requests.get(f"https://api.tomorrow.io/v4/weather/forecast?location={lat}%2C{long}&timesteps=daily&units=metric&apikey={tomorrowAPI}&timezone=Europe%2FLondon", headers=headers)
        if resultsMain.status_code == 200:
            pass
        elif resultsMain.status_code == 429:
            print("Error: " + resultsMain.status_code + " - Too many requests. Please try again later.")
            return False
        else:
            print("Error: " + resultsMain.status_code)
            return False
        results = resultsMain.json()

    forecast = []
    for i in range(0, 5): # 5 days of forecast (0 = today)
        date = results["timelines"]["daily"][i]["time"]
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        day_of_week = date.strftime("%A")
        condition = getWeatherInfo(str(results["timelines"]["daily"][i]["values"]["weatherCodeMax"]))
        if condition == "Invalid weather code":
            condition = "Hell on Earth"
        temp_c_high = round(results["timelines"]["daily"][i]["values"]["temperatureMax"], 1)
        temp_f_high = round(temp_c_high * 1.8 + 32, 1)
        temp_c_low = round(results["timelines"]["daily"][i]["values"]["temperatureMin"], 1)
        temp_f_low = round(temp_c_low * 1.8 + 32, 1)

        forecast.append(f"{day_of_week}: {condition} {temp_f_high}°F / {temp_f_low}°F █ ")

    return f"Forecast for {location} █ " + "".join(forecast)

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
    with requests_cache.enabled('location_cache', backed='sqlite'):
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

def forecast(location, format="C"):
    try:
        lat, long = getCoordinatesGoogle(location)
    except:
        lat, long = getCoordinates(location)
    if format == "C":
        result = getForecast(lat, long, location)
    elif format == "F":
        result = getForecastF(lat, long, location)
    return result

if __name__ == "__main__":
    print (main("target"))