import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

# === Global threshold for system import ===
MIN_SCORE_THRESHOLD = float(os.getenv("MIN_SCORE_THRESHOLD", 7.0))


# =====================================================
# === RSI / MACD / EMA Slope Core Calculations ===
# =====================================================
def calculate_rsi(closes, period=14):
    if len(closes) <= period:
        return 50.0  # Neutral if too short

    deltas = np.diff(closes)
    ups = np.clip(deltas, a_min=0, a_max=None)
    downs = -np.clip(deltas, a_min=None, a_max=0)

    ma_up = np.convolve(ups, np.ones(period) / period, mode='valid')
    ma_down = np.convolve(downs, np.ones(period) / period, mode='valid')

    rs = ma_up / (ma_down + 1e-6)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi[-1]) if len(rsi) else 50.0


def exponential_moving_average(data, period):
    if len(data) < period:
        return [float(data[-1])] if len(data) else [0.0]
    ema = [float(data[0])]
    k = 2 / (period + 1)
    for price in data[1:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return ema


def calculate_macd(closes, fast=12, slow=26, signal=9):
    if len(closes) < slow:
        return 0.0
    ema_fast = exponential_moving_average(closes, fast)
    ema_slow = exponential_moving_average(closes, slow)
    macd_line = np.array(ema_fast[-len(ema_slow):]) - np.array(ema_slow)
    signal_line = exponential_moving_average(macd_line, signal)
    if not len(signal_line):
        return 0.0
    return float(macd_line[-1] - signal_line[-1])


def calculate_ema_slope(closes, period=20):
    if len(closes) < period + 2:
        return 0.0
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    ema = np.convolve(closes, weights, mode='valid')
    return float(ema[-1] - ema[-2]) if len(ema) >= 2 else 0.0


# =====================================================
# === UNIVERSAL SCORING ENGINE ===
# =====================================================
def score_signal(signal: dict) -> float:
    """
    Multi-factor signal scorer:
      • RSI, MACD, EMA slope, Volume spike
      • Returns 0–10 confidence score
    """

    # --- Extract or compute indicators ---
    candles = signal.get("candles")
    rsi = signal.get("rsi")
    macd_hist = signal.get("macd_hist")
    ema_slope = signal.get("ema_slope")
    vol_spike_flag = signal.get("volume_spike")

    if candles:
        closes = [c.get("close", 0) for c in candles if "close" in c]
        volumes = [c.get("volume", 1) for c in candles if "volume" in c]

        if len(closes) >= 30:
            rsi = calculate_rsi(closes)
            macd_hist = calculate_macd(closes)
            ema_slope = calculate_ema_slope(closes)

        # Volume spike detection with safe denominator
        if len(volumes) > 3:
            avg_prev = np.mean(volumes[:-1]) or 1  # avoid div/0
            vol_spike = volumes[-1] / avg_prev
            vol_spike_flag = vol_spike > 2.0
        else:
            vol_spike_flag = False

    # Default safe values
    rsi = float(rsi or 50.0)
    macd_hist = float(macd_hist or 0.0)
    ema_slope = float(ema_slope or 0.0)
    vol_spike_flag = bool(vol_spike_flag)

    score = 0.0

    # === RSI Weight ===
    if rsi < 30 or rsi > 70:
        score += 2
    elif rsi < 40 or rsi > 60:
        score += 1

    # === MACD Momentum ===
    if abs(macd_hist) > 0.002:
        score += 2
    elif abs(macd_hist) > 0.001:
        score += 1

    # === EMA Trend Strength ===
    if abs(ema_slope) > 0.1:
        score += 2
    elif abs(ema_slope) > 0.05:
        score += 1

    # === Volume Spike Bonus ===
    if vol_spike_flag:
        score += 1

    # === Volatility bonus ===
    if 3 < score < 6:
        score += 0.5  # gentle bias midrange signals

    final_score = round(float(score), 2)
    logger.info(f"🧠 Scored signal: {final_score}/10 (⚖️ {'Strong' if final_score >= MIN_SCORE_THRESHOLD else 'Moderate'})")

    return final_score

