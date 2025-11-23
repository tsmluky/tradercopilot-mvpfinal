# backend/test_api_live.py
"""
Script para probar la API de estrategias en vivo.
Ejecutar con el backend corriendo.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print("🧪 Testing Strategy API - Live")
print("="*60)

# Test 1: Listar estrategias
print("\n[1/5] GET /strategies/")
print("-" * 40)
response = requests.get(f"{BASE_URL}/strategies/")
if response.status_code == 200:
    strategies = response.json()
    print(f"✅ Found {len(strategies)} strategies:")
    for s in strategies:
        print(f"  - {s['id']}: {s['name']}")
        print(f"    Enabled: {s['enabled']}, Signals: {s['total_signals']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test 2: Ver detalles de una estrategia
print("\n[2/5] GET /strategies/rsi_macd_divergence_v1")
print("-" * 40)
response = requests.get(f"{BASE_URL}/strategies/rsi_macd_divergence_v1")
if response.status_code == 200:
    details = response.json()
    print(f"✅ Strategy details:")
    print(f"  Name: {details['metadata']['name']}")
    print(f"  Version: {details['metadata']['version']}")
    print(f"  Universe: {details['metadata']['universe']}")
    print(f"  Risk: {details['metadata']['risk_profile']}")
    print(f"  Stats: {details['stats']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test 3: Activar estrategia
print("\n[3/5] PATCH /strategies/rsi_macd_divergence_v1")
print("-" * 40)
update_data = {
    "enabled": True,
    "interval_seconds": 60,
    "tokens": ["ETH", "BTC", "SOL"],
    "timeframes": ["1h"],
    "config": {
        "rsi_period": 14,
        "min_confidence": 0.65
    }
}
response = requests.patch(
    f"{BASE_URL}/strategies/rsi_macd_divergence_v1",
    json=update_data
)
if response.status_code == 200:
    print(f"✅ Strategy activated:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test 4: Verificar que se activó
print("\n[4/5] GET /strategies/ (verificar cambios)")
print("-" * 40)
response = requests.get(f"{BASE_URL}/strategies/")
if response.status_code == 200:
    strategies = response.json()
    for s in strategies:
        if s['id'] == 'rsi_macd_divergence_v1':
            print(f"✅ Strategy status:")
            print(f"  Enabled: {s['enabled']}")
            print(f"  Tokens: {len(strategies[0])} configured")
else:
    print(f"❌ Error: {response.status_code}")

# Test 5: Ejecutar manualmente
print("\n[5/5] POST /strategies/rsi_macd_divergence_v1/execute")
print("-" * 40)
execute_data = {
    "tokens": ["ETH"],
    "timeframe": "1h",
    "context": {}
}
response = requests.post(
    f"{BASE_URL}/strategies/rsi_macd_divergence_v1/execute",
    json=execute_data
)
if response.status_code == 200:
    result = response.json()
    print(f"✅ Execution result:")
    print(f"  Status: {result['status']}")
    print(f"  Signals generated: {result['signals_generated']}")
    if result['signals_generated'] > 0:
        print(f"  Signals:")
        for sig in result['signals']:
            print(f"    - {sig['token']} {sig['direction']} @ {sig['entry']}")
    else:
        print("  (No signals generated - example strategy)")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print("\n" + "="*60)
print("✅ API Testing Complete!")
print("="*60)
