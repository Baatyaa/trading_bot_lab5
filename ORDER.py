import requests
import json
from urllib.parse import urljoin
from datetime import datetime
import os

BASE_URL = "https://api.ataix.kz/"


def save_to_json(data, filename_prefix="order"):
    """Сохраняет данные в JSON файл"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"

        # Создаем папку для результатов, если ее нет
        os.makedirs("order_results", exist_ok=True)
        filepath = os.path.join("order_results", filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Данные сохранены в {filepath}")
        return filepath
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        return None


def get_market_data(api_key, symbol):
    """Получаем рыночные данные с учетом precision"""
    url = urljoin(BASE_URL, "api/symbols")
    headers = {"accept": "application/json", "X-API-Key": api_key}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if isinstance(data, dict) and data.get("status") and "result" in data:
            for market in data["result"]:
                if market.get("symbol") == symbol:
                    return {
                        "bid": float(market.get("bid", 0)),
                        "ask": float(market.get("ask", 0)),
                        "price": float(market.get("price", 0)),
                        "minTradeSize": float(market.get("minTradeSize", 0)),
                        "pricePrecision": float(10 ** -int(market.get("pricePrecision", 3)))
                    }
            print(f"Пара {symbol} не найдена")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


def adjust_price(price, precision):
    """Округляем цену до нужной точности"""
    return round(price // precision * precision, 8)


def create_ataix_order(api_key, symbol, side, order_type, quantity, price=None, discount_percent=0, sub_type="gtc"):
    market_data = get_market_data(api_key, symbol)
    if not market_data:
        error_data = {
            "status": False,
            "error": "Ошибка получения рыночных данных",
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol
        }
        save_to_json(error_data, "error")
        return error_data

    # Рассчитываем цену с учетом precision
    if discount_percent > 0:
        current_bid = market_data["bid"]
        if current_bid <= 0:
            error_data = {
                "status": False,
                "error": "Некорректная цена bid",
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "market_data": market_data
            }
            save_to_json(error_data, "error")
            return error_data

        raw_price = current_bid * (1 - discount_percent / 100)
        price = adjust_price(raw_price, market_data["pricePrecision"])
        print(f"Цена после коррекции: {price} (precision: {market_data['pricePrecision']})")

    url = urljoin(BASE_URL, "api/orders")
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }

    payload = {
        "symbol": symbol,
        "side": side.lower(),
        "type": order_type.lower(),
        "quantity": str(quantity),
        "price": str(price),
        "subType": sub_type
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        # Добавляем дополнительную информацию
        result["request_data"] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "calculated_price": price,
            "timestamp": datetime.now().isoformat()
        }

        # Сохраняем результат
        save_to_json(result, "order_success" if result.get("status") else "order_failed")

        return result
    except Exception as e:
        error_data = {
            "status": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "request_payload": payload
        }
        save_to_json(error_data, "error")
        return error_data


if __name__ == "__main__":
    API_KEY = "ваш API ключ"
    SYMBOL = "ETH/USDT"
    SIDE = "buy"
    ORDER_TYPE = "limit"
    QUANTITY = 0.00001
    DISCOUNT_PERCENT = 8

    print("Получаем данные...")
    market_data = get_market_data(API_KEY, SYMBOL)

    if market_data:
        print(f"\nДанные {SYMBOL}:")
        print(f"Bid: {market_data['bid']}")
        print(f"Ask: {market_data['ask']}")
        print(f"Price Precision: {market_data['pricePrecision']}")

        print("\nСоздаем ордер...")
        result = create_ataix_order(
            api_key=API_KEY,
            symbol=SYMBOL,
            side=SIDE,
            order_type=ORDER_TYPE,
            quantity=QUANTITY,
            discount_percent=DISCOUNT_PERCENT
        )

        print("\nРезультат:")
        print(json.dumps(result, indent=2))
    else:
        print("Ошибка получения данных")