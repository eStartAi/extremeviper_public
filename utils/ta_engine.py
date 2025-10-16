import numpy as np

# =====================================================
# === RSI Calculation (short 7-period for faster reaction)
# =====================================================
def calc_rsi(prices, period=7):
    prices = np.array(prices, dtype=float)
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    rsi_values = []

    for i in range(period, len(prices)):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)

    return rsi_values[-1] if rsi_values else 50.0


# =====================================================
# === MACD (shortened: 6,19,5) for intraday momentum
# =====================================================
def calc_macd(prices, short=6, long=19, signal=5):
    prices = np.array(prices, dtype=float)
    if len(prices) < long:
        return 0.0

    def ema(values, window):
        alpha = 2 / (window + 1)
        out = []
        for i, val in enumerate(values):
            if i == 0:
                out.append(val)
            else:
                out.append(out[-1] + alpha * (val - out[-1]))
        return np.array(out)

    ema_short = ema(prices, short)
    ema_long = ema(prices, long)
    macd_line = ema_short - ema_long
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return float(hist[-1])


# =====================================================
# === EMA Slope (3-period) for quick directional bias
# =====================================================
def calc_ema_slope(prices, period=3):
    prices = np.array(prices, dtype=float)
    if len(prices) < period + 1:
        return 0.0

    alpha = 2 / (period + 1)
    ema_vals = []
    for i, val in enumerate(prices):
        if i == 0:
            ema_vals.append(val)
        else:
            ema_vals.append(ema_vals[-1] + alpha * (val - ema_vals[-1]))

    slope = (ema_vals[-1] - ema_vals[-period]) / ema_vals[-period]
    return float(slope)


# =====================================================
# === Synthetic "Volatility / Volume Spike" Estimator
# =====================================================
def calc_vol_spike(highs, lows, period=14):
    """
    Computes a pseudo-volume multiplier using candle range (ATR-like).
    Returns >1.0 when volatility expands.
    """
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    if len(highs) <= period * 2:
        return 1.0

    ranges = highs - lows
    avg_recent = np.mean(ranges[-period:])
    avg_prev = np.mean(ranges[-period * 2 : -period])
    if avg_prev == 0:
        return 1.0

    spike = avg_recent / avg_prev
    return float(round(spike, 2))

