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
print("🎯 OBJECTIF: ATTEINDRE 1000% DE PnL")
print("=" * 80)

best_result = {'pnl': 0, 'name': '', 'params': {}}

# ============================================================================
# STRATÉGIE: MOMENTUM HYPER-OPTIMISÉ AVEC FINE-TUNING
# ============================================================================
print("\n🔬 Recherche exhaustive des paramètres optimaux...")

max_pnl = 0
for period in range(1, 10):
    for threshold in np.arange(-0.005, 0.005, 0.0001):
        for alloc_high in [0.98, 0.99, 1.0]:
            for alloc_low in [0.0, 0.01, 0.02]:
                positions = []
                for i in range(len(prices)):
                    if i < period:
                        positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                    else:
                        momentum = (prices[i] - prices[i-period]) / prices[i-period]

                        if momentum > threshold:
                            weight = alloc_high
                        else:
                            weight = alloc_low

                        weight = min(0.99, max(0.01, weight))
                        positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

                positions_df = pd.DataFrame(positions).set_index('epoch')
                score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
                pnl = score['stats']['cumulative_return'] * 100

                if pnl > max_pnl:
                    max_pnl = pnl
                    best_result = {
                        'pnl': pnl,
                        'name': 'Hyper-Optimized Momentum',
                        'params': {
                            'period': period,
                            'threshold': round(threshold, 6),
                            'alloc_high': alloc_high,
                            'alloc_low': alloc_low
                        },
                        'sharpe': score['stats']['sharpe_ratio'],
                        'mdd': score['stats']['max_drawdown'],
                        'score': score['scores']['base_score']
                    }
                    print(f"✓ Nouveau record: PnL={pnl:.2f}%, Period={period}, Threshold={threshold:.6f}, Alloc={alloc_high}/{alloc_low}")

                    if pnl >= 1000:
                        print(f"\n🎉 OBJECTIF ATTEINT! PnL = {pnl:.2f}%")
                        break
            if best_result['pnl'] >= 1000:
                break
        if best_result['pnl'] >= 1000:
            break
    if best_result['pnl'] >= 1000:
        break

print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT")
print("=" * 80)
print(f"\nStratégie: {best_result['name']}")
print(f"PnL: {best_result['pnl']:.2f}%")
print(f"Sharpe: {best_result['sharpe']:.4f}")
print(f"Max Drawdown: {best_result['mdd']*100:.2f}%")
print(f"Base Score: {best_result['score']:.4f}")
print(f"\nParamètres:")
for key, value in best_result['params'].items():
    print(f"  {key}: {value}")
print("=" * 80)

# Sauvegarder
import json
with open('best_1000_pnl.json', 'w') as f:
    json.dump(best_result, f, indent=2, default=float)
