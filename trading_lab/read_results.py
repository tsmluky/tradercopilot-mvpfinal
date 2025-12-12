import pandas as pd
import glob

print("\n📊 RESULTADOS DE BACKTEST (Simulación Jesse Logic)\n")
for f in glob.glob("backtest_results_*.csv"):
    try:
        df = pd.read_csv(f)
        if df.empty:
            continue
        
        wins = df[df["outcome"] == "WIN"]
        winrate = len(wins) / len(df) * 100
        total_pnl = df["pnl"].sum() * 100
        avg_pnl = df["pnl"].mean() * 100
        
        name = f.replace("backtest_results_", "").replace(".csv", "")
        
        print(f"Strategy: {name}")
        print(f"  Trades: {len(df)}")
        print(f"  Win Rate: {winrate:.2f}%")
        print(f"  Total PnL: {total_pnl:.2f}%")
        print(f"  Avg PnL: {avg_pnl:.2f}%")
        print("-" * 30)
    except Exception as e:
        print(f"Error reading {f}: {e}")
