#!/usr/bin/env python3
"""
Visualiseur de données financières
Charge et visualise les données depuis le dossier ../data
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns

# Configuration de style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class VisualiseurFinancier:
    """Classe pour visualiser les données financières"""

    def __init__(self, data_dir='../data'):
        """Initialise le visualiseur avec le répertoire de données"""
        self.data_dir = Path(data_dir)
        self.data = {}

    def charger_donnees(self):
        """Charge tous les fichiers CSV du répertoire data"""
        csv_files = list(self.data_dir.glob('*.csv'))

        if not csv_files:
            print(f"⚠️  Aucun fichier CSV trouvé dans {self.data_dir}")
            return

        print(f"📊 Chargement des données depuis {self.data_dir}...")

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, index_col=0)
                nom_fichier = csv_file.stem
                self.data[nom_fichier] = df
                print(f"✓ {nom_fichier}: {len(df)} lignes, {len(df.columns)} colonnes")
            except Exception as e:
                print(f"✗ Erreur lors du chargement de {csv_file.name}: {e}")

        print(f"\n📈 {len(self.data)} fichier(s) chargé(s) avec succès\n")

    def afficher_statistiques(self):
        """Affiche les statistiques descriptives pour chaque dataset"""
        if not self.data:
            print("Aucune donnée chargée. Utilisez charger_donnees() d'abord.")
            return

        for nom, df in self.data.items():
            print(f"\n{'='*60}")
            print(f"📊 Statistiques pour: {nom}")
            print(f"{'='*60}")
            print(df.describe())
            print(f"\nPremières lignes:")
            print(df.head())
            print(f"\nDernières lignes:")
            print(df.tail())

    def plot_series_temporelles(self):
        """Affiche les séries temporelles pour tous les datasets"""
        if not self.data:
            print("Aucune donnée chargée.")
            return

        fig, axes = plt.subplots(len(self.data), 1, figsize=(12, 4*len(self.data)))

        if len(self.data) == 1:
            axes = [axes]

        for idx, (nom, df) in enumerate(self.data.items()):
            ax = axes[idx]

            for col in df.columns:
                ax.plot(df.index, df[col], label=col, linewidth=2)

            ax.set_title(f'Série Temporelle - {nom}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Temps', fontsize=12)
            ax.set_ylabel('Valeur', fontsize=12)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.data_dir.parent / 'visualiseur' / 'series_temporelles.png', dpi=300, bbox_inches='tight')
        print("✓ Graphique sauvegardé: series_temporelles.png")
        plt.show()

    def plot_rendements(self):
        """Calcule et affiche les rendements (variations)"""
        if not self.data:
            print("Aucune donnée chargée.")
            return

        fig, axes = plt.subplots(len(self.data), 1, figsize=(12, 4*len(self.data)))

        if len(self.data) == 1:
            axes = [axes]

        for idx, (nom, df) in enumerate(self.data.items()):
            ax = axes[idx]

            # Calcul des rendements (variation en pourcentage)
            rendements = df.pct_change().dropna() * 100

            for col in rendements.columns:
                ax.plot(rendements.index, rendements[col], label=f'{col} (Rendements %)', linewidth=1.5, alpha=0.7)

            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
            ax.set_title(f'Rendements (%) - {nom}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Temps', fontsize=12)
            ax.set_ylabel('Rendement (%)', fontsize=12)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.data_dir.parent / 'visualiseur' / 'rendements.png', dpi=300, bbox_inches='tight')
        print("✓ Graphique sauvegardé: rendements.png")
        plt.show()

    def plot_distribution(self):
        """Affiche la distribution des valeurs"""
        if not self.data:
            print("Aucune donnée chargée.")
            return

        for nom, df in self.data.items():
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            # Histogramme
            for col in df.columns:
                axes[0].hist(df[col], bins=30, alpha=0.6, label=col, edgecolor='black')

            axes[0].set_title(f'Distribution des Valeurs - {nom}', fontsize=14, fontweight='bold')
            axes[0].set_xlabel('Valeur', fontsize=12)
            axes[0].set_ylabel('Fréquence', fontsize=12)
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)

            # Boxplot
            df.boxplot(ax=axes[1])
            axes[1].set_title(f'Boîte à Moustaches - {nom}', fontsize=14, fontweight='bold')
            axes[1].set_ylabel('Valeur', fontsize=12)
            axes[1].grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.data_dir.parent / 'visualiseur' / f'distribution_{nom}.png', dpi=300, bbox_inches='tight')
            print(f"✓ Graphique sauvegardé: distribution_{nom}.png")
            plt.show()

    def plot_correlation(self):
        """Affiche la matrice de corrélation si plusieurs colonnes"""
        if not self.data:
            print("Aucune donnée chargée.")
            return

        for nom, df in self.data.items():
            if len(df.columns) < 2:
                print(f"⚠️  {nom}: Une seule colonne, corrélation non applicable")
                continue

            fig, ax = plt.subplots(figsize=(10, 8))

            corr = df.corr()
            sns.heatmap(corr, annot=True, fmt='.3f', cmap='coolwarm',
                       center=0, square=True, ax=ax, cbar_kws={"shrink": 0.8})

            ax.set_title(f'Matrice de Corrélation - {nom}', fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.savefig(self.data_dir.parent / 'visualiseur' / f'correlation_{nom}.png', dpi=300, bbox_inches='tight')
            print(f"✓ Graphique sauvegardé: correlation_{nom}.png")
            plt.show()

    def analyser_tout(self):
        """Exécute toutes les analyses et visualisations"""
        print("\n" + "="*60)
        print("🔍 ANALYSE COMPLÈTE DES DONNÉES FINANCIÈRES")
        print("="*60 + "\n")

        self.charger_donnees()

        if not self.data:
            return

        self.afficher_statistiques()

        print("\n" + "="*60)
        print("📈 GÉNÉRATION DES VISUALISATIONS")
        print("="*60 + "\n")

        self.plot_series_temporelles()
        self.plot_rendements()
        self.plot_distribution()
        self.plot_correlation()

        print("\n" + "="*60)
        print("✅ ANALYSE TERMINÉE")
        print("="*60 + "\n")


def menu_interactif():
    """Menu interactif pour l'utilisateur"""
    visualiseur = VisualiseurFinancier()

    while True:
        print("\n" + "="*60)
        print("📊 VISUALISEUR DE DONNÉES FINANCIÈRES")
        print("="*60)
        print("\n1. Charger les données")
        print("2. Afficher les statistiques")
        print("3. Tracer les séries temporelles")
        print("4. Tracer les rendements")
        print("5. Afficher la distribution")
        print("6. Afficher la matrice de corrélation")
        print("7. Analyse complète")
        print("0. Quitter")
        print("\n" + "="*60)

        choix = input("\nVotre choix: ").strip()

        if choix == '1':
            visualiseur.charger_donnees()
        elif choix == '2':
            visualiseur.afficher_statistiques()
        elif choix == '3':
            visualiseur.plot_series_temporelles()
        elif choix == '4':
            visualiseur.plot_rendements()
        elif choix == '5':
            visualiseur.plot_distribution()
        elif choix == '6':
            visualiseur.plot_correlation()
        elif choix == '7':
            visualiseur.analyser_tout()
        elif choix == '0':
            print("\n👋 Au revoir!")
            break
        else:
            print("\n⚠️  Choix invalide. Veuillez réessayer.")


if __name__ == '__main__':
    # Lancer le menu interactif
    menu_interactif()
