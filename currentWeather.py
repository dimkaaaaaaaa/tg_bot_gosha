import requests

def get_weather_advice(description, temperature):
    if "ясно" in description:
        if temperature > 20:
            advice = "🌞 Ясная погода, отличное время для прогулок! Не забудьте солнцезащитные очки 🕶️🫠"
        elif temperature > 10:
            advice = "🌤️ Ясно, но прохладно. Возьмите с собой лёгкую куртку 🧥🤗"
        else:
            advice = "❄️ Ясно, но холодно. Не забудьте тёплую одежду 🧤🥶"
    elif "дождь" in description:
        advice = "🌧️ Дождь, не забудьте зонт ☂️!"
    elif "снег" in description:
        if temperature < 0:
            advice = "❄️ Снег, возьмите тёплую одежду и одежду, которая не промокает 🧥🥺"
        else:
            advice = "🌨️ Снег, но не слишком холодно. Всё равно возьмите тёплую одежду 🧣😌"
    elif "пасмурно" in description:
        if temperature > 15:
            advice = "☁️ Пасмурно, но тепло. Отличное время для прогулок, возьмите куртку на всякий случай 🧥😁"
        else:
            advice = "☁️ Пасмурно и холодно. Лучше взять тёплую одежду 🧣😔"
    elif "облачно с прояснениями" in description:
        if temperature > 15:
            advice = "🌥️ Облачно с прояснениями, достаточно тепло, но лучше взять куртку на всякий случай 🧥🙃"
        else:
            advice = "🌥️ Облачно с прояснениями, прохладно. Возьмите тёплую одежду 🧤🥱"
    else:
        advice = "🌈 Неопределённая погода. Подготовьтесь к различным условиям 🌦️🤪"

    return advice

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
        advice = get_weather_advice(weather_description, temperature)
        wind_speed = wind_data["speed"]

        return  f"Погода в городе {city}:\n" \
                f"Температура: {temperature}°C\n" \
                f"Влажность: {humidity}%\n" \
                f"Описание: {weather_description.capitalize()}\n" \
                f"Скорость ветра: {wind_speed} м/с \n" \
                f"{advice}" 
    else:
        return "Город не найден. Проверьте правильность ввода."