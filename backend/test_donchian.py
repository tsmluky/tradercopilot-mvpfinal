"""
TEST DIRECTO - Donchian V2
===========================
Ejecuta la estrategia una vez para verificar que funciona.
"""

from strategies.DonchianBreakoutV2 import DonchianBreakoutV2

print("=" * 60)
print("🧪 TEST DIRECTO - DONCHIAN V2")
print("=" * 60)

# Crear instancia de la estrategia
strategy = DonchianBreakoutV2()

# Tokens a analizar
tokens = ["ETH", "BTC", "SOL"]
timeframe = "1h"

print(f"\n📊 Analizando {len(tokens)} tokens en timeframe {timeframe}...")
print(f"Tokens: {', '.join(tokens)}\n")

# Generar señales
try:
    signals = strategy.generate_signals(tokens, timeframe)
    
    print(f"\n{'=' * 60}")
    print(f"✅ RESULTADO: {len(signals)} señales generadas")
    print(f"{'=' * 60}\n")
    
    if signals:
        for sig in signals:
            print(f"📈 {sig.token} {sig.direction.upper()}")
            print(f"   Entry: ${sig.entry:.2f}")
            print(f"   TP: ${sig.tp:.2f}")
            print(f"   SL: ${sig.sl:.2f}")
            print(f"   Confidence: {sig.confidence:.0%}")
            print(f"   Rationale: {sig.rationale}")
            print()
    else:
        print("ℹ️  No hay setups válidos en este momento.")
        print("   Esto es normal - la estrategia solo genera señales cuando:")
        print("   • Precio rompe Donchian Upper/Lower Band")
        print("   • ATR > Media ATR (volatilidad alta)")
        print("   • Precio alineado con EMA200 (tendencia)")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'=' * 60}")
