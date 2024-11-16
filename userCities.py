import json
import os

# Путь к файлу с городами
USER_CITIES_FILE = "user_cities.json"

# Загружаем данные о городах пользователей
def load_user_cities():
    if os.path.exists(USER_CITIES_FILE):
        with open(USER_CITIES_FILE, "r") as file:
            return json.load(file)
    return {}

# Сохраняем данные о городах в файл
def save_user_cities(user_cities):
    with open(USER_CITIES_FILE, "w") as file:
        json.dump(user_cities, file)

# Изначальный словарь с городами
user_cities = load_user_cities()