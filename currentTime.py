from datetime import datetime
import requests
import pytz

def get_coordinates(city):
    api_key = "bd5e378503939ddaee76f12ad7a97608"
    url =  f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(url).json()
    if response.get("coord"):
        return response["coord"]["lat"], response["coord"]["lon"]
    else:
        return None, None

def get_timezone(lat, lon):
    api_key = "6HHF7D61JGL5"
    url = f"http://api.timezonedb.com/v2.1/get-time-zone?key={api_key}&format=json&by=position&lat={lat}&lng={lon}"
    response = requests.get(url).json() 
    if response.get("status") == "OK":
        return response["zoneName"]
    else:
        return None

def get_current_time(city):
    lat, lon = get_coordinates(city)
    if lat is not None and lon is not None:
        timezone = get_timezone(lat, lon)
        if timezone:
            city_time = datetime.now(pytz.timezone(timezone))
            return city_time.strftime("%H:%M:%S")
        else:
            return "Не удалось определить временную зону😔"