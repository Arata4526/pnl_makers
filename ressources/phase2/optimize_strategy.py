#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True

import pandas as pd
import numpy as np
from scoring.scoring import get_local_score
from itertools import product

# Charger les données
prices_df = pd.read_csv('data/asset_b_train.csv', index_col=0)
prices_df['Cash'] = 1
prices = prices_df['Asset B'].values

print("=" * 80)
print("🔬 OPTIMISATION AVANCÉE DE LA STRATÉGIE")
print("=" * 80)
print(f"Objectif: Atteindre 1000% de PnL")
print("=" * 80)

best_result = {
    'pnl': 0,
    'score': 0,
    'params': None,
    'positions': None
}

# ============================================================================
# STRATÉGIE 1: OPTIMISATION DES PARAMÈTRES TRIPLE MOMENTUM
# ============================================================================
print("\n🔍 Phase 1: Optimisation des paramètres Triple Momentum")

param_grid = {
    'short': [3, 4, 5, 6, 7],
    'medium': [8, 10, 12, 15],
    'long': [18, 20, 25, 30],
    'weight_short': [0.4, 0.5, 0.6, 0.7],
    'weight_medium': [0.2, 0.3, 0.4],
    'threshold_high': [0.005, 0.01, 0.015, 0.02],
    'allocation_high': [0.85, 0.90, 0.95, 0.98],
    'allocation_low': [0.05, 0.10, 0.15, 0.20],
}

test_count = 0
for short, medium, long in product(param_grid['short'], param_grid['medium'], param_grid['long']):
    if short >= medium or medium >= long:
        continue

    for w_s, w_m in product(param_grid['weight_short'], param_grid['weight_medium']):
        w_l = 1.0 - w_s - w_m
        if w_l < 0.1 or w_l > 0.5:
            continue

        for th_high, alloc_high, alloc_low in product(
            param_grid['threshold_high'],
            param_grid['allocation_high'],
            param_grid['allocation_low']
        ):
            test_count += 1

            positions = []
            for i in range(len(prices)):
                if i < long:
                    positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                else:
                    mom_s = (prices[i] - prices[i-short]) / prices[i-short] if i >= short else 0
                    mom_m = (prices[i] - prices[i-medium]) / prices[i-medium] if i >= medium else 0
                    mom_l = (prices[i] - prices[i-long]) / prices[i-long] if i >= long else 0

                    momentum_score = w_s * mom_s + w_m * mom_m + w_l * mom_l

                    if momentum_score > th_high:
                        weight = alloc_high
                    elif momentum_score > 0:
                        weight = 0.7
                    elif momentum_score > -th_high:
                        weight = 0.3
                    else:
                        weight = alloc_low

                    positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

            positions_df = pd.DataFrame(positions).set_index('epoch')
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)

            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best_result['pnl']:
                best_result = {
                    'pnl': pnl,
                    'score': score['scores']['base_score'],
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown'],
                    'params': {
                        'type': 'Triple Momentum Optimized',
                        'short': short,
                        'medium': medium,
                        'long': long,
                        'weight_short': w_s,
                        'weight_medium': w_m,
                        'weight_long': w_l,
                        'threshold_high': th_high,
                        'allocation_high': alloc_high,
                        'allocation_low': alloc_low,
                    },
                    'positions': positions_df
                }
                print(f"  ✓ Nouveau meilleur: PnL={pnl:.2f}%, Sharpe={score['stats']['sharpe_ratio']:.2f}, Params={short}/{medium}/{long}, W={w_s:.1f}/{w_m:.1f}/{w_l:.1f}")

print(f"\nTests effectués: {test_count}")

# ============================================================================
# STRATÉGIE 2: MOMENTUM AVEC EFFET DE LEVIER DYNAMIQUE
# ============================================================================
print("\n🔍 Phase 2: Momentum avec rebalancement agressif")

for leverage_factor in [1.5, 2.0, 2.5, 3.0]:
    for mom_period in [3, 4, 5, 6, 7]:
        for threshold in [0.005, 0.01, 0.015]:
            positions = []
            for i in range(len(prices)):
                if i < mom_period:
                    positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                else:
                    momentum = (prices[i] - prices[i-mom_period]) / prices[i-mom_period]

                    if abs(momentum) > threshold:
                        # Signal fort: allocation agressive
                        base_weight = 0.95 if momentum > 0 else 0.05
                    else:
                        # Signal faible: allocation modérée
                        base_weight = 0.7 if momentum > 0 else 0.3

                    # Clip pour éviter le levier (max 0.99)
                    weight = min(0.99, max(0.01, base_weight))

                    positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

            positions_df = pd.DataFrame(positions).set_index('epoch')
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best_result['pnl']:
                best_result = {
                    'pnl': pnl,
                    'score': score['scores']['base_score'],
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown'],
                    'params': {
                        'type': 'Aggressive Momentum',
                        'momentum_period': mom_period,
                        'threshold': threshold,
                        'leverage_factor': leverage_factor,
                    },
                    'positions': positions_df
                }
                print(f"  ✓ Nouveau meilleur: PnL={pnl:.2f}%, Period={mom_period}, Threshold={threshold}")

# ============================================================================
# STRATÉGIE 3: MULTI-TIMEFRAME AVEC TREND FOLLOWING
# ============================================================================
print("\n🔍 Phase 3: Multi-timeframe trend following")

for fast, slow in [(2, 8), (3, 10), (4, 12), (5, 15), (3, 20)]:
    for trend_period in [20, 30, 40, 50]:
        for aggressive_alloc in [0.95, 0.97, 0.98, 0.99]:
            positions = []
            ma_fast = pd.Series(prices).rolling(window=fast).mean().values
            ma_slow = pd.Series(prices).rolling(window=slow).mean().values
            ma_trend = pd.Series(prices).rolling(window=trend_period).mean().values

            for i in range(len(prices)):
                if i < trend_period or np.isnan(ma_fast[i]) or np.isnan(ma_slow[i]) or np.isnan(ma_trend[i]):
                    positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                else:
                    # Signal de tendance
                    trend_up = prices[i] > ma_trend[i]
                    # Signal de momentum
                    momentum_up = ma_fast[i] > ma_slow[i]

                    # Double confirmation
                    if trend_up and momentum_up:
                        weight = aggressive_alloc
                    elif not trend_up and not momentum_up:
                        weight = 1 - aggressive_alloc
                    else:
                        weight = 0.5

                    positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

            positions_df = pd.DataFrame(positions).set_index('epoch')
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best_result['pnl']:
                best_result = {
                    'pnl': pnl,
                    'score': score['scores']['base_score'],
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown'],
                    'params': {
                        'type': 'Multi-Timeframe Trend',
                        'fast': fast,
                        'slow': slow,
                        'trend_period': trend_period,
                        'aggressive_alloc': aggressive_alloc,
                    },
                    'positions': positions_df
                }
                print(f"  ✓ Nouveau meilleur: PnL={pnl:.2f}%, Fast/Slow={fast}/{slow}, Trend={trend_period}")

# ============================================================================
# STRATÉGIE 4: MOMENTUM EXPONENTIEL PONDÉRÉ
# ============================================================================
print("\n🔍 Phase 4: Momentum exponentiel pondéré")

for lookback in [3, 4, 5, 6, 7, 8]:
    for alpha in [0.3, 0.4, 0.5, 0.6, 0.7]:
        for max_alloc in [0.95, 0.97, 0.98, 0.99]:
            positions = []
            ema = pd.Series(prices).ewm(alpha=alpha).mean().values

            for i in range(len(prices)):
                if i < lookback or np.isnan(ema[i]):
                    positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
                else:
                    # Momentum basé sur EMA
                    ema_momentum = (prices[i] - ema[i]) / ema[i]
                    # Momentum récent
                    recent_momentum = (prices[i] - prices[i-lookback]) / prices[i-lookback]

                    # Combinaison
                    combined_momentum = 0.6 * recent_momentum + 0.4 * ema_momentum

                    if combined_momentum > 0.015:
                        weight = max_alloc
                    elif combined_momentum > 0.005:
                        weight = 0.8
                    elif combined_momentum > 0:
                        weight = 0.6
                    elif combined_momentum > -0.005:
                        weight = 0.4
                    elif combined_momentum > -0.015:
                        weight = 0.2
                    else:
                        weight = 1 - max_alloc

                    positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

            positions_df = pd.DataFrame(positions).set_index('epoch')
            score = get_local_score(prices=prices_df, positions=positions_df, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best_result['pnl']:
                best_result = {
                    'pnl': pnl,
                    'score': score['scores']['base_score'],
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown'],
                    'params': {
                        'type': 'EMA Momentum',
                        'lookback': lookback,
                        'alpha': alpha,
                        'max_alloc': max_alloc,
                    },
                    'positions': positions_df
                }
                print(f"  ✓ Nouveau meilleur: PnL={pnl:.2f}%, Lookback={lookback}, Alpha={alpha:.2f}")

# ============================================================================
# AFFICHER LE MEILLEUR RÉSULTAT
# ============================================================================
print("\n" + "=" * 80)
print("🏆 MEILLEUR RÉSULTAT TROUVÉ")
print("=" * 80)
print(f"\nStratégie: {best_result['params']['type']}")
print(f"PnL: {best_result['pnl']:.2f}%")
print(f"Sharpe: {best_result['sharpe']:.4f}")
print(f"Max Drawdown: {best_result['mdd']*100:.2f}%")
print(f"Base Score: {best_result['score']:.4f}")
print(f"\nParamètres:")
for key, value in best_result['params'].items():
    if key != 'type':
        print(f"  {key}: {value}")

print("\n" + "=" * 80)

# Sauvegarder les meilleurs paramètres
import json
with open('best_params.json', 'w') as f:
    json.dump(best_result['params'], f, indent=2)

print("✓ Meilleurs paramètres sauvegardés dans best_params.json")
