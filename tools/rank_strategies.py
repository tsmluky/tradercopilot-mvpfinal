
import pandas as pd
import sys

def rank_strategies():
    file_path = "benchmark_results_20251212_184511.csv"
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"No se encontró el archivo: {file_path}")
        return

    # Filtrar solo las exitosas
    df = df[df['status'] == 'SUCCESS'].copy()
    
    # Asegurar tipos numéricos
    df['roi_pct'] = pd.to_numeric(df['roi_pct'], errors='coerce')
    df['win_rate'] = pd.to_numeric(df['win_rate'], errors='coerce')
    df['total_trades'] = pd.to_numeric(df['total_trades'], errors='coerce')

    # Filtros de Calidad:
    # 1. Al menos 10 operaciones (para tener significancia estadística mínima)
    # 2. ROI positivo
    qualified = df[
        (df['total_trades'] >= 10) & 
        (df['roi_pct'] > 0)
    ].copy()

    # Ordenar por ROI descendente
    top_performers = qualified.sort_values(by='roi_pct', ascending=False).head(15)

    print("\n🏆 TOP 15 ESTRATEGIAS RENTABLES (Base: 180 días) 🏆")
    print("=" * 80)
    print(f"{'Estrategia':<20} | {'Token':<6} | {'TF':<4} | {'ROI %':<8} | {'Win Rate':<8} | {'Trades':<6}")
    print("-" * 80)
    
    for _, row in top_performers.iterrows():
        print(f"{row['strategy']:<20} | {row['token']:<6} | {row['timeframe']:<4} | {row['roi_pct']:>6.2f}% | {row['win_rate']:>6.1f}% | {row['total_trades']:<6}")
    
    print("=" * 80)
    
    # Ver las peores
    worst_performers = qualified.sort_values(by='roi_pct', ascending=True).head(5)
    # print("\n📉 PEORES (Pero con ganancia):")
    # for _, row in worst_performers.iterrows():
    #     print(f"{row['strategy']} {row['token']} {row['timeframe']}: {row['roi_pct']}%")

if __name__ == "__main__":
    rank_strategies()
