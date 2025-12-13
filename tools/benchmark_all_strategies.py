"""
Strategy Benchmark Suite - OPTIMIZED
- Incremental CSV saves (no data loss on crash)
- Data caching (download once, reuse)
- Progress tracking with resume capability
"""
import sys
import os
import time
import csv
import json
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.backtest_engine import BacktestEngine
from market_data_api import get_ohlcv_data

# ============= CONFIGURATION =============
# Edit these to customize your benchmark

# --- Set A: TREND FOLLOWING ---
# Names must match the MODULE name (filename) in backend/strategies/
TREND_STRATEGIES = ['donchian', 'DonchianBreakoutV2', 'ma_cross', 'supertrend_flow']
TREND_TOKENS = ['BTC', 'ETH', 'SOL', 'AVAX', 'BNB', 'ADA', 'XRP', 'DOGE', 'NEAR', 'ARB']
TREND_TIMEFRAMES = ['1h', '4h', '1d']

# --- Set B: MEAN REVERSION (Intraday focus) ---
REVERSION_STRATEGIES = ['bb_mean_reversion', 'rsi_divergence', 'vwap_intraday']
REVERSION_TOKENS = ['MATIC', 'LINK', 'DOT', 'UNI', 'LTC', 'SOL', 'ETH', 'AVAX', 'APE', 'RUNE']
REVERSION_TIMEFRAMES = ['5m', '15m', '30m', '1h']

DURATIONS = [45, 180] 
INITIAL_CAPITAL = 1000

# =========================================

# Data cache
DATA_CACHE = {}

def get_cached_data(token: str, timeframe: str, days: int) -> List[Dict]:
    """Get OHLCV data with caching to avoid re-downloading."""
    cache_key = f"{token}_{timeframe}_{days}"
    
    if cache_key not in DATA_CACHE:
        print(f"   📥 Downloading {token} {timeframe} {days}d data...", end=" ")
        start = time.time()
        
        # Calculate limit
        candles_per_day = {
            '5m': 288,
            '15m': 96, 
            '30m': 48,
            '1h': 24, 
            '4h': 6,
            '1d': 1
        }
        limit = days * candles_per_day.get(timeframe, 24)
        
        data = get_ohlcv_data(token, timeframe, limit=limit)
        DATA_CACHE[cache_key] = data
        
        print(f"✅ {len(data)} candles in {time.time() - start:.1f}s")
    
    return DATA_CACHE[cache_key]

def save_result_incremental(result: Dict, csv_path: str):
    """Append single result to CSV immediately."""
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=result.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

def get_existing_completed_tests(csv_path: str) -> set:
    """Read existing CSV to find completed tests."""
    completed_keys = set()
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Key: strategy|token|timeframe|days
                    key = f"{row['strategy']}|{row['token']}|{row['timeframe']}|{row['days']}"
                    # Only skip if it was SUCCESS or if we want to skip failed ones too?
                    # Let's retry failed ones, skip SUCCESS.
                    if row.get('status') == 'SUCCESS':
                        completed_keys.add(key)
        except Exception as e:
            print(f"⚠️ Error reading existing CSV: {e}")
    return completed_keys

def run_benchmark():
    """Run optimized benchmark with incremental saves."""
    
    print("=" * 80)
    print("🏆 STRATEGY BENCHMARK SUITE - OPTIMIZED")
    print("=" * 80)
    
    # Output file - reuse the latest one or create new?
    # User loop wants to "continue". We should probably search for the latest file or use a fixed one.
    # For now let's try to find the most recent benchmark file to resume or create new.
    # Actually, logic is cleaner if we just use one 'benchmark_results.csv' or the user-provided one.
    # But files are timestamped. Let's list and pick the newest.
    files = [f for f in os.listdir('.') if f.startswith('benchmark_results_') and f.endswith('.csv')]
    files.sort(reverse=True)
    
    if files:
        csv_path = files[0]
        print(f"📂 Found existing results file: {csv_path}")
        print(f"resume_mode: ON (Skipping entries marked SUCCESS)")
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = f'benchmark_results_{timestamp}.csv'
        print(f"🆕 Creating new results file: {csv_path}")

    existing_completed = get_existing_completed_tests(csv_path)
    print(f"⏭️  Already completed tests: {len(existing_completed)}")
    
    print(f"Trend Set: {len(TREND_STRATEGIES)} strats x {len(TREND_TOKENS)} tokens x {len(TREND_TIMEFRAMES)} TFs")
    print(f"Reversion Set: {len(REVERSION_STRATEGIES)} strats x {len(REVERSION_TOKENS)} tokens x {len(REVERSION_TIMEFRAMES)} TFs")
    
    # Calculate totals
    trend_tests = len(TREND_STRATEGIES) * len(TREND_TOKENS) * len(TREND_TIMEFRAMES) * len(DURATIONS)
    rev_tests = len(REVERSION_STRATEGIES) * len(REVERSION_TOKENS) * len(REVERSION_TIMEFRAMES) * len(DURATIONS)
    total_tests = trend_tests + rev_tests
    
    print(f"\nTotal Categorized Tests: {total_tests}")
    print("=" * 80)
    print()
    
    print(f"📊 Results will be saved to: {csv_path}")
    print(f"💾 Each test saves immediately (crash-safe!)\n")
    
    # Progress tracking
    completed = len(existing_completed)
    failed = 0
    results = [] # We might want to re-load results if we want a full summary at end
    
    # Pre-download all data
    print("=" * 80)
    print("📥 PRE-DOWNLOADING CACHE...")
    print("=" * 80)
    
    # Download Trend Data
    for token in TREND_TOKENS:
        for tf in TREND_TIMEFRAMES:
            for d in DURATIONS:
                get_cached_data(token, tf, d)

    # Download Reversion Data
    for token in REVERSION_TOKENS:
        for tf in REVERSION_TIMEFRAMES:
            for d in DURATIONS:
                get_cached_data(token, tf, d)
    
    print("\n✅ All data cached! Running Categorized Backtests...\n")
    print("=" * 80)
    
    # --- HELPER FUNCTION FOR RUNNING A SET ---
    def run_set(set_name, strats, tokens, tfs):
        nonlocal completed, failed
        print(f"\n🚀 STARTING {set_name} SET...")
        
        for strategy in strats:
            for token in tokens:
                for timeframe in tfs:
                    for days in DURATIONS:
                        
                        # SKIP IF COMPLETED
                        test_key = f"{strategy}|{token}|{timeframe}|{days}"
                        if test_key in existing_completed:
                            print(f"⏭️  Skipping {test_key} (Already SUCCESS)")
                            continue

                        completed += 1
                        
                        print(f"[{completed}/{total_tests}] {strategy} | {token} | {timeframe} | {days}d", end=" ... ")
                        
                        try:
                            start_time = time.time()
                            cached_data = get_cached_data(token, timeframe, days)
                            engine = BacktestEngine(initial_capital=INITIAL_CAPITAL)
                            
                            # Inject data
                            import pandas as pd
                            df = pd.DataFrame(cached_data)
                            
                            result = engine.run(
                                strategy_id=strategy,
                                symbol=token,
                                timeframe=timeframe,
                                days=days
                            )
                            
                            elapsed = time.time() - start_time
                            metrics = result['metrics']
                            
                            result_row = {
                                'timestamp': datetime.now().isoformat(),
                                'strategy': strategy,
                                'category': set_name, # Added category
                                'token': token,
                                'timeframe': timeframe,
                                'days': days,
                                'total_pnl': round(metrics['total_pnl'], 2),
                                'buy_hold_pnl': round(metrics['buy_hold_pnl'], 2),
                                'alpha': round(metrics['total_pnl'] - metrics['buy_hold_pnl'], 2),
                                'win_rate': round(metrics['win_rate'], 1),
                                'total_trades': metrics['total_trades'],
                                'best_trade': round(metrics['best_trade'], 2),
                                'worst_trade': round(metrics['worst_trade'], 2),
                                'final_capital': round(metrics['final_capital'], 2),
                                'roi_pct': round(((metrics['final_capital'] - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100, 2),
                                'elapsed_seconds': round(elapsed, 2),
                                'status': 'SUCCESS'
                            }
                            
                            save_result_incremental(result_row, csv_path)
                            results.append(result_row)
                            
                            pnl_color = "🟢" if metrics['total_pnl'] > 0 else "🔴"
                            print(f"{pnl_color} ${metrics['total_pnl']:.0f} | {metrics['total_trades']} trades | {elapsed:.1f}s")
                            
                        except Exception as e:
                            failed += 1
                            error_msg = str(e)[:50]
                            print(f"❌ {error_msg}")
                            
                            result_row = {
                                'timestamp': datetime.now().isoformat(),
                                'strategy': strategy,
                                'category': set_name,
                                'token': token,
                                'timeframe': timeframe,
                                'days': days,
                                'total_pnl': 0, 
                                'status': f'FAILED: {error_msg}'
                            }
                            save_result_incremental(result_row, csv_path)
                            results.append(result_row)

    # Run Sets
    run_set("TREND", TREND_STRATEGIES, TREND_TOKENS, TREND_TIMEFRAMES)
    run_set("REVERSION", REVERSION_STRATEGIES, REVERSION_TOKENS, REVERSION_TIMEFRAMES)
    
    print()
    print("=" * 80)
    print(f"✅ Completed: {completed - failed}/{total_tests}")
    print(f"❌ Failed: {failed}/{total_tests}")
    print(f"📊 Results saved to: {csv_path}")
    print("=" * 80)
    
    # Print top performers
    print_summary(results)
    
    return results

def print_summary(results: List[Dict]):
    """Print console summary of top performers."""
    
    print("\n" + "=" * 80)
    print("🏆 TOP 5 PERFORMERS")
    print("=" * 80)
    
    success_results = [r for r in results if r['status'] == 'SUCCESS']
    
    if success_results:
        sorted_by_pnl = sorted(success_results, key=lambda x: x['total_pnl'], reverse=True)[:5]
        
        print(f"\n{'Rank':<5} {'Strategy':<20} {'Token':<6} {'TF':<5} {'Days':<6} {'PnL':<10} {'Win%':<8} {'Trades'}")
        print("-" * 80)
        
        for i, r in enumerate(sorted_by_pnl, 1):
            print(f"{i:<5} {r['strategy']:<20} {r['token']:<6} {r['timeframe']:<5} {r['days']:<6} "
                  f"${r['total_pnl']:<9.2f} {r['win_rate']:<7.1f}% {r['total_trades']}")
        
        print("\n" + "=" * 80)
        
        # Best by token
        print("\n🪙 BEST STRATEGY PER TOKEN:")
        all_tokens = list(set(TREND_TOKENS + REVERSION_TOKENS))
        for token in all_tokens:
            token_results = [r for r in success_results if r['token'] == token]
            if token_results:
                best = max(token_results, key=lambda x: x['total_pnl'])
                print(f"  {token}: {best['strategy']} ({best['timeframe']}, {best['days']}d) → ${best['total_pnl']:.2f}")

if __name__ == "__main__":
    print("\n⚠️  Optimized version with:")
    print("   ✅ Incremental saves (crash-safe)")
    print("   ✅ Data caching (faster)")
    print("   ✅ Reduced combinations (quicker results)")
    print("\nPress Ctrl+C to cancel, or wait 3 seconds to start...\n")
    
    try:
        time.sleep(3)
        run_benchmark()
    except KeyboardInterrupt:
        print("\n\n❌ Benchmark cancelled by user.")
        sys.exit(0)
