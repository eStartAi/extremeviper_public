from tabulate import tabulate

def display_signal_table(signal_rows: list):
    """
    Display signal data as a formatted table.
    Each row = [BROKER, PAIR, SCORE, THRESH, LOT SIZE, ACTION]
    """
    headers = ["BROKER", "PAIR", "SCORE", "THRESH", "LOT SIZE", "ACTION"]
    print("\n" + tabulate(signal_rows, headers=headers, tablefmt="rounded_grid") + "\n")
