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
print("🧪 TEST DES STRATÉGIES DE TRADING")
print("=" * 80)

# ============================================================================
# STRATÉGIE 1: BUY AND HOLD
# ============================================================================
def strategy_buy_and_hold():
    positions = []
    for i in range(len(prices)):
        positions.append({
            'epoch': i,
            'Asset B': 1.0,
            'Cash': 0.0
        })
    return pd.DataFrame(positions).set_index('epoch')

# ============================================================================
# STRATÉGIE 2: MOMENTUM SIMPLE (stratégie actuelle)
# ============================================================================
def strategy_momentum_simple():
    positions = []
    for i in range(len(prices)):
        if i == 0:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            delta = prices[i] - prices[i-1]
            if delta > 0:
                positions.append({'epoch': i, 'Asset B': 0.7, 'Cash': 0.3})
            else:
                positions.append({'epoch': i, 'Asset B': 0.3, 'Cash': 0.7})
    return pd.DataFrame(positions).set_index('epoch')

# ============================================================================
# STRATÉGIE 3: MOMENTUM AVEC MOYENNES MOBILES
# ============================================================================
def strategy_moving_average_crossover():
    positions = []
    ma_short = pd.Series(prices).rolling(window=10).mean().values
    ma_long = pd.Series(prices).rolling(window=50).mean().values

    for i in range(len(prices)):
        if i < 50 or np.isnan(ma_short[i]) or np.isnan(ma_long[i]):
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Signal haussier: MA courte > MA longue
            if ma_short[i] > ma_long[i]:
                positions.append({'epoch': i, 'Asset B': 0.9, 'Cash': 0.1})
            else:
                positions.append({'epoch': i, 'Asset B': 0.1, 'Cash': 0.9})
    return pd.DataFrame(positions).set_index('epoch')

# ============================================================================
# STRATÉGIE 4: RSI MEAN REVERSION
# ============================================================================
def strategy_rsi_mean_reversion():
    def calculate_rsi(prices, period=14):
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)

        avg_gain = pd.Series(gain).rolling(window=period).mean().values
        avg_loss = pd.Series(loss).rolling(window=period).mean().values

        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    positions = []
    rsi = calculate_rsi(prices, period=14)

    for i in range(len(prices)):
        if i < 15 or np.isnan(rsi[i-1]):
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            rsi_val = rsi[i-1]
            # Survendu (RSI < 30): acheter plus
            if rsi_val < 30:
                positions.append({'epoch': i, 'Asset B': 0.9, 'Cash': 0.1})
            # Suracheté (RSI > 70): vendre
            elif rsi_val > 70:
                positions.append({'epoch': i, 'Asset B': 0.1, 'Cash': 0.9})
            # Zone neutre: position équilibrée
            else:
                positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
    return pd.DataFrame(positions).set_index('epoch')

# ============================================================================
# STRATÉGIE 5: MOMENTUM ADAPTATIF AVEC VOLATILITÉ
# ============================================================================
def strategy_adaptive_momentum():
    positions = []
    returns = np.diff(prices) / prices[:-1]

    for i in range(len(prices)):
        if i < 20:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Calculer la volatilité récente
            recent_returns = returns[max(0, i-20):i]
            volatility = np.std(recent_returns)

            # Calculer le momentum
            momentum = (prices[i] - prices[i-5]) / prices[i-5] if i >= 5 else 0

            # Adapter l'exposition à la volatilité
            if volatility > 0.01:  # Haute volatilité
                if momentum > 0:
                    weight = 0.6
                else:
                    weight = 0.4
            else:  # Basse volatilité
                if momentum > 0:
                    weight = 0.8
                else:
                    weight = 0.2

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

# ============================================================================
# STRATÉGIE 6: TRIPLE MOMENTUM (court, moyen, long terme)
# ============================================================================
def strategy_triple_momentum():
    positions = []

    for i in range(len(prices)):
        if i < 20:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # Momentum court terme (5 jours)
            mom_short = (prices[i] - prices[i-5]) / prices[i-5] if i >= 5 else 0
            # Momentum moyen terme (10 jours)
            mom_medium = (prices[i] - prices[i-10]) / prices[i-10] if i >= 10 else 0
            # Momentum long terme (20 jours)
            mom_long = (prices[i] - prices[i-20]) / prices[i-20] if i >= 20 else 0

            # Score de momentum (pondéré)
            momentum_score = 0.5 * mom_short + 0.3 * mom_medium + 0.2 * mom_long

            # Allocation basée sur le score
            if momentum_score > 0.01:
                weight = 0.9
            elif momentum_score > 0:
                weight = 0.7
            elif momentum_score > -0.01:
                weight = 0.3
            else:
                weight = 0.1

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

# ============================================================================
# STRATÉGIE 7: COMBINÉE (RSI + MOMENTUM + VOLATILITÉ)
# ============================================================================
def strategy_combined_advanced():
    def calculate_rsi(prices, period=14):
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        avg_gain = pd.Series(gain).rolling(window=period).mean().values
        avg_loss = pd.Series(loss).rolling(window=period).mean().values
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    positions = []
    returns = np.diff(prices) / prices[:-1]
    rsi = calculate_rsi(prices, period=14)

    for i in range(len(prices)):
        if i < 20:
            positions.append({'epoch': i, 'Asset B': 0.5, 'Cash': 0.5})
        else:
            # 1. Signal RSI
            rsi_val = rsi[i-1] if i > 0 and not np.isnan(rsi[i-1]) else 50
            if rsi_val < 30:
                rsi_signal = 0.3  # Signal haussier fort
            elif rsi_val < 40:
                rsi_signal = 0.15
            elif rsi_val > 70:
                rsi_signal = -0.3  # Signal baissier fort
            elif rsi_val > 60:
                rsi_signal = -0.15
            else:
                rsi_signal = 0

            # 2. Signal momentum
            momentum = (prices[i] - prices[i-10]) / prices[i-10] if i >= 10 else 0
            momentum_signal = np.clip(momentum * 10, -0.3, 0.3)

            # 3. Signal volatilité (adapter l'exposition)
            recent_returns = returns[max(0, i-20):i]
            volatility = np.std(recent_returns)
            vol_factor = 1.0 if volatility < 0.005 else 0.7 if volatility < 0.01 else 0.5

            # 4. Combiner les signaux
            base_weight = 0.5
            signal = rsi_signal + momentum_signal
            weight = base_weight + signal
            weight = np.clip(weight * vol_factor, 0.05, 0.95)

            positions.append({'epoch': i, 'Asset B': weight, 'Cash': 1-weight})
    return pd.DataFrame(positions).set_index('epoch')

# ============================================================================
# TESTER TOUTES LES STRATÉGIES
# ============================================================================
strategies = {
    'Buy and Hold': strategy_buy_and_hold,
    'Momentum Simple': strategy_momentum_simple,
    'MA Crossover': strategy_moving_average_crossover,
    'RSI Mean Reversion': strategy_rsi_mean_reversion,
    'Adaptive Momentum': strategy_adaptive_momentum,
    'Triple Momentum': strategy_triple_momentum,
    'Combined Advanced': strategy_combined_advanced,
}

results = {}

for name, strategy_func in strategies.items():
    print(f"\n🔄 Test de: {name}")
    positions = strategy_func()
    score = get_local_score(prices=prices_df, positions=positions, initial_capital=1000)
    results[name] = {
        'sharpe': score['stats']['sharpe_ratio'],
        'cumulative_return': score['stats']['cumulative_return'],
        'max_drawdown': score['stats']['max_drawdown'],
        'base_score': score['scores']['base_score'],
        'positions': positions
    }
    print(f"   Sharpe: {score['stats']['sharpe_ratio']:.4f}")
    print(f"   Rendement cumulé: {score['stats']['cumulative_return']*100:.2f}%")
    print(f"   Max Drawdown: {score['stats']['max_drawdown']*100:.2f}%")
    print(f"   Base Score: {score['scores']['base_score']:.4f}")

# ============================================================================
# AFFICHER LE CLASSEMENT
# ============================================================================
print("\n" + "=" * 80)
print("🏆 CLASSEMENT DES STRATÉGIES (par Base Score)")
print("=" * 80)

sorted_results = sorted(results.items(), key=lambda x: x[1]['base_score'], reverse=True)

for rank, (name, result) in enumerate(sorted_results, 1):
    print(f"\n{rank}. {name}")
    print(f"   Base Score: {result['base_score']:.4f}")
    print(f"   Sharpe: {result['sharpe']:.4f}")
    print(f"   Rendement: {result['cumulative_return']*100:.2f}%")
    print(f"   Max DD: {result['max_drawdown']*100:.2f}%")

print("\n" + "=" * 80)
print(f"🎯 MEILLEURE STRATÉGIE: {sorted_results[0][0]}")
print("=" * 80)
