# utils/pairmap.py

# === OANDA ===
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

# === Kraken ===
PAIRMAP_KRAKEN = {
    "BTC/USD": "XBTUSD",
    "ETH/USD": "ETHUSD",
    "ADA/USD": "ADAUSD",
    "XRP/USD": "XRPUSD",
    "SOL/USD": "SOLUSD",
    "DOT/USD": "DOTUSD",
}

# === Alpaca ===
PAIRMAP_ALPACA = {
    "EUR/USD": "EURUSD",
    "GBP/USD": "GBPUSD",
    "BTC/USD": "BTCUSD",
    "ETH/USD": "ETHUSD",
    "AAPL": "AAPL",
    "TSLA": "TSLA",
    "NVDA": "NVDA",
    "SPY": "SPY",
    "QQQ": "QQQ"
}

# === Reverse Maps
REVERSE_OANDA = {v: k for k, v in PAIRMAP_OANDA.items()}
REVERSE_KRAKEN = {v: k for k, v in PAIRMAP_KRAKEN.items()}
REVERSE_ALPACA = {v: k for k, v in PAIRMAP_ALPACA.items()}

# === Combined List
ALL_PAIRMAPS = [PAIRMAP_OANDA, PAIRMAP_KRAKEN, PAIRMAP_ALPACA]
ENABLED_PAIRS = sorted(list({pair for m in ALL_PAIRMAPS for pair in m.keys()}))
