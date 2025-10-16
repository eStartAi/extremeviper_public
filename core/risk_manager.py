import logging
from datetime import datetime, timedelta
log = logging.getLogger(__name__)

MAX_TRADES_PER_HOUR = 25
COOLDOWN_SECS = 180
MAX_CONSECUTIVE_LOSSES = 3
MAX_DAILY_DRAWDOWN_PCT = 0.10

_trade_log, _last_trade_time = [], {}
_consecutive_losses = 0
_daily_start_balance = None
_last_balance = None

def init_daily_balance(balance):
    global _daily_start_balance, _last_balance, _consecutive_losses
    if _daily_start_balance is None:
        _daily_start_balance = balance
        _last_balance = balance
        _consecutive_losses = 0
        log.info(f"[RiskManager] Daily baseline set at {balance:.2f}")

def can_trade():
    now = datetime.utcnow()
    window = now - timedelta(hours=1)
    recent = [t for t in _trade_log if t > window]
    if len(recent) >= MAX_TRADES_PER_HOUR:
        log.warning(f"[Throttle] Max {MAX_TRADES_PER_HOUR}/hour reached.")
        return False
    _trade_log.append(now)
    return True

def can_trade_pair(pair):
    now = datetime.utcnow()
    if pair in _last_trade_time:
        delta = (now - _last_trade_time[pair]).total_seconds()
        if delta < COOLDOWN_SECS:
            log.warning(f"[Cooldown] {pair} cooling down ({int(delta)}s/{COOLDOWN_SECS}s).")
            return False
    _last_trade_time[pair] = now
    return True

def record_trade_result(balance, previous_balance):
    global _consecutive_losses, _last_balance
    if previous_balance is None: _last_balance = balance; return
    if balance < previous_balance: _consecutive_losses += 1
    else: _consecutive_losses = 0
    _last_balance = balance
    if _consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
        log.error(f"🛑 Trading paused — {_consecutive_losses} consecutive losses.")
        return False
    return True

def check_daily_drawdown(balance):
    if not _daily_start_balance: return True
    drawdown = 1 - (balance / _daily_start_balance)
    if drawdown >= MAX_DAILY_DRAWDOWN_PCT:
        log.error(f"🛑 Max daily drawdown reached ({drawdown:.2%}). Trading disabled.")
        return False
    return True
