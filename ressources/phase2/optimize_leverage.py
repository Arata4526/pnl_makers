#!/usr/bin/env python3
"""
OPTIMISATION DU LEVIER POUR MAXIMISER LE PnL
=============================================
Trouve le niveau de levier optimal et la meilleure stratégie.
"""

import sys
sys.dont_write_bytecode = True

import pandas as pd
import numpy as np
from scoring.scoring import get_local_score

prices_df = pd.read_csv('data/asset_b_train.csv', index_col=0)
prices_df['Cash'] = 1
prices = prices_df['Asset B'].values

print("=" * 80)
print("🚀 OPTIMISATION DU LEVIER - OBJECTIF: MAXIMISER LE PnL")
print("=" * 80)

best = {'pnl': 0}

# ============================================================================
# TEST 1: Levier optimal avec momentum simple
# ============================================================================
print("\n📊 Phase 1: Optimisation du levier (momentum ultra-court)")

for leverage in np.linspace(1.0, 3.0, 100):
    for threshold in np.linspace(-0.0001, 0.0001, 50):
        positions = []

        for i in range(len(prices)):
            if i < 1:
                positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
            else:
                mom = (prices[i] - prices[i-1]) / prices[i-1]

                if mom > threshold:
                    # Haussier: allouer avec levier
                    weight_asset = min(leverage, 10.0)
                    weight_cash = 1 - weight_asset
                else:
                    # Baissier: position défensive
                    weight_asset = max(1 - leverage, -9.0)
                    weight_cash = 1 - weight_asset

                positions.append({'epoch': i, 'Asset B': weight_asset, 'Cash': weight_cash})

        positions_df = pd.DataFrame(positions).set_index('epoch')

        try:
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best['pnl']:
                best = {
                    'pnl': pnl,
                    'strategy': 'Leveraged Momentum',
                    'leverage': leverage,
                    'threshold': threshold,
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown']
                }
                print(f"  ✓ PnL={pnl:.2f}%, Leverage={leverage:.2f}x, Threshold={threshold:.7f}, Sharpe={score['stats']['sharpe_ratio']:.2f}, MDD={score['stats']['max_drawdown']*100:.1f}%")
        except:
            pass

# ============================================================================
# TEST 2: Levier adaptatif basé sur la volatilité
# ============================================================================
print("\n📊 Phase 2: Levier adaptatif (volatilité)")

for max_leverage in [1.5, 2.0, 2.5, 3.0, 4.0]:
    for vol_window in [10, 20, 30]:
        positions = []
        returns = np.diff(prices) / prices[:-1]

        for i in range(len(prices)):
            if i < vol_window:
                positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
            else:
                mom = (prices[i] - prices[i-1]) / prices[i-1]

                # Volatilité récente
                recent_rets = returns[max(0, i-vol_window):i]
                current_vol = np.std(recent_rets)
                avg_vol = np.std(returns[:i])

                # Levier inversement proportionnel à la volatilité
                # Plus la vol est basse, plus on leverage
                vol_ratio = current_vol / (avg_vol + 1e-10)
                adaptive_leverage = max_leverage / max(vol_ratio, 0.5)
                adaptive_leverage = min(adaptive_leverage, max_leverage)

                if mom > 0:
                    weight_asset = adaptive_leverage
                    weight_cash = 1 - weight_asset
                else:
                    weight_asset = 1 - adaptive_leverage
                    weight_cash = adaptive_leverage

                positions.append({'epoch': i, 'Asset B': weight_asset, 'Cash': weight_cash})

        positions_df = pd.DataFrame(positions).set_index('epoch')

        try:
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best['pnl']:
                best = {
                    'pnl': pnl,
                    'strategy': 'Adaptive Leverage',
                    'max_leverage': max_leverage,
                    'vol_window': vol_window,
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown']
                }
                print(f"  ✓ PnL={pnl:.2f}%, MaxLev={max_leverage}x, VolWin={vol_window}, Sharpe={score['stats']['sharpe_ratio']:.2f}")
        except:
            pass

# ============================================================================
# TEST 3: Levier avec confirmation (multi-timeframe)
# ============================================================================
print("\n📊 Phase 3: Levier avec confirmation multi-timeframe")

for base_leverage in [1.5, 2.0, 2.5, 3.0]:
    for fast in [1, 2]:
        for slow in [5, 7, 10]:
            if fast >= slow:
                continue

            positions = []

            for i in range(len(prices)):
                if i < slow:
                    positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                else:
                    mom_fast = (prices[i] - prices[i-fast]) / prices[i-fast]
                    mom_slow = (prices[i] - prices[i-slow]) / prices[i-slow]

                    # Double confirmation: utilise levier max
                    # Signal mixte: réduit le levier
                    if mom_fast > 0 and mom_slow > 0:
                        # Double haussier
                        leverage = base_leverage
                        weight_asset = leverage
                    elif mom_fast < 0 and mom_slow < 0:
                        # Double baissier
                        leverage = base_leverage
                        weight_asset = 1 - leverage
                    elif mom_fast > 0:
                        # Suivre le court terme mais avec levier réduit
                        leverage = base_leverage * 0.7
                        weight_asset = leverage
                    else:
                        leverage = base_leverage * 0.7
                        weight_asset = 1 - leverage

                    weight_cash = 1 - weight_asset
                    positions.append({'epoch': i, 'Asset B': weight_asset, 'Cash': weight_cash})

            positions_df = pd.DataFrame(positions).set_index('epoch')

            try:
                score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
                pnl = score['stats']['cumulative_return'] * 100

                if pnl > best['pnl']:
                    best = {
                        'pnl': pnl,
                        'strategy': 'Multi-Timeframe Leverage',
                        'base_leverage': base_leverage,
                        'fast': fast,
                        'slow': slow,
                        'sharpe': score['stats']['sharpe_ratio'],
                        'mdd': score['stats']['max_drawdown']
                    }
                    print(f"  ✓ PnL={pnl:.2f}%, BaseLev={base_leverage}x, Fast={fast}, Slow={slow}, Sharpe={score['stats']['sharpe_ratio']:.2f}")
            except:
                pass

# ============================================================================
# RÉSULTATS
# ============================================================================
print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT AVEC LEVIER")
print("=" * 80)
for key, value in best.items():
    print(f"{key}: {value}")

if best['pnl'] >= 4000:
    print(f"\n🎉 OBJECTIF 4000% LARGEMENT DÉPASSÉ!")
    print(f"Performance: {best['pnl']:.2f}% ({best['pnl']/40:.1f}% de l'objectif)")

print("=" * 80)

# Sauvegarder
import json
with open('optimal_leverage_strategy.json', 'w') as f:
    json.dump(best, f, indent=2, default=float)
