#!/usr/bin/env python3
"""
STRATÉGIES ULTRA-AGRESSIVES POUR 4000% PnL
===========================================
Approches innovantes et agressives pour maximiser le PnL.
"""

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
print("🚀 STRATÉGIES ULTRA-AGRESSIVES - OBJECTIF 4000%")
print("=" * 80)

best = {'pnl': 737.69}  # Baseline actuelle

# ============================================================================
# STRATÉGIE 1: THRESHOLD ULTRA-FIN (recherche exhaustive)
# ============================================================================
print("\n🔬 Phase 1: Recherche threshold ultra-fin (0 à 0.0001)")

for threshold in np.linspace(-0.0001, 0.0001, 1000):
    positions = []
    for i in range(len(prices)):
        if i < 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            mom = (prices[i] - prices[i-1]) / prices[i-1]
            weight = 0.99 if mom > threshold else 0.01
            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    positions_df = pd.DataFrame(positions).set_index('epoch')
    try:
        score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        if pnl > best['pnl']:
            best = {
                'pnl': pnl,
                'name': 'Ultra-Fine Threshold',
                'threshold': threshold,
                'sharpe': score['stats']['sharpe_ratio'],
                'mdd': score['stats']['max_drawdown']
            }
            print(f"  ✓ PnL={pnl:.2f}%, Threshold={threshold:.10f}, Sharpe={score['stats']['sharpe_ratio']:.2f}")
    except:
        pass

# ============================================================================
# STRATÉGIE 2: PREDICT NEXT MOVE (Pattern Recognition)
# ============================================================================
print("\n🔬 Phase 2: Pattern Recognition - Predict Next Move")

def pattern_recognition(lookback=3):
    """Analyse les patterns récurrents pour prédire le prochain mouvement"""
    positions = []

    for i in range(len(prices)):
        if i < lookback + 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Pattern actuel (séquence de mouvements)
            current_pattern = []
            for j in range(1, lookback + 1):
                move = 1 if prices[i - j + 1] > prices[i - j] else -1
                current_pattern.append(move)

            # Chercher ce pattern dans l'historique
            pattern_outcomes = []
            for k in range(lookback + 1, i):
                historical_pattern = []
                for j in range(1, lookback + 1):
                    move = 1 if prices[k - j + 1] > prices[k - j] else -1
                    historical_pattern.append(move)

                if historical_pattern == current_pattern:
                    # Pattern trouvé! Quel était le mouvement suivant?
                    next_move = 1 if prices[k + 1] > prices[k] else -1
                    pattern_outcomes.append(next_move)

            # Prédiction basée sur les occurrences historiques
            if len(pattern_outcomes) > 0:
                avg_outcome = np.mean(pattern_outcomes)
                if avg_outcome > 0.3:
                    weight = 0.99
                elif avg_outcome < -0.3:
                    weight = 0.01
                else:
                    weight = 0.5
            else:
                # Pas de pattern trouvé: fallback sur momentum
                mom = (prices[i] - prices[i-1]) / prices[i-1]
                weight = 0.99 if mom > 0 else 0.01

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

for lookback in [2, 3, 4, 5]:
    positions = pattern_recognition(lookback)
    score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
    pnl = score['stats']['cumulative_return'] * 100

    if pnl > best['pnl']:
        best = {
            'pnl': pnl,
            'name': 'Pattern Recognition',
            'lookback': lookback,
            'sharpe': score['stats']['sharpe_ratio'],
            'mdd': score['stats']['max_drawdown']
        }
        print(f"  ✓ Pattern: PnL={pnl:.2f}%, Lookback={lookback}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 3: MOMENTUM COMPOUNDING (Position accrue sur tendances)
# ============================================================================
print("\n🔬 Phase 3: Momentum Compounding")

def momentum_compounding():
    """Augmente exponentiellement la position sur tendances persistantes"""
    positions = []
    consecutive_wins = 0
    last_direction = 0

    for i in range(len(prices)):
        if i < 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
            last_direction = 0
        else:
            mom = (prices[i] - prices[i-1]) / prices[i-1]
            current_direction = 1 if mom > 0 else -1

            # Compte les mouvements consécutifs dans la même direction
            if current_direction == last_direction:
                consecutive_wins += 1
            else:
                consecutive_wins = 1
                last_direction = current_direction

            # Plus la streak est longue, plus on alloue (compounding)
            base_weight = 0.99 if current_direction > 0 else 0.01

            # Bonus pour streaks (max +0% = on reste à 99% ou 1%)
            # On garde l'allocation maximale
            weight = base_weight

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

positions = momentum_compounding()
score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
pnl = score['stats']['cumulative_return'] * 100

if pnl > best['pnl']:
    best = {
        'pnl': pnl,
        'name': 'Momentum Compounding',
        'sharpe': score['stats']['sharpe_ratio'],
        'mdd': score['stats']['max_drawdown']
    }
    print(f"  ✓ Compounding: PnL={pnl:.2f}%, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 4: MICRO-TREND FOLLOWING (Suivi de micro-tendances)
# ============================================================================
print("\n🔬 Phase 4: Micro-Trend Following")

def micro_trend_following(window=3):
    """Détecte et suit les micro-tendances"""
    positions = []

    for i in range(len(prices)):
        if i < window:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Compte le nombre de mouvements haussiers vs baissiers
            ups = 0
            downs = 0
            for j in range(window):
                if prices[i - j] > prices[i - j - 1]:
                    ups += 1
                else:
                    downs += 1

            # Forte tendance = beaucoup de mouvements dans une direction
            if ups > downs:
                strength = ups / window
                weight = 0.5 + 0.49 * strength
            else:
                strength = downs / window
                weight = 0.5 - 0.49 * strength

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

for window in [2, 3, 4, 5, 7, 10]:
    positions = micro_trend_following(window)
    score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
    pnl = score['stats']['cumulative_return'] * 100

    if pnl > best['pnl']:
        best = {
            'pnl': pnl,
            'name': 'Micro-Trend Following',
            'window': window,
            'sharpe': score['stats']['sharpe_ratio'],
            'mdd': score['stats']['max_drawdown']
        }
        print(f"  ✓ MicroTrend: PnL={pnl:.2f}%, Window={window}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 5: ZERO THRESHOLD (Aucun filtre - 100% réactif)
# ============================================================================
print("\n🔬 Phase 5: Zero Threshold - Pure Momentum")

def zero_threshold():
    """Réaction instantanée à TOUT mouvement, même infinitésimal"""
    positions = []

    for i in range(len(prices)):
        if i < 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Aucun threshold - réaction immédiate
            if prices[i] >= prices[i-1]:  # >= pour capturer égalité aussi
                weight = 0.99
            else:
                weight = 0.01

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

positions = zero_threshold()
score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
pnl = score['stats']['cumulative_return'] * 100

if pnl > best['pnl']:
    best = {
        'pnl': pnl,
        'name': 'Zero Threshold',
        'sharpe': score['stats']['sharpe_ratio'],
        'mdd': score['stats']['max_drawdown']
    }
    print(f"  ✓ ZeroThreshold: PnL={pnl:.2f}%, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 6: MOMENTUM + PRICE LEVEL (Combine momentum et niveaux de prix)
# ============================================================================
print("\n🔬 Phase 6: Momentum + Price Level")

def momentum_price_level():
    """Combine momentum avec la position du prix par rapport à ses niveaux"""
    positions = []

    for i in range(len(prices)):
        if i < 20:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Momentum
            mom = (prices[i] - prices[i-1]) / prices[i-1]

            # Niveau du prix (par rapport à min/max récent)
            recent_prices = prices[max(0, i-20):i+1]
            price_min = np.min(recent_prices)
            price_max = np.max(recent_prices)
            price_range = price_max - price_min

            if price_range > 0:
                price_position = (prices[i] - price_min) / price_range
            else:
                price_position = 0.5

            # Si momentum positif ET prix pas au top: acheter
            # Si momentum négatif ET prix pas au bottom: vendre
            if mom > 0:
                # Plus le prix est bas, plus on peut gagner
                potential = 1 - price_position
                weight = 0.5 + 0.49 * min(1, 0.5 + potential)
            else:
                # Plus le prix est haut, plus on peut shorter
                potential = price_position
                weight = 0.5 - 0.49 * min(1, 0.5 + potential)

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

positions = momentum_price_level()
score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
pnl = score['stats']['cumulative_return'] * 100

if pnl > best['pnl']:
    best = {
        'pnl': pnl,
        'name': 'Momentum + Price Level',
        'sharpe': score['stats']['sharpe_ratio'],
        'mdd': score['stats']['max_drawdown']
    }
    print(f"  ✓ MomPrice: PnL={pnl:.2f}%, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# AFFICHER LE MEILLEUR
# ============================================================================
print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT ULTRA-AGRESSIF")
print("=" * 80)
for key, value in best.items():
    print(f"{key}: {value}")

if best['pnl'] >= 4000:
    print("\n🎉🎉🎉 OBJECTIF 4000% ATTEINT! 🎉🎉🎉")
else:
    print(f"\n📊 Progression: {best['pnl']:.2f}% / 4000% ({best['pnl']/40:.1f}%)")
print("=" * 80)

# Sauvegarder
import json
with open('ultra_aggressive_best.json', 'w') as f:
    json.dump(best, f, indent=2, default=float)
