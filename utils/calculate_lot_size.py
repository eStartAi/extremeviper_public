import os
import logging

logger = logging.getLogger(__name__)

def calculate_lot_size(signal: dict, score: float, balance: float = None):
    """
    Calculate position size based on confidence score and risk percentage.
    """
    price = signal.get("price", 1000)
    balance = balance or float(os.getenv("ACCOUNT_BALANCE", 1000))
    risk_pct = float(os.getenv("RISK_PCT", 0.02))  # 2%

    confidence = min(score / 10, 1.0)
    risk_cap = balance * risk_pct
    lot_size = (risk_cap * confidence) / price

    logger.info(f"📐 Calculated lot size: {lot_size:.4f} | Score={score:.2f} | Price={price}")
    return round(lot_size, 4)
