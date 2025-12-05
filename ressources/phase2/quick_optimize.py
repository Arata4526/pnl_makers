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

print("🔍 Optimisation rapide autour des meilleurs paramètres (666% PnL)")
print("=" * 80)

best_pnl = 666.27
best_params = None

# Test autour de period=3, threshold=-0.001
for period in [1, 2, 3, 4]:
    for threshold in np.linspace(-0.003, 0.002, 50):
        for use_gradient in [False, True]:
            positions = []
            for i in range(len(prices)):
                if i < max(period, 2):
                    positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                else:
                    momentum = (prices[i] - prices[i-period]) / prices[i-period]

                    # Option: ajouter un gradient (tendance de la tendance)
                    if use_gradient and i >= period + 1:
                        prev_momentum = (prices[i-1] - prices[i-period-1]) / prices[i-period-1]
                        gradient = momentum - prev_momentum

                        if momentum > threshold:
                            # Momentum positif
                            if gradient > 0:
                                weight = 0.99  # Accélération
                            else:
                                weight = 0.95  # Décélération
                        else:
                            # Momentum négatif
                            if gradient < 0:
                                weight = 0.01  # Accélération baissière
                            else:
                                weight = 0.05  # Décélération baissière
                    else:
                        # Simple momentum
                        weight = 0.99 if momentum > threshold else 0.01

                    positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

            positions_df = pd.DataFrame(positions).set_index('epoch')
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best_pnl:
                best_pnl = pnl
                best_params = {
                    'period': period,
                    'threshold': threshold,
                    'use_gradient': use_gradient,
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown']
                }
                print(f"✓ PnL={pnl:.2f}%, P={period}, T={threshold:.5f}, Gradient={use_gradient}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT")
print("=" * 80)
if best_params:
    print(f"PnL: {best_pnl:.2f}%")
    print(f"Paramètres: {best_params}")
else:
    print("Aucune amélioration trouvée")
print("=" * 80)
