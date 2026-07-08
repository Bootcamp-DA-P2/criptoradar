from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

precio = cg.get_price(ids="bitcoin", vs_currencies="usd")

print(precio)
