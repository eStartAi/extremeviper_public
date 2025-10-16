import logging
import math

logger = logging.getLogger(__name__)

def score_signal(signal: dict) -> dict:
    """
    Compute a 0–10 confidence score based on RSI, MACD, EMA slope, and Volume spike.
    Handles missing or invalid fields gracefully.
    """

    try:
        # Extract safely
        rsi = float(signal.get("rsi", 50))
        macd = float(signal.get("macd", 0))
        ema_slope = float(signal.get("ema_slope", 0))
        volume_spike = float(signal.get("volume_spike", 1.0))
        trend = signal.get("trend", "sideways")

        # --- RSI component ---
        if rsi < 30:
            rsi_score = 8 + (30 - rsi) / 5     # oversold → strong buy
        elif rsi > 70:
            rsi_score = 8 + (rsi - 70) / 5     # overbought → strong sell
        else:
            rsi_score = 5 - abs(50 - rsi) / 10 # neutral zone penalty
        rsi_score = max(0, min(rsi_score, 10))

        # --- MACD component ---
        macd_score = min(10, max(0, 5 + 3 * math.tanh(macd * 2)))

        # --- EMA slope component ---
        slope_score = min(10, max(0, 5 + ema_slope * 100))

        # --- Volume spike component ---
        if volume_spike > 1.5:
            volume_score = 2
        elif volume_spike < 0.7:
            volume_score = -1
        else:
            volume_score = 0

        # Combine base score
        base_score = (rsi_score * 0.4) + (macd_score * 0.3) + (slope_score * 0.3) + volume_score

        # --- Trend penalty/bonus ---
        if trend == "sideways":
            base_score *= 0.7
        elif trend == "strong":
            base_score *= 1.1

        confidence = round(max(0, min(base_score, 10)), 2)
        signal["score"] = confidence

        # --- Human-readable tag ---
        if confidence >= 8:
            signal["signal_strength"] = "🔥 Strong"
        elif confidence >= 5:
            signal["signal_strength"] = "⚖️ Moderate"
        else:
            signal["signal_strength"] = "🧊 Weak"

        logger.info(f"🧠 Scored signal: {confidence}/10 ({signal['signal_strength']})")
        return signal

    except Exception as e:
        logger.error(f"❌ Score engine failed: {e}")
        signal["score"] = 0
        signal["signal_strength"] = "Error"
        return signal
score_trade = score_signal
