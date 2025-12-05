# 🤖 Bot Trading - Triple Momentum Strategy

Algorithme de trading optimisé utilisant une stratégie de Triple Momentum pour maximiser les rendements tout en contrôlant le risque.

## 📊 Performances

| Métrique | Valeur |
|----------|--------|
| **Base Score** | 0.8967 |
| **Sharpe Ratio** | 2.86 |
| **Rendement Cumulé** | +314.14% |
| **Max Drawdown** | -9.20% |
| **Sharpe Score** | 1.4299 |
| **PnL Score** | 0.6283 |

## 🎯 Stratégie: Triple Momentum

La stratégie combine trois horizons temporels de momentum pour capturer les tendances du marché:

1. **Momentum Court Terme (5 périodes)** - 50% du signal
   - Capture les mouvements immédiats
   - Maximise la réactivité

2. **Momentum Moyen Terme (10 périodes)** - 30% du signal
   - Filtre le bruit
   - Confirme la tendance

3. **Momentum Long Terme (20 périodes)** - 20% du signal
   - Identifie la tendance de fond
   - Stabilise les décisions

### Allocation Dynamique

Le score de momentum combiné détermine l'allocation:

```
Score > 0.01   → 90% Asset B (très haussier)
Score > 0      → 70% Asset B (haussier)
Score > -0.01  → 30% Asset B (baissier)
Score ≤ -0.01  → 10% Asset B (très baissier)
```

## 🚀 Installation

### 1. Configuration de l'environnement

```bash
chmod +x setup_env.sh
./setup_env.sh
```

### 2. Installation manuelle (alternative)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirement.txt
```

## 💻 Utilisation

### Exécution du bot

```bash
# Exécution simple
python3 main.py data/asset_b_train.csv

# Avec graphique
python3 main.py data/asset_b_train.csv --show-graph
```

### Scripts d'analyse

```bash
# Analyser les statistiques du marché
python3 analyze_market.py

# Tester différentes stratégies
python3 test_strategies.py
```

## 📁 Structure du Projet

```
.
├── bot_trade.py           # Algorithme de trading (Triple Momentum)
├── main.py                # Script principal d'exécution
├── requirement.txt        # Dépendances Python
├── setup_env.sh          # Script de configuration
├── data/
│   └── asset_b_train.csv # Données d'entraînement
├── scoring/
│   └── scoring.py        # Module de scoring et backtest
├── analyze_market.py     # Analyse statistique du marché
└── test_strategies.py    # Framework de test de stratégies
```

## 🔬 Analyse du Marché

### Caractéristiques Identifiées

- **Observations**: 2520 périodes
- **Rendement moyen**: 0.0327% par période
- **Volatilité**: 0.53% par période
- **Autocorrélation (lag 1)**: 0.354 (forte persistance des tendances)
- **Distribution**: 52.2% rendements positifs / 47.8% négatifs

### Métriques Clés

- **Prix min/max**: 1.9350 / 4.8601
- **Sharpe annualisé (buy-and-hold)**: 0.99
- **Rendement cumulé (buy-and-hold)**: 120.29%

## 🧪 Stratégies Testées

| Rang | Stratégie | Base Score | Sharpe | Rendement | Max DD |
|------|-----------|------------|--------|-----------|--------|
| 🥇 | **Triple Momentum** | **0.8967** | **2.86** | **314%** | **-9.20%** |
| 🥈 | Adaptive Momentum | 0.7903 | 2.68 | 251% | -12.63% |
| 🥉 | Momentum Simple | 0.7119 | 2.54 | 202% | -11.68% |
| 4 | MA Crossover | 0.3997 | 1.26 | 101% | -11.38% |
| 5 | Buy and Hold | 0.3628 | 0.98 | 120% | -28.92% |
| 6 | Combined Advanced | 0.2280 | 0.70 | 29% | -12.53% |
| 7 | RSI Mean Reversion | 0.0590 | -0.88 | -33% | -41.03% |

## 📈 Avantages de la Stratégie

1. **Performance Exceptionnelle**
   - Surperforme le buy-and-hold de 161%
   - Sharpe ratio 2.9x supérieur au marché

2. **Gestion du Risque**
   - Max Drawdown réduit de 68% vs buy-and-hold
   - Allocation dynamique adaptée aux conditions de marché

3. **Robustesse**
   - Exploite l'autocorrélation naturelle du marché
   - Combine plusieurs horizons temporels
   - Réduit le bruit grâce à la pondération

## 🔧 Configuration

### Paramètres de la Stratégie

Les paramètres suivants peuvent être ajustés dans `bot_trade.py`:

```python
# Horizons de momentum
SHORT_TERM = 5    # Périodes pour momentum court terme
MEDIUM_TERM = 10  # Périodes pour momentum moyen terme
LONG_TERM = 20    # Périodes pour momentum long terme

# Pondérations
WEIGHT_SHORT = 0.5   # 50%
WEIGHT_MEDIUM = 0.3  # 30%
WEIGHT_LONG = 0.2    # 20%

# Seuils d'allocation
THRESHOLD_HIGH = 0.01    # Score pour allocation agressive
THRESHOLD_NEUTRAL = 0.0  # Score pour allocation neutre
THRESHOLD_LOW = -0.01    # Score pour allocation défensive
```

## 📦 Dépendances

- `pandas` - Manipulation des données
- `numpy` - Calculs numériques
- `matplotlib` - Visualisation des résultats

## 📝 Notes

- La stratégie nécessite 20 périodes de warm-up avant d'être pleinement opérationnelle
- Les frais de transaction (0.01%) sont pris en compte dans le backtest
- Le capital initial par défaut est de 1000 unités

## 🎓 Méthodologie

1. **Analyse exploratoire** des données de marché
2. **Identification** des caractéristiques clés (autocorrélation, volatilité)
3. **Développement** de 7 stratégies différentes
4. **Backtesting** rigoureux avec frais de transaction
5. **Sélection** de la stratégie optimale (Triple Momentum)
6. **Validation** des performances sur données d'entraînement

## 🏆 Résultats

La stratégie Triple Momentum a été sélectionnée comme stratégie optimale car elle:
- Maximise le Sharpe ratio (meilleur rapport risque/rendement)
- Génère le rendement le plus élevé (314%)
- Maintient un drawdown contrôlé (-9.20%)
- Obtient le Base Score le plus élevé (0.8967)

---

**Développé et optimisé pour maximiser les performances de trading** 🚀
