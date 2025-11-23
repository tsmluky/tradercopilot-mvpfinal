# plot_performance.py
# Genera PNGs de equity y drawdown por símbolo/TF con los CSV generados.
import os
import argparse
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

RESULTS_DIR = "results"
PLOTS_DIR   = "results/plots"

def list_equity_files(symbol: str, timeframe: str, run_id: str=None):
    pattern = f"equity_{symbol}_*_{timeframe}.csv"
    base = os.path.join(RESULTS_DIR, run_id) if run_id else RESULTS_DIR
    return sorted(glob.glob(os.path.join(base, pattern)))

def plot_equities(files, out_path, title):
    plt.figure()
    for f in files:
        df = pd.read_csv(f)
        label = os.path.basename(f).replace(".csv","").replace("equity_","")
        plt.plot(df["trade_idx"], df["equity"], label=label)
    plt.title(title)
    plt.xlabel("Trade #")
    plt.ylabel("Equity (× inicial)")
    plt.legend()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close()

def plot_drawdown(log_file, out_path, title):
    df = pd.read_csv(log_file)
    eq = (1.0 + (df["return_pct_net"].fillna(0.0)/100.0)).cumprod()
    roll_max = eq.cummax()
    dd = (eq/roll_max) - 1.0
    plt.figure()
    plt.plot(np.arange(len(dd)), dd*100.0)
    plt.title(title)
    plt.xlabel("Trade #")
    plt.ylabel("Drawdown (%)")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--timeframe", required=True)
    ap.add_argument("--run_id", default=None, help="ej: run_20250812_161000 (opcional)")
    ap.add_argument("--strategy_for_dd", default=None, help="nombre exacto para drawdown (ej: MA_10x50_tp1.5_sl1.0)")
    args = ap.parse_args()

    files = list_equity_files(args.symbol, args.timeframe, args.run_id)
    if not files:
        raise SystemExit("No hay equity CSVs para ese filtro.")

    run_dir = args.run_id if args.run_id else "latest"
    out_equity = os.path.join(PLOTS_DIR, run_dir, f"equity_{args.symbol}_{args.timeframe}.png")
    plot_equities(files, out_equity, f"Equity curves — {args.symbol} @ {args.timeframe}")

    if args.strategy_for_dd:
        # buscar el CSV de logs
        logs_base = "logs"
        logs_dir = os.path.join(logs_base, args.run_id) if args.run_id else logs_base
        log_file = os.path.join(logs_dir, f"{args.symbol}_{args.strategy_for_dd}_{args.timeframe}.csv")
        if os.path.exists(log_file):
            out_dd = os.path.join(PLOTS_DIR, run_dir, f"drawdown_{args.symbol}_{args.strategy_for_dd}_{args.timeframe}.png")
            plot_drawdown(log_file, out_dd, f"Drawdown — {args.symbol} @ {args.timeframe} — {args.strategy_for_dd}")
        else:
            print(f"[plot] No se encontró {log_file} para drawdown.")
    print(f"[plot] Listo. Imágenes en {os.path.join(PLOTS_DIR, run_dir)}")

if __name__ == "__main__":
    main()
