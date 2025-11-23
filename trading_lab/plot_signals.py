# plot_signals.py

import pandas as pd
import matplotlib.pyplot as plt

# CONFIGURACIÓN
DATA_PATH = "data/BTCUSD_Daily_OHLC.csv"  # o BTCUSD_1.csv si estás usando la de 1m
TRADES_PATH = "last_trades.csv"  # temporal, exportado desde engine

def load_price_data(path):
    df = pd.read_csv(path)
    df.columns = [col.lower() for col in df.columns]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s" if "1.csv" in path else "ns")
    df.set_index("timestamp", inplace=True)
    return df

def load_trades(path):
    return pd.read_csv(path, parse_dates=["entry_time"])

def plot_signals(df, trades):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df["close"], label="Precio", alpha=0.5)
    plt.plot(df.index, df["arima_pred"], label="Predicción ARIMA", linestyle="--", alpha=0.8)

    # Entradas y salidas
    for _, trade in trades.iterrows():
        entry_time = trade["entry_time"]
        exit_price = trade["exit_price"]
        entry_price = trade["entry_price"]
        result = trade["result"]

        color = "green" if result == "win" else "red" if result == "loss" else "gray"
        plt.scatter(entry_time, entry_price, color=color, marker="^", label="Entrada" if _ == 0 else "", zorder=3)
        plt.axhline(exit_price, color=color, linestyle=":", alpha=0.5)

    plt.title("Señales + Predicción ARIMA")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    df = load_price_data(DATA_PATH)
    trades = load_trades(TRADES_PATH)
    plot_signals(df, trades)

if __name__ == "__main__":
    main()
