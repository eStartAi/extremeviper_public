# utils/position_sizer.py

import os

def get_size_pct_from_score(score: float) -> float:
    """Map score to percentage of max lot size."""
    if score < 5:
        return 0.0
    elif score < 6.1:
        return 0.5
    elif score < 7.6:
        return 0.75
    else:
        return 1.0

def calculate_lot_size(score: float, price: float) -> float:
    """
    Returns lot size based on score and risk.
    """
    balance = float(os.getenv("ACCOUNT_BALANCE", 300))
    risk_pct = float(os.getenv("RISK_PCT", 0.12))
    leverage = float(os.getenv("LEVERAGE", 20))
    min_lot = float(os.getenv("MIN_LOT_SIZE", 0.01))
    max_lot = float(os.getenv("MAX_LOT_SIZE", 1.0))

    size_pct = get_size_pct_from_score(score)

    # Effective capital based on risk and leverage
    capital_to_use = balance * risk_pct * leverage
    raw_lot = capital_to_use / price

    adjusted_lot = raw_lot * size_pct
    final_lot = max(min_lot, min(adjusted_lot, max_lot))
    return round(final_lot, 2)
