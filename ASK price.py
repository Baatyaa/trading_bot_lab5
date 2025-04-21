import requests

def get_highest_bid(symbol):

    symbols_url = 'https://api.ataix.kz/api/symbols'
    symbols_response = requests.get(symbols_url, headers={'accept': 'application/json'})

    if not symbols_response.json().get('status'):
        print("API-ден сауда жұптарын алу мүмкін емес")
        return None

    # 2. Таңдалған жұпты табу
    selected_pair = None
    for pair in symbols_response.json()['result']:
        if pair['symbol'] == symbol:
            selected_pair = pair
            break

    if not selected_pair:
        print(f"{symbol} жұбы табылмады")
        return None

    # 3. Жұптың ағымдағы bid/ask бағасын алу (егер API қолдаса)
    if 'bid' in selected_pair and selected_pair['bid'] != "0.0000000000":
        highest_bid = float(selected_pair['bid'])
        print(f"{symbol} жұбы бойынша ең жоғары сатып алу бағасы (bid): {highest_bid}")
        return highest_bid
    else:
        # Егер bid API-де жоқ болса, depth эндпоинті арқылы алу
        depth_url = f'https://api.ataix.kz/api/depth?symbol={symbol.replace("/", "_")}'
        depth_response = requests.get(depth_url, headers={'accept': 'application/json'})

        if not depth_response.json().get('status'):
            print(f"{symbol} жұбы бойынша деректер жоқ")
            return None

        bids = depth_response.json()['result'].get('bids', [])
        if bids:
            highest_bid = float(bids[0][0])  # bids = [[цена, объем], ...]
            print(f"{symbol} жұбы бойынша ең жоғары сұраныс бағасы (bid): {highest_bid}")
            return highest_bid
        else:
            print(f"{symbol} жұбында белсенді сұраныс жоқ")
            return None


get_highest_bid("ETH/USDT")