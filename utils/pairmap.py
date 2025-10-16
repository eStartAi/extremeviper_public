# utils/pairmap.py

# ✅ OANDA uses underscore-separated symbols
PAIRMAP_OANDA = {
    "EUR/USD": "EUR_USD",
    "GBP/USD": "GBP_USD",
    "USD/JPY": "USD_JPY",
    "AUD/JPY": "AUD_JPY",
    "USD/CAD": "USD_CAD",
    "NZD/USD": "NZD_USD",
    "EUR/JPY": "EUR_JPY",
    "GBP/JPY": "GBP_JPY",
    "EUR/GBP": "EUR_GBP",
    "AUD/USD": "AUD_USD",
}

# ✅ Kraken uses uppercase + no slash
PAIRMAP_KRAKEN = {
    "BTC/USD": "XBTUSD",
    "ETH/USD": "ETHUSD",
    "ADA/USD": "ADAUSD",
    "XRP/USD": "XRPUSD",
    "SOL/USD": "SOLUSD",
    "DOT/USD": "DOTUSD",
}
