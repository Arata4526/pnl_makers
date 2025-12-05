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

print("🎯 Test ultra-réactif avec période 1 et 2")
print("=" * 80)

best = {'pnl': 0}

# Test exhaustif pour période 1 et 2
for period in [1, 2]:
    print(f"\n📊 Test avec période = {period}")
    for threshold in np.linspace(-0.01, 0.01, 200):
        positions = []
        for i in range(len(prices)):
            if i < period:
                positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
            else:
                momentum = (prices[i] - prices[i-period]) / prices[i-period]
                weight = 0.99 if momentum > threshold else 0.01
                positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

        positions_df = pd.DataFrame(positions).set_index('epoch')
        try:
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best['pnl']:
                best = {
                    'pnl': pnl,
                    'period': period,
                    'threshold': threshold,
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown'],
                    'base_score': score['scores']['base_score']
                }
                print(f"  ✓ PnL={pnl:.2f}%, Threshold={threshold:.6f}, Sharpe={score['stats']['sharpe_ratio']:.2f}, MDD={score['stats']['max_drawdown']*100:.1f}%")
        except:
            pass

print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT")
print("=" * 80)
print(f"PnL: {best['pnl']:.2f}%")
print(f"Period: {best['period']}")
print(f"Threshold: {best['threshold']:.6f}")
print(f"Sharpe: {best['sharpe']:.4f}")
print(f"Max Drawdown: {best['mdd']*100:.2f}%")
print(f"Base Score: {best['base_score']:.4f}")
print("=" * 80)

if best['pnl'] >= 1000:
    print("\n🎉 OBJECTIF 1000% ATTEINT!")

# Sauvegarder
import json
with open('best_period_1_2.json', 'w') as f:
    json.dump(best, f, indent=2, default=float)
