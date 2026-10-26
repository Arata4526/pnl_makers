# PnL Makers : hackathon Ramify (décembre 2025)

Bot de trading algorithmique développé en équipe de deux pendant le hackathon Ramify. Le but : écrire une fonction `make_decision(epoch, price)` qui décide à chaque pas de temps de la répartition du portefeuille entre des actifs et du cash, notée sur le rendement et le ratio de Sharpe.

## Approche

- **Phase 1** (un actif + cash) : stratégie à indicateurs multiples, puis recherche de paramètres pour limiter le drawdown maximal à 40 %.
- **Phase 2** (deux actifs) : stratégie *Triple Momentum*. Trois horizons de momentum (5, 10 et 20 périodes, pondérés 50/30/20) donnent un score qui fixe l'allocation, de 10 % à 90 % sur l'actif le plus porteur.
- Scripts d'optimisation par grille (`optimize_strategy.py`, `optimize_leverage.py`) et de test par période (`test_period_1_2.py`).

## Résultats (backtest sur les données du hackathon)

| Métrique | Valeur |
|---|---|
| Ratio de Sharpe | 2,86 |
| Rendement cumulé | +314 % |
| Drawdown maximal | −9,2 % |

Nous n'avons pas gagné. Avec le recul, les paramètres ont été optimisés sur les mêmes données que celles du score : ces chiffres sont très probablement surajustés et ne diraient rien d'un marché réel. Une validation *walk-forward* sur des périodes jamais vues aurait été la bonne méthode.

## Arborescence

```
ressources/phase1/   bot, optimisation, scoring et visualiseur fournis
ressources/phase2/   stratégie Triple Momentum, optimisations, résultats
temp_baul_band/      variante de soumission de la phase 1
```

## Lancer

```bash
cd ressources/phase2
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirement.txt
python3 main.py
```

Équipe : Arata4526, Firfal.
