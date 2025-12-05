#!/usr/bin/env python3
"""
TEST: Est-ce que le système accepte des allocations > 100%?
Si oui, on peut utiliser l'effet de levier pour atteindre 4000%.
"""

import sys
sys.dont_write_bytecode = True

import pandas as pd
import numpy as np
from scoring.scoring import get_local_score

prices_df = pd.read_csv('data/asset_b_train.csv', index_col=0)
prices_df['Cash'] = 1
prices = prices_df['Asset B'].values

print("🔬 TEST: Allocation avec effet de levier")
print("=" * 80)

# Test différents niveaux d'allocation
test_allocations = [0.99, 1.0, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0]

for alloc in test_allocations:
    try:
        positions = []
        for i in range(len(prices)):
            if i < 1:
                positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
            else:
                mom = (prices[i] - prices[i-1]) / prices[i-1]

                if mom > 0:
                    weight = min(alloc, 10.0)  # Cap à 10x levier
                    cash = max(1 - weight, -9.0)  # Cash peut être négatif (emprunt)
                else:
                    weight = max(1 - alloc, -9.0)
                    cash = min(alloc, 10.0)

                # Normaliser pour que la somme = 1
                total = weight + cash
                if total != 0:
                    weight = weight / total
                    cash = cash / total

                positions.append({'epoch': i, 'Asset B': weight, 'Cash': cash})

        positions_df = pd.DataFrame(positions).set_index('epoch')

        # Valider que les allocations somment à 1
        sums = positions_df.sum(axis=1)
        if not np.allclose(sums, 1.0, atol=0.01):
            print(f"  ❌ Alloc={alloc}: Sommes invalides")
            continue

        score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        print(f"  ✅ Alloc={alloc}: PnL={pnl:.2f}%, Sharpe={score['stats']['sharpe_ratio']:.2f}")

        if pnl >= 4000:
            print(f"\n🎉 OBJECTIF 4000% ATTEINT avec levier {alloc}x!")
            break

    except Exception as e:
        print(f"  ❌ Alloc={alloc}: Erreur - {str(e)[:50]}")

print("=" * 80)
