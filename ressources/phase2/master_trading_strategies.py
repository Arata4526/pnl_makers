#!/usr/bin/env python3
"""
STRATÉGIES DE TRADING PROFESSIONNELLES - OBJECTIF 4000% PnL
================================================================
Implémentation des meilleures stratégies de trading utilisées
par les professionnels pour maximiser le PnL.
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
print("🔥 STRATÉGIES DE TRADING PROFESSIONNELLES")
print("=" * 80)
print("Objectif: 4000% PnL minimum")
print("=" * 80)

best_result = {'pnl': 0, 'name': '', 'params': {}}

# ============================================================================
# STRATÉGIE 1: KELLY CRITERION avec MOMENTUM
# ============================================================================
print("\n📊 Phase 1: Kelly Criterion Optimal Position Sizing")

def kelly_criterion_strategy(lookback=5, kelly_fraction=0.5):
    """Kelly Criterion pour dimensionnement optimal des positions"""
    positions = []
    returns = np.diff(prices) / prices[:-1]

    for i in range(len(prices)):
        if i < lookback + 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Momentum
            momentum = (prices[i] - prices[i-lookback]) / prices[i-lookback]

            # Estimation de la probabilité de gain (win rate historique)
            recent_returns = returns[max(0, i-lookback):i]
            win_rate = (recent_returns > 0).sum() / len(recent_returns)

            # Kelly Criterion: f = (p * b - q) / b
            # où p = win_rate, q = 1-p, b = ratio gain/perte moyen
            winning_returns = recent_returns[recent_returns > 0]
            losing_returns = recent_returns[recent_returns < 0]

            if len(winning_returns) > 0 and len(losing_returns) > 0:
                avg_win = np.mean(winning_returns)
                avg_loss = abs(np.mean(losing_returns))

                if avg_loss > 0:
                    b = avg_win / avg_loss
                    kelly_f = (win_rate * b - (1 - win_rate)) / b

                    # Fractional Kelly pour réduire le risque
                    kelly_f = kelly_f * kelly_fraction

                    # Direction basée sur le momentum
                    if momentum > 0 and kelly_f > 0:
                        weight = min(0.99, max(0.5, 0.5 + kelly_f))
                    elif momentum < 0 and kelly_f > 0:
                        weight = max(0.01, min(0.5, 0.5 - kelly_f))
                    else:
                        weight = 0.5
                else:
                    weight = 0.5
            else:
                weight = 0.5

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

for lookback in [3, 5, 7, 10]:
    for kelly_frac in [0.3, 0.5, 0.7, 1.0, 1.5]:
        positions = kelly_criterion_strategy(lookback, kelly_frac)
        score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        if pnl > best_result['pnl']:
            best_result = {
                'pnl': pnl,
                'name': 'Kelly Criterion',
                'params': {'lookback': lookback, 'kelly_fraction': kelly_frac},
                'sharpe': score['stats']['sharpe_ratio'],
                'mdd': score['stats']['max_drawdown']
            }
            print(f"  ✓ Kelly: PnL={pnl:.2f}%, Lookback={lookback}, Fraction={kelly_frac}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 2: VOLATILITY BREAKOUT
# ============================================================================
print("\n📊 Phase 2: Volatility Breakout Strategy")

def volatility_breakout(vol_period=20, breakout_std=1.5):
    """Entre agressivement sur les cassures de volatilité"""
    positions = []
    returns = np.diff(prices) / prices[:-1]

    for i in range(len(prices)):
        if i < vol_period:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Volatilité historique
            recent_returns = returns[max(0, i-vol_period):i]
            vol = np.std(recent_returns)
            mean_return = np.mean(recent_returns)

            # Return actuel
            current_return = returns[i-1] if i > 0 else 0

            # Breakout: mouvement > X écarts-types
            z_score = (current_return - mean_return) / (vol + 1e-10)

            if z_score > breakout_std:
                # Breakout haussier fort
                weight = 0.99
            elif z_score > breakout_std * 0.5:
                # Breakout haussier modéré
                weight = 0.85
            elif z_score < -breakout_std:
                # Breakout baissier fort
                weight = 0.01
            elif z_score < -breakout_std * 0.5:
                # Breakout baissier modéré
                weight = 0.15
            else:
                weight = 0.5

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

for vol_period in [10, 15, 20, 30]:
    for breakout_std in [0.5, 1.0, 1.5, 2.0]:
        positions = volatility_breakout(vol_period, breakout_std)
        score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
        pnl = score['stats']['cumulative_return'] * 100

        if pnl > best_result['pnl']:
            best_result = {
                'pnl': pnl,
                'name': 'Volatility Breakout',
                'params': {'vol_period': vol_period, 'breakout_std': breakout_std},
                'sharpe': score['stats']['sharpe_ratio'],
                'mdd': score['stats']['max_drawdown']
            }
            print(f"  ✓ VolBreakout: PnL={pnl:.2f}%, Period={vol_period}, Std={breakout_std}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 3: ADAPTIVE POSITION SIZING (Score de Conviction)
# ============================================================================
print("\n📊 Phase 3: Adaptive Position Sizing")

def adaptive_position_sizing(fast=2, slow=10, strength_multiplier=200):
    """Taille de position adaptée à la force du signal"""
    positions = []

    for i in range(len(prices)):
        if i < slow:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Momentum multi-timeframe
            mom_fast = (prices[i] - prices[i-fast]) / prices[i-fast]
            mom_slow = (prices[i] - prices[i-slow]) / prices[i-slow]

            # Score de conviction (les deux signaux s'alignent)
            if mom_fast > 0 and mom_slow > 0:
                # Double confirmation haussière
                conviction = min(abs(mom_fast) + abs(mom_slow), 0.02) * strength_multiplier
                weight = 0.5 + min(0.49, conviction)
            elif mom_fast < 0 and mom_slow < 0:
                # Double confirmation baissière
                conviction = min(abs(mom_fast) + abs(mom_slow), 0.02) * strength_multiplier
                weight = 0.5 - min(0.49, conviction)
            elif abs(mom_fast) > abs(mom_slow):
                # Suivre le signal le plus fort (court terme)
                weight = 0.99 if mom_fast > 0 else 0.01
            else:
                weight = 0.5

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

for fast in [1, 2, 3]:
    for slow in [5, 7, 10, 15]:
        for strength_mult in [100, 150, 200, 300]:
            if fast >= slow:
                continue
            positions = adaptive_position_sizing(fast, slow, strength_mult)
            score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
            pnl = score['stats']['cumulative_return'] * 100

            if pnl > best_result['pnl']:
                best_result = {
                    'pnl': pnl,
                    'name': 'Adaptive Position Sizing',
                    'params': {'fast': fast, 'slow': slow, 'strength_multiplier': strength_mult},
                    'sharpe': score['stats']['sharpe_ratio'],
                    'mdd': score['stats']['max_drawdown']
                }
                print(f"  ✓ Adaptive: PnL={pnl:.2f}%, Fast={fast}, Slow={slow}, Mult={strength_mult}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 4: MOMENTUM + ACCELERATION + VOLATILITY (Multi-Factor)
# ============================================================================
print("\n📊 Phase 4: Multi-Factor Strategy")

def multi_factor_strategy(period=3):
    """Combine momentum, accélération et volatilité"""
    positions = []
    returns = np.diff(prices) / prices[:-1]

    for i in range(len(prices)):
        if i < period + 10:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # 1. Momentum
            momentum = (prices[i] - prices[i-period]) / prices[i-period]

            # 2. Accélération (dérivée du momentum)
            prev_momentum = (prices[i-1] - prices[i-period-1]) / prices[i-period-1]
            acceleration = momentum - prev_momentum

            # 3. Volatilité récente
            recent_returns = returns[max(0, i-10):i]
            current_vol = np.std(recent_returns)
            avg_vol = np.std(returns[:i])
            vol_ratio = current_vol / (avg_vol + 1e-10)

            # Score combiné
            momentum_signal = 1 if momentum > 0 else -1
            accel_signal = 1 if acceleration > 0 else -1
            vol_signal = 1 if vol_ratio < 1.2 else 0  # Favorise basse volatilité

            total_score = momentum_signal + accel_signal + vol_signal

            # Allocation basée sur le score combiné
            if total_score >= 2 and momentum > 0:
                weight = 0.99  # Signal très fort haussier
            elif total_score >= 1 and momentum > 0:
                weight = 0.85  # Signal fort haussier
            elif total_score <= -2 and momentum < 0:
                weight = 0.01  # Signal très fort baissier
            elif total_score <= -1 and momentum < 0:
                weight = 0.15  # Signal fort baissier
            elif momentum > 0:
                weight = 0.7
            elif momentum < 0:
                weight = 0.3
            else:
                weight = 0.5

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

for period in [1, 2, 3, 4, 5]:
    positions = multi_factor_strategy(period)
    score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
    pnl = score['stats']['cumulative_return'] * 100

    if pnl > best_result['pnl']:
        best_result = {
            'pnl': pnl,
            'name': 'Multi-Factor',
            'params': {'period': period},
            'sharpe': score['stats']['sharpe_ratio'],
            'mdd': score['stats']['max_drawdown']
        }
        print(f"  ✓ MultiFactor: PnL={pnl:.2f}%, Period={period}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 5: TREND STRENGTH avec POSITION PYRAMIDING
# ============================================================================
print("\n📊 Phase 5: Trend Strength with Pyramiding")

def trend_strength_pyramiding(lookback=5):
    """Augmente la position progressivement sur une tendance forte"""
    positions = []

    for i in range(len(prices)):
        if i < lookback:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Compter le nombre de périodes consécutives dans la même direction
            consecutive_up = 0
            consecutive_down = 0

            for j in range(1, min(lookback + 1, i + 1)):
                if prices[i - j + 1] > prices[i - j]:
                    consecutive_up += 1
                    if consecutive_down > 0:
                        break
                elif prices[i - j + 1] < prices[i - j]:
                    consecutive_down += 1
                    if consecutive_up > 0:
                        break

            # Pyramiding: plus la tendance est longue, plus on alloue
            if consecutive_up > 0:
                strength = min(consecutive_up / lookback, 1.0)
                weight = 0.5 + 0.49 * strength
            elif consecutive_down > 0:
                strength = min(consecutive_down / lookback, 1.0)
                weight = 0.5 - 0.49 * strength
            else:
                weight = 0.5

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

for lookback in [3, 5, 7, 10, 15]:
    positions = trend_strength_pyramiding(lookback)
    score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
    pnl = score['stats']['cumulative_return'] * 100

    if pnl > best_result['pnl']:
        best_result = {
            'pnl': pnl,
            'name': 'Trend Strength Pyramiding',
            'params': {'lookback': lookback},
            'sharpe': score['stats']['sharpe_ratio'],
            'mdd': score['stats']['max_drawdown']
        }
        print(f"  ✓ Pyramiding: PnL={pnl:.2f}%, Lookback={lookback}, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# STRATÉGIE 6: EXTREME MOMENTUM SCALPING (Ultra-agressif)
# ============================================================================
print("\n📊 Phase 6: Extreme Momentum Scalping")

def extreme_momentum_scalping():
    """Scalping ultra-agressif sur chaque tick"""
    positions = []

    for i in range(len(prices)):
        if i < 1:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Momentum instantané
            instant_return = (prices[i] - prices[i-1]) / prices[i-1]

            # Ultra-agressif: réaction immédiate et totale
            if instant_return > 0.00001:  # Seuil ultra-fin
                weight = 0.99
            elif instant_return < -0.00001:
                weight = 0.01
            else:
                # Même mouvement minime compte
                weight = 0.99 if instant_return >= 0 else 0.01

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})

    return pd.DataFrame(positions).set_index('epoch')

positions = extreme_momentum_scalping()
score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
pnl = score['stats']['cumulative_return'] * 100

if pnl > best_result['pnl']:
    best_result = {
        'pnl': pnl,
        'name': 'Extreme Momentum Scalping',
        'params': {'threshold': 0.00001},
        'sharpe': score['stats']['sharpe_ratio'],
        'mdd': score['stats']['max_drawdown']
    }
    print(f"  ✓ Scalping: PnL={pnl:.2f}%, Sharpe={score['stats']['sharpe_ratio']:.2f}")

# ============================================================================
# AFFICHER LE MEILLEUR
# ============================================================================
print("\n" + "=" * 80)
print("🏆 MEILLEURE STRATÉGIE TROUVÉE")
print("=" * 80)
print(f"\nNom: {best_result['name']}")
print(f"PnL: {best_result['pnl']:.2f}%")
print(f"Sharpe: {best_result['sharpe']:.4f}")
print(f"Max Drawdown: {best_result['mdd']*100:.2f}%")
print(f"\nParamètres: {best_result['params']}")

if best_result['pnl'] >= 4000:
    print("\n🎉🎉🎉 OBJECTIF 4000% ATTEINT! 🎉🎉🎉")
else:
    print(f"\n📊 Progression: {best_result['pnl']:.2f}% / 4000% ({best_result['pnl']/40:.1f}%)")

print("=" * 80)

# Sauvegarder
import json
with open('master_best_strategy.json', 'w') as f:
    json.dump(best_result, f, indent=2, default=float)
