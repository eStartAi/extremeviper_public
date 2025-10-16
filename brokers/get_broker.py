from brokers import oanda, kraken, alpaca, tos

def get_broker(name):
    name = name.lower()
    if "oanda" in name:
        return oanda
    elif "kraken" in name:
        return kraken
    elif "alpaca" in name:
        return alpaca
    elif "tos" in name:
        return tos
    else:
        raise ValueError(f"Unknown broker: {name}")
