import requests

def get_weather_advice(description, temperature):
    if "ясно" in description:
        if temperature > 20:
            advice = "🌞 Ясная погода, отличное время для прогулок! Не забудьте солнцезащитные очки 🕶🫠"
        elif temperature > 10:
            advice = "🌤 Ясно, но прохладно. Возьмите с собой лёгкую куртку 🧥🤗"
        else:
            advice = "❄️ Ясно, но холодно. Не забудьте тёплую одежду 🧤🥶"
    elif "дождь" in description:
        advice = "🌧 Дождь, не забудьте зонт ☂️!"
    elif "снег" in description:
        if temperature < 0:
            advice = "❄️ Снег, возьмите тёплую одежду и одежду, которая не промокает 🧥🥺"
        else:
            advice = "🌨 Снег, но не слишком холодно. Всё равно возьмите тёплую одежду 🧣😌"
    elif "пасмурно" in description:
        if temperature > 15:
            advice = "☁️ Пасмурно, но тепло. Отличное время для прогулок, возьмите куртку на всякий случай 🧥😁"
        else:
            advice = "☁️ Пасмурно и холодно. Лучше взять тёплую одежду 🧣😔"
    elif "облачно" in description:
        if temperature > 15:
            advice = "🌥 Облачно, достаточно тепло, но лучше взять куртку на всякий случай 🧥🙃"
        else:
            advice = "🌥 Облачно, прохладно. Возьмите тёплую одежду 🧤🥱"
    else:
        advice = "🌈 Неопределённая погода. Подготовьтесь к различным условиям 🌦🤪"

    return advice

# Функция для получения погоды с Яндекс API
def get_weather(city): 
    api_key = "c5b830d3-bf94-4bc0-a219-d020d629719f"
    url = f"https://api.weather.yandex.ru/v2/forecast"
    headers = {
        "X-Yandex-API-Key": api_key
    }
    params = {
        "lang": "ru_RU",
        "limit": 1,
        "hours": False,
        "geoid": city  # geoid нужно брать из базы данных Яндекса.
    }

    response = requests.get(url, headers=headers, params=params).json()

    if "fact" in response:
        fact_data = response["fact"]
        temperature = fact_data["temp"]
        condition = fact_data["condition"]  # Условия погоды
        wind_speed = fact_data["wind_speed"]
        humidity = fact_data["humidity"]

        condition_map = {
            "clear": "ясно",
            "partly-cloudy": "малооблачно",
            "cloudy": "облачно с прояснениями",
            "overcast": "пасмурно",
            "drizzle": "морось",
            "light-rain": "небольшой дождь",
            "rain": "дождь",
            "moderate-rain": "умеренный дождь",
            "heavy-rain": "сильный дождь",
            "continuous-heavy-rain": "затяжной сильный дождь",
            "showers": "ливень",
            "wet-snow": "мокрый снег",
            "light-snow": "небольшой снег",
            "snow": "снег",
            "snow-showers": "снегопад",
            "hail": "град",
            "thunderstorm": "гроза",
            "thunderstorm-with-rain": "дождь с грозой",
            "thunderstorm-with-hail": "гроза с градом",
        }

        weather_description = condition_map.get(condition, "неопределённая погода")
        advice = get_weather_advice(weather_description, temperature)

        return (f"Погода в городе {city}:\n"
                f"Температура: {temperature}°C\n"
                f"Влажность: {humidity}%\n"
                f"Описание: {weather_description.capitalize()}\n"
                f"Скорость ветра: {wind_speed} м/с \n"
                f"{advice}")
    else:
        return "Город не найден или произошла ошибка. Проверьте API-ключ или параметры запроса."