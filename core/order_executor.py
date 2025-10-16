import logging
log = logging.getLogger(__name__)

MAX_RISK_PCT = 0.12
MIN_RISK_PCT = 0.01

def calculate_position_size(balance: float, price: float, score: float) -> float:
    if score <= 0: return 0.0
    risk_fraction = max(MIN_RISK_PCT, min((score / 10) * MAX_RISK_PCT, MAX_RISK_PCT))
    risk_amount = balance * risk_fraction
    size = risk_amount / price
    log.info(f"[SizeScaling] Score={score} → Risk={risk_fraction:.2%}, Size={size:.5f}")
    return round(size, 5)

def execute_order(api, pair, side, price, score, tp, sl, balance):
    size = calculate_position_size(balance, price, score)
    if size <= 0:
        log.warning(f"[OrderExecutor] Skipping {pair} — score too low ({score}).")
        return None
    try:
        log.info(f"📈 Executing {side.upper()} {pair} | Size={size} | TP={tp} | SL={sl}")
        order = api.place_order(pair=pair, side=side, size=size, tp=tp, sl=sl)
        return order
    except Exception as e:
        log.error(f"❌ Order execution failed for {pair}: {e}")
        return None
