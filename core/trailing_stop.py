def update_trailing_stop(entry_price, current_price, trail_pct=0.02, direction="buy"):
    if direction == "buy":
        trigger = entry_price * (1 + trail_pct)
        return max(trigger, current_price - (current_price * trail_pct))
    else:
        trigger = entry_price * (1 - trail_pct)
        return min(trigger, current_price + (current_price * trail_pct))
