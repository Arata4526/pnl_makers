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

print("🎯 Ultra-fine tuning autour de threshold=0.00005, period=1")
print("=" * 80)

best = {'pnl': 762.24}

# Recherche très fine
for threshold in np.linspace(-0.0005, 0.0015, 2000):
    for high_alloc in np.linspace(0.97, 1.0, 30):
        for low_alloc in np.linspace(0.0, 0.03, 30):
            if high_alloc + low_alloc > 1.0:
                continue

            positions = []
            for i in range(len(prices)):
                if i < 1:
                    positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                else:
                    momentum = (prices[i] - prices[i-1]) / prices[i-1]
                    weight = high_alloc if momentum > threshold else low_alloc
                    weight = min(0.99, max(0.01, weight))
                    positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

            positions_df = pd.DataFrame(positions).set_index('epoch')
            try:
                score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
                pnl = score['stats']['cumulative_return'] * 100

                if pnl > best['pnl']:
                    best = {
                        'pnl': pnl,
                        'threshold': threshold,
                        'high_alloc': high_alloc,
                        'low_alloc': low_alloc,
                        'sharpe': score['stats']['sharpe_ratio'],
                        'mdd': score['stats']['max_drawdown'],
                        'base_score': score['scores']['base_score']
                    }
                    print(f"✓ PnL={pnl:.2f}%, T={threshold:.6f}, H={high_alloc:.4f}, L={low_alloc:.4f}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

                    if pnl >= 1000:
                        print(f"\n🎉 OBJECTIF 1000% ATTEINT!")
                        break
            except:
                pass

        if best['pnl'] >= 1000:
            break
    if best['pnl'] >= 1000:
        break

print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT")
print("=" * 80)
for key, value in best.items():
    print(f"{key}: {value}")
print("=" * 80)

# Sauvegarder
import json
with open('ultra_fine_result.json', 'w') as f:
    json.dump(best, f, indent=2, default=float)
