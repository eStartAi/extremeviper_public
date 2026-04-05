from brokers import oanda, kraken, alpaca, tos

def get_broker(name):
    name = name.lower()
    if name == "oanda":
        return oanda
    elif name == "kraken":
        return kraken
    elif name == "alpaca":
        return alpaca
    elif name in ["tos", "thinkorswim"]:
        return tos
    else:
        raise ValueError(f"Unsupported broker: {name}")
