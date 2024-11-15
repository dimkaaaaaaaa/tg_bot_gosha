import requests

# Функ для получения погоды
def get_weather(city): 
    api_key = "bd5e378503939ddaee76f12ad7a97608"
    url =  f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(url).json()
    if response.get("main"):
        main_data = response["main"]
        weather_data = response["weather"][0]
        wind_data = response["wind"]

        temperature = main_data["temp"]
        humidity = main_data["humidity"]
        weather_description = response["weather"][0]["description"]
        advice = ""
        wind_speed = wind_data["speed"]

        if "дождь" in weather_description:
            advice = "Возьмите зонт, на улице дождь."
        elif "снег" in weather_description:
            advice = "Снег, оденьтесь теплее."
        elif "ясно" in weather_description:
            advice = "Солнечно, одевайтесь легче."

        return  f"Погода в городе {city}:\n" \
                f"Температура: {temperature}°C\n" \
                f"Влажность: {humidity}%\n" \
                f"Описание: {weather_description.capitalize()}\n" \
                f"Скорость ветра: {wind_speed} м/с" \
                f"{advice}" 
    else:
        return "Город не найден. Проверьте правильность ввода."