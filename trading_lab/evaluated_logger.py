# evaluated_logger.py
import os
import pandas as pd
from datetime import timedelta

# Directorios
BASE_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_FILE = os.path.join(BASE_DIR, "data", "ETHUSDT_60.csv")

def evaluate_signals(log_file, data_df):
    print(f"\n🔍 Evaluando señales en: {log_file}")
    df_signals = pd.read_csv(log_file)

    # Normalizar fechas
    if "entry_time" not in df_signals.columns:
        print(f"[⚠️] El archivo {log_file} no contiene columna 'entry_time'. Omitido.")
        return

    df_data = data_df.copy()
    df_signals["entry_time"] = pd.to_datetime(df_signals["entry_time"])
    df_data["timestamp"] = pd.to_datetime(df_data["timestamp"], unit="s", errors="coerce")

    for idx, sig in df_signals.iterrows():
        if str(sig.get("verification_status", "")).lower() != "pending":
            continue

        start_time = sig["entry_time"]
        timeout_end = start_time + timedelta(minutes=int(sig["bars_timeout"]) * 60)

        df_future = df_data[(df_data["timestamp"] >= start_time) & (df_data["timestamp"] <= timeout_end)]

        if df_future.empty:
            print(f"[⚠️] No hay datos futuros para {sig['symbol']} en {start_time}")
            continue

        exit_price = None
        result = "timeout"

        for _, row in df_future.iterrows():
            if sig["side"].upper() == "LONG":
                if row["high"] >= sig["tp"]:
                    exit_price = sig["tp"]
                    result = "win"
                    break
                elif row["low"] <= sig["sl"]:
                    exit_price = sig["sl"]
                    result = "loss"
                    break
            else:  # SHORT
                if row["low"] <= sig["tp"]:
                    exit_price = sig["tp"]
                    result = "win"
                    break
                elif row["high"] >= sig["sl"]:
                    exit_price = sig["sl"]
                    result = "loss"
                    break

        if exit_price is None:
            exit_price = df_future.iloc[-1]["close"]

        return_pct = ((exit_price - sig["entry_price"]) / sig["entry_price"]) * 100
        if sig["side"].upper() == "SHORT":
            return_pct *= -1

        df_signals.at[idx, "exit_time"] = timeout_end.strftime("%Y-%m-%d %H:%M:%S")
        df_signals.at[idx, "exit_price"] = round(exit_price, 6)
        df_signals.at[idx, "result"] = result
        df_signals.at[idx, "return_pct"] = round(return_pct, 2)
        df_signals.at[idx, "verification_status"] = "verified"

        print(f"[✔] Señal #{idx} → {result.upper()} ({return_pct:.2f}%)")

    df_signals.to_csv(log_file, index=False)
    print(f"✅ Señales verificadas y guardadas en {log_file}")


if __name__ == "__main__":
    if not os.path.exists(DATA_FILE):
        print(f"[❌] No se encontró {DATA_FILE}")
        exit()

    df_data = pd.read_csv(DATA_FILE)
    for f in os.listdir(LOGS_DIR):
        if f.endswith(".csv"):
            evaluate_signals(os.path.join(LOGS_DIR, f), df_data)
