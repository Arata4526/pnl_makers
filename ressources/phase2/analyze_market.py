#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Charger les données
data = pd.read_csv('data/asset_b_train.csv', index_col=0)
prices = data['Asset B'].values

print("=" * 80)
print("📊 ANALYSE DU MARCHÉ")
print("=" * 80)

# Statistiques de base
print("\n🔍 STATISTIQUES DE BASE:")
print(f"  Nombre d'observations: {len(prices)}")
print(f"  Prix min: {prices.min():.4f}")
print(f"  Prix max: {prices.max():.4f}")
print(f"  Prix moyen: {prices.mean():.4f}")
print(f"  Prix médian: {np.median(prices):.4f}")
print(f"  Écart-type: {prices.std():.4f}")

# Analyse des rendements
returns = np.diff(prices) / prices[:-1]
print(f"\n📈 RENDEMENTS:")
print(f"  Rendement moyen: {returns.mean()*100:.4f}%")
print(f"  Volatilité: {returns.std()*100:.4f}%")
print(f"  Rendement cumulé: {(prices[-1]/prices[0] - 1)*100:.2f}%")
print(f"  Sharpe (annualisé): {returns.mean()/returns.std() * np.sqrt(252):.4f}")

# Analyse de tendance
print(f"\n📊 TENDANCES:")
print(f"  Rendements positifs: {(returns > 0).sum()} ({(returns > 0).mean()*100:.1f}%)")
print(f"  Rendements négatifs: {(returns < 0).sum()} ({(returns < 0).mean()*100:.1f}%)")

# Autocorrélation
autocorr_1 = np.corrcoef(returns[:-1], returns[1:])[0, 1]
autocorr_5 = np.corrcoef(returns[:-5], returns[5:])[0, 1]
autocorr_10 = np.corrcoef(returns[:-10], returns[10:])[0, 1]
print(f"\n🔄 AUTOCORRÉLATION DES RENDEMENTS:")
print(f"  Lag 1: {autocorr_1:.4f}")
print(f"  Lag 5: {autocorr_5:.4f}")
print(f"  Lag 10: {autocorr_10:.4f}")

# Calcul de moyennes mobiles pour identifier les tendances
ma_5 = pd.Series(prices).rolling(window=5).mean().values
ma_10 = pd.Series(prices).rolling(window=10).mean().values
ma_20 = pd.Series(prices).rolling(window=20).mean().values
ma_50 = pd.Series(prices).rolling(window=50).mean().values

print(f"\n📉 MOYENNES MOBILES (à la fin de la période):")
print(f"  MA5: {ma_5[-1]:.4f}")
print(f"  MA10: {ma_10[-1]:.4f}")
print(f"  MA20: {ma_20[-1]:.4f}")
print(f"  MA50: {ma_50[-1]:.4f}")
print(f"  Prix actuel: {prices[-1]:.4f}")

# Analyse de volatilité
volatility_window = 20
rolling_vol = pd.Series(returns).rolling(window=volatility_window).std().values
print(f"\n📊 VOLATILITÉ ROULANTE (window={volatility_window}):")
print(f"  Volatilité moyenne: {np.nanmean(rolling_vol)*100:.4f}%")
print(f"  Volatilité min: {np.nanmin(rolling_vol)*100:.4f}%")
print(f"  Volatilité max: {np.nanmax(rolling_vol)*100:.4f}%")

# Calcul RSI (Relative Strength Index)
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    gain = np.where(deltas > 0, deltas, 0)
    loss = np.where(deltas < 0, -deltas, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean().values
    avg_loss = pd.Series(loss).rolling(window=period).mean().values

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi

rsi = calculate_rsi(prices)
print(f"\n📊 RSI (Relative Strength Index, period=14):")
print(f"  RSI actuel: {rsi[-1]:.2f}")
print(f"  RSI moyen: {np.nanmean(rsi):.2f}")
print(f"  RSI min: {np.nanmin(rsi):.2f}")
print(f"  RSI max: {np.nanmax(rsi):.2f}")

# Analyse momentum
momentum_5 = prices[-1] / prices[-6] - 1
momentum_10 = prices[-1] / prices[-11] - 1
momentum_20 = prices[-1] / prices[-21] - 1
print(f"\n🚀 MOMENTUM:")
print(f"  5 jours: {momentum_5*100:.2f}%")
print(f"  10 jours: {momentum_10*100:.2f}%")
print(f"  20 jours: {momentum_20*100:.2f}%")

print("\n" + "=" * 80)
