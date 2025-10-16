def execute_trade(signal: dict, score: float, broker: str = None):
    """
    Executes a trade with fallback support if the primary broker fails.
    """
    pair = signal["pair"]
    price = signal["price"]
    side = signal["side"]
    sl = signal.get("sl")
    tp = signal.get("tp")

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    lot_size = calculate_lot_size(score, price)

    primary = broker or os.getenv("PRIMARY_BROKER", "oanda")
    fallback = os.getenv("FALLBACK_BROKER", "kraken")

    def log_and_return(status, msg, data={}):
        logging.info(f"[{ts}] {msg}")
        return {"status": status, **data}

    if DRY_RUN:
        return log_and_return("dry_run", f"💤 DRYRUN: {side.upper()} {lot_size} lot {pair} via {primary}")

    def try_oanda():
        units = int(lot_size * 1000)
        if side.lower() == "sell":
            units *= -1
        data = {
            "order": {
                "instrument": pair.replace("/", "_"),
                "units": str(units),
                "type": "MARKET",
                "positionFill": "DEFAULT",
            }
        }
        if sl:
            data["order"]["stopLossOnFill"] = {"price": str(sl)}
        if tp:
            data["order"]["takeProfitOnFill"] = {"price": str(tp)}
        try:
            r = OrderCreate(accountID=OANDA_ACCOUNT_ID, data=data)
            oanda_api.request(r)
            return log_and_return("sent", f"✅ OANDA {side.upper()} {lot_size} lot {pair}", {"broker": "oanda"})
        except Exception as e:
            return log_and_return("fail", f"OANDA ERROR: {e}", {"reason": str(e)})

    def try_kraken():
        try:
            kr_pair = pair.replace("/", "")
            response = kraken_api.query_private('AddOrder', {
                'pair': kr_pair,
                'type': side.lower(),
                'ordertype': 'market',
                'volume': str(lot_size)
            })
            return log_and_return("sent", f"✅ Kraken {side.upper()} {lot_size} lot {pair}", {"broker": "kraken"})
        except Exception as e:
            return log_and_return("fail", f"KRAKEN ERROR: {e}", {"reason": str(e)})

    # === Try Primary Broker ===
    if primary == "oanda":
        result = try_oanda()
    elif primary == "kraken":
        result = try_kraken()
    else:
        return log_and_return("error", f"❌ Unsupported broker: {primary}", {"reason": "unsupported"})

    # === Fallback if failed ===
    if result["status"] == "fail" and fallback and fallback != primary:
        logging.warning(f"⚠️ Primary broker {primary} failed — retrying with fallback broker {fallback}")
        if fallback == "oanda":
            return try_oanda()
        elif fallback == "kraken":
            return try_kraken()
        else:
            return log_and_return("fail", f"❌ Fallback broker '{fallback}' unsupported.")

    return result
