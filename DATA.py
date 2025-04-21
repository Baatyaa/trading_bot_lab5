import os
import requests

API_KEY = os.getenv("API_KEY")
response = requests.get(
    "https://api.ataix.kz/api/user/balances/USDT",
    headers={"accept": "application/json", "X-API-Key": "ваш API ключ"}
)

data = response.json()

available_usdt = data['result']['available']
print(f"Қолжетімді USDT балансы: {available_usdt}")

