from binance.client import Client
from data.config import API_KEY, API_SECRET

# Binance API mijozini o‘rnatish
client = Client(API_KEY, API_SECRET)

# Narxlar va trendlar olish
def get_signals(symbols):
    try:
        signals = []

        for symbol in symbols:
            # O'rta narxni olish
            ticker = client.get_ticker(symbol=symbol)
            price_change = float(ticker["priceChangePercent"])  # Foizdagi o‘zgarish
            price = float(ticker["lastPrice"])
            volume = float(ticker["volume"])

            # Absolyut o‘zgarishni hisoblash
            change_absolute = (price_change / 100) * price

            signal = {
                "pair": symbol,
                "trend": "Bullish" if price_change > 0 else "Bearish",
                "price": price,
                "change": f"{price_change:.2f}%",
                "change_absolute": change_absolute,
                "volume": volume
            }
            signals.append(signal)

        return signals
    except Exception as e:
        print(f"Xato: {e}")
        return []
