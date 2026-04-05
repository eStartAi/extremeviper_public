def normalize_kraken_candles(raw_candles, interval):
    """
    Normalize Kraken candles to:
    [
        {
            'timestamp': ...,
            'open': ...,
            'high': ...,
            'low': ...,
            'close': ...,
            'volume': ...
        },
        ...
    ]
    """
    result = []
    for c in raw_candles:
        try:
            result.append({
                "timestamp": int(float(c[0])),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[6])
            })
        except Exception:
            continue
    return result[-100:]
