#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True

import pandas as pd
import numpy as np
from scoring.scoring import get_local_score

# Charger les données
prices_df = pd.read_csv('data/asset_b_train.csv', index_col=0)
prices_df['Cash'] = 1
prices = prices_df['Asset B'].values

print("=" * 80)
print("🚀 TEST DE STRATÉGIES ULTRA-AGRESSIVES")
print("=" * 80)

best_result = {'pnl': 0, 'name': '', 'params': {}}

# ============================================================================
# STRATÉGIE 1: MOMENTUM ULTRA-COURT TERME
# ============================================================================
def strategy_ultra_short_momentum(period=3, threshold=0.0):
    positions = []
    for i in range(len(prices)):
        if i < period:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            momentum = (prices[i] - prices[i-period]) / prices[i-period]

            if momentum > threshold:
                weight = 0.99
            else:
                weight = 0.01

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

for period in [2, 3, 4]:
    for threshold in [-0.001, 0.0, 0.001, 0.002]:
        positions = strategy_ultra_short_momentum(period, threshold)
        score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        if pnl > best_result['pnl']:
            best_result = {
                'pnl': pnl,
                'name': 'Ultra Short Momentum',
                'params': {'period': period, 'threshold': threshold},
                'sharpe': score['stats']['sharpe_ratio'],
                'mdd': score['stats']['max_drawdown'],
                'score': score['scores']['base_score']
            }
            print(f"✓ Ultra Short Momentum: PnL={pnl:.2f}%, Period={period}, Threshold={threshold}")

# ============================================================================
# STRATÉGIE 2: DOUBLE MOMENTUM AVEC CONFIRMATIO N
# ============================================================================
def strategy_double_momentum_confirm(fast=2, slow=5):
    positions = []
    for i in range(len(prices)):
        if i < slow:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            mom_fast = (prices[i] - prices[i-fast]) / prices[i-fast]
            mom_slow = (prices[i] - prices[i-slow]) / prices[i-slow]

            # Les deux momentum doivent être alignés
            if mom_fast > 0 and mom_slow > 0:
                weight = 0.99
            elif mom_fast < 0 and mom_slow < 0:
                weight = 0.01
            else:
                # Signaux contradictoires: suivre le plus récent
                weight = 0.8 if mom_fast > 0 else 0.2

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

for fast in [2, 3]:
    for slow in [5, 6, 7, 8]:
        if fast >= slow:
            continue
        positions = strategy_double_momentum_confirm(fast, slow)
        score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        if pnl > best_result['pnl']:
            best_result = {
                'pnl': pnl,
                'name': 'Double Momentum Confirm',
                'params': {'fast': fast, 'slow': slow},
                'sharpe': score['stats']['sharpe_ratio'],
                'mdd': score['stats']['max_drawdown'],
                'score': score['scores']['base_score']
            }
            print(f"✓ Double Momentum: PnL={pnl:.2f}%, Fast={fast}, Slow={slow}")

# ============================================================================
# STRATÉGIE 3: ACCELERATION MOMENTUM
# ============================================================================
def strategy_acceleration_momentum(period=3):
    positions = []
    for i in range(len(prices)):
        if i < period + 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Momentum actuel
            mom_current = (prices[i] - prices[i-period]) / prices[i-period]
            # Momentum précédent
            mom_previous = (prices[i-1] - prices[i-period-1]) / prices[i-period-1]
            # Accélération
            acceleration = mom_current - mom_previous

            if acceleration > 0 and mom_current > 0:
                weight = 0.99  # Accélération positive
            elif acceleration < 0 and mom_current < 0:
                weight = 0.01  # Accélération négative
            elif mom_current > 0:
                weight = 0.7
            else:
                weight = 0.3

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

for period in [2, 3, 4, 5]:
    positions = strategy_acceleration_momentum(period)
    score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
    pnl = score['stats']['cumulative_return'] * 100

    if pnl > best_result['pnl']:
        best_result = {
            'pnl': pnl,
            'name': 'Acceleration Momentum',
            'params': {'period': period},
            'sharpe': score['stats']['sharpe_ratio'],
            'mdd': score['stats']['max_drawdown'],
            'score': score['scores']['base_score']
        }
        print(f"✓ Acceleration: PnL={pnl:.2f}%, Period={period}")

# ============================================================================
# STRATÉGIE 4: MOMENTUM MULTI-NIVEAU
# ============================================================================
def strategy_multilevel_momentum(p1=2, p2=4, p3=7):
    positions = []
    for i in range(len(prices)):
        if i < p3:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            m1 = (prices[i] - prices[i-p1]) / prices[i-p1] if i >= p1 else 0
            m2 = (prices[i] - prices[i-p2]) / prices[i-p2] if i >= p2 else 0
            m3 = (prices[i] - prices[i-p3]) / prices[i-p3] if i >= p3 else 0

            # Compter les signaux positifs
            positive_signals = sum([m1 > 0, m2 > 0, m3 > 0])

            if positive_signals == 3:
                weight = 0.99
            elif positive_signals == 2:
                weight = 0.75
            elif positive_signals == 1:
                weight = 0.25
            else:
                weight = 0.01

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

for p1 in [2, 3]:
    for p2 in [4, 5, 6]:
        for p3 in [7, 8, 10]:
            if p1 >= p2 or p2 >= p3:
                continue
            positions = strategy_multilevel_momentum(p1, p2, p3)
            score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best_result['pnl']:
                best_result = {
                    'pnl': pnl,
                    'name': 'Multilevel Momentum',
                    'params': {'p1': p1, 'p2': p2, 'p3': p3},
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown'],
                    'score': score['scores']['base_score']
                }
                print(f"✓ Multilevel: PnL={pnl:.2f}%, Periods={p1}/{p2}/{p3}")

# ============================================================================
# STRATÉGIE 5: TREND STRENGTH avec allocation exponentielle
# ============================================================================
def strategy_trend_strength(period=5, min_alloc=0.05, max_alloc=0.98):
    positions = []
    for i in range(len(prices)):
        if i < period:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Force de la tendance
            momentum = (prices[i] - prices[i-period]) / prices[i-period]

            # Allocation exponentielle basée sur la force du momentum
            if momentum > 0:
                # Fonction sigmoïde pour allocation progressive
                strength = abs(momentum) * 100  # Normaliser
                weight = min_alloc + (max_alloc - min_alloc) * (1 / (1 + np.exp(-10 * (strength - 0.5))))
            else:
                strength = abs(momentum) * 100
                weight = max_alloc - (max_alloc - min_alloc) * (1 / (1 + np.exp(-10 * (strength - 0.5))))

            weight = np.clip(weight, min_alloc, max_alloc)
            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

for period in [3, 4, 5, 6]:
    for max_alloc in [0.95, 0.97, 0.98, 0.99]:
        positions = strategy_trend_strength(period, 0.01, max_alloc)
        score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        if pnl > best_result['pnl']:
            best_result = {
                'pnl': pnl,
                'name': 'Trend Strength',
                'params': {'period': period, 'max_alloc': max_alloc},
                'sharpe': score['stats']['sharpe_ratio'],
                'mdd': score['stats']['max_drawdown'],
                'score': score['scores']['base_score']
            }
            print(f"✓ Trend Strength: PnL={pnl:.2f}%, Period={period}, MaxAlloc={max_alloc}")

# ============================================================================
# AFFICHER LE MEILLEUR
# ============================================================================
print("\n" + "=" * 80)
print("🏆 MEILLEURE STRATÉGIE ULTRA-AGRESSIVE")
print("=" * 80)
print(f"\nStratégie: {best_result['name']}")
print(f"PnL: {best_result['pnl']:.2f}%")
print(f"Sharpe: {best_result['sharpe']:.4f}")
print(f"Max Drawdown: {best_result['mdd']*100:.2f}%")
print(f"Base Score: {best_result['score']:.4f}")
print(f"\nParamètres: {best_result['params']}")
print("=" * 80)

# Sauvegarder
import json
with open('best_ultra_aggressive.json', 'w') as f:
    json.dump(best_result, f, indent=2)
