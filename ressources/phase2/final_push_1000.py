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

print("🚀 DERNIÈRE TENTATIVE POUR ATTEINDRE 1000% PnL")
print("=" * 80)
print("Stratégie: Test de variations très fines + allocations variables")
print("=" * 80)

best = {'pnl': 763.89}

# Test 1: Variations très fines du threshold autour de 0.000061
print("\n📊 Phase 1: Fine-tuning du threshold...")
for threshold in np.linspace(0.00001, 0.0002, 500):
    positions = []
    for i in range(len(prices)):
        if i < 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            momentum = (prices[i] - prices[i-1]) / prices[i-1]
            weight = 0.99 if momentum > threshold else 0.01
            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    positions_df = pd.DataFrame(positions).set_index('epoch')
    try:
        score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        if pnl > best['pnl']:
            best = {'pnl': pnl, 'type': 'Simple', 'threshold': threshold, 'sharpe': score['stats']['sharpe_ratio'], 'mdd': score['stats']['max_drawdown']}
            print(f"  ✓ PnL={pnl:.2f}%, Threshold={threshold:.7f}, Sharpe={score['stats']['sharpe_ratio']:.2f}")
    except:
        pass

# Test 2: Allocation progressive basée sur la force du momentum
print("\n📊 Phase 2: Allocation progressive...")
for threshold in np.linspace(0.00001, 0.0002, 100):
    for strength_factor in [50, 75, 100, 150, 200]:
        positions = []
        for i in range(len(prices)):
            if i < 1:
                positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
            else:
                momentum = (prices[i] - prices[i-1]) / prices[i-1]

                # Allocation progressive basée sur la force
                if momentum > threshold:
                    # Plus le momentum est fort, plus on alloue
                    strength = min(1.0, abs(momentum) * strength_factor)
                    weight = 0.5 + 0.49 * strength  # Entre 0.5 et 0.99
                else:
                    strength = min(1.0, abs(momentum) * strength_factor)
                    weight = 0.5 - 0.49 * strength  # Entre 0.01 et 0.5

                positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

        positions_df = pd.DataFrame(positions).set_index('epoch')
        try:
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best['pnl']:
                best = {'pnl': pnl, 'type': 'Progressive', 'threshold': threshold, 'strength_factor': strength_factor, 'sharpe': score['stats']['sharpe_ratio'], 'mdd': score['stats']['max_drawdown']}
                print(f"  ✓ PnL={pnl:.2f}%, T={threshold:.7f}, Factor={strength_factor}, Sharpe={score['stats']['sharpe_ratio']:.2f}")
        except:
            pass

# Test 3: Double condition (momentum + accélération)
print("\n📊 Phase 3: Double condition (momentum + accélération)...")
for mom_threshold in np.linspace(0.00001, 0.0002, 100):
    for accel_weight in [0.1, 0.2, 0.3, 0.4, 0.5]:
        positions = []
        for i in range(len(prices)):
            if i < 2:
                positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
            else:
                # Momentum
                momentum = (prices[i] - prices[i-1]) / prices[i-1]
                prev_momentum = (prices[i-1] - prices[i-2]) / prices[i-2]
                # Accélération
                acceleration = momentum - prev_momentum

                # Signal combiné
                if momentum > mom_threshold and acceleration > 0:
                    weight = 0.99  # Momentum positif ET accélération
                elif momentum > mom_threshold:
                    weight = 0.85  # Momentum positif seul
                elif momentum < -mom_threshold and acceleration < 0:
                    weight = 0.01  # Momentum négatif ET décélération
                elif momentum < -mom_threshold:
                    weight = 0.15  # Momentum négatif seul
                else:
                    weight = 0.5  # Zone neutre

                positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

        positions_df = pd.DataFrame(positions).set_index('epoch')
        try:
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best['pnl']:
                best = {'pnl': pnl, 'type': 'Double', 'mom_threshold': mom_threshold, 'accel_weight': accel_weight, 'sharpe': score['stats']['sharpe_ratio'], 'mdd': score['stats']['max_drawdown']}
                print(f"  ✓ PnL={pnl:.2f}%, MomT={mom_threshold:.7f}, AccelW={accel_weight}, Sharpe={score['stats']['sharpe_ratio']:.2f}")
        except:
            pass

print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT FINAL")
print("=" * 80)
for key, value in best.items():
    print(f"{key}: {value}")

if best['pnl'] >= 1000:
    print("\n🎉🎉🎉 OBJECTIF 1000% ATTEINT! 🎉🎉🎉")
else:
    print(f"\n📊 Maximum atteignable: {best['pnl']:.2f}%")
    print(f"Écart à l'objectif: {1000 - best['pnl']:.2f}%")

print("=" * 80)

# Sauvegarder
import json
with open('final_best_result.json', 'w') as f:
    json.dump(best, f, indent=2, default=float)
