# Visualiseur de Données Financières

Ce visualiseur permet d'analyser et de visualiser les données financières contenues dans le dossier `../data`.

## Installation

1. Installez les dépendances:
```bash
pip install -r requirements.txt
```

## Utilisation

### Interface Graphique (Recommandé)

Lancez l'interface graphique complète qui affiche tout en une seule fenêtre:
```bash
./run_gui.sh
```
ou
```bash
python3 visualiseur_gui.py
```

L'interface graphique offre:
- **Vue d'ensemble**: Tous les graphiques affichés dans une seule fenêtre scrollable
  - Séries temporelles
  - Rendements (%)
  - Distributions et boxplots
- **Statistiques**: Toutes les statistiques détaillées
- **Bouton Rafraîchir**: Recharge les données à la volée
- **Bouton Sauvegarder**: Exporte tous les graphiques en haute résolution

### Mode Terminal (Interactif)

Lancez le visualiseur en mode interactif dans le terminal:
```bash
./run.sh
```
ou
```bash
python3 visualiseur.py
```

Un menu vous permettra de:
- Charger les données
- Afficher les statistiques descriptives
- Générer différents types de graphiques
- Effectuer une analyse complète

### Utilisation Programmatique

Vous pouvez aussi utiliser le visualiseur dans vos propres scripts:

```python
from visualiseur import VisualiseurFinancier

# Créer une instance
vis = VisualiseurFinancier(data_dir='../data')

# Charger les données
vis.charger_donnees()

# Afficher les statistiques
vis.afficher_statistiques()

# Générer des graphiques
vis.plot_series_temporelles()
vis.plot_rendements()
vis.plot_distribution()

# Ou tout faire d'un coup
vis.analyser_tout()
```

## Fonctionnalités

### 1. Séries Temporelles
Affiche l'évolution des valeurs dans le temps.

### 2. Rendements
Calcule et affiche les variations en pourcentage entre chaque période.

### 3. Distribution
Montre la distribution des valeurs avec:
- Histogramme
- Boîte à moustaches (boxplot)

### 4. Corrélation
Affiche une matrice de corrélation entre les différentes colonnes (si applicable).

### 5. Statistiques
Affiche des statistiques descriptives complètes:
- Moyenne, médiane
- Écart-type
- Min, max
- Quartiles

## Fichiers Générés

Les graphiques sont automatiquement sauvegardés dans le dossier `visualiseur/`:
- `series_temporelles.png`
- `rendements.png`
- `distribution_[nom].png`
- `correlation_[nom].png`

## Structure

```
visualiseur/
├── visualiseur_gui.py      # Interface graphique (recommandé)
├── visualiseur.py          # Script terminal/ligne de commande
├── run_gui.sh             # Lanceur GUI
├── run.sh                 # Lanceur terminal
├── requirements.txt        # Dépendances Python
└── README.md              # Ce fichier
```
