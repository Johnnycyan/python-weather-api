from flask import Flask
from flask import request
from markupsafe import escape
from getWeather import main as getWeather
from tomorrow import main as getWeatherTomorrow
from tomorrow import forecast as getWeatherForecast
import html

app = Flask(__name__)

@app.route('/weather')
def application():
    try:
        fallback = request.args.get('fallback')
    except:
        return "Error: No fallback specified."
    try:
        location = request.args.get('location')
        location = location.strip()
        location = html.unescape(location)
    except:
        return "Error: No location specified."
    try:
        format = request.args.get('format')
        format = format.upper()
    except:
        format = "C"
    if location == None:
        location = fallback
    elif location == "":
        location = fallback
    elif "!" in location:
        location = fallback
    elif "@" in location:
        location = fallback
    try:
        forecast = request.args.get('forecast')
        if forecast == "true":
            forecast = True
        else:
            forecast = False
    except:
        forecast = False
    try:
        json = request.args.get('json')
        if json == "true":
            json = True
        else:
            json = False
    except:
        json = False
    if forecast == False:
        try:
            result = getWeatherTomorrow(location, json)
            if result == False:
                try:
                    result = getWeather(location, json)
                    return result
                except:
                    return "Error: Invalid location."
            return result
        except:
            try:
                result = getWeather(location, json)
                return result
            except:
                return "Error: Invalid location."
    else:
        try:
            result = getWeatherForecast(location, format)
            if result == False:
                return "Error: Invalid location."
            return result
        except:
            return "Error: Invalid location."

if __name__ == "__main__":
    app.run()