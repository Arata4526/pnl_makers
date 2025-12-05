#!/usr/bin/env python3
"""
Visualiseur de données financières - Interface Graphique
Affiche toutes les visualisations dans une seule interface
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox

# Configuration de style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class VisualiseurGUI:
    """Interface graphique pour visualiser les données financières"""

    def __init__(self, root):
        self.root = root
        self.root.title("📊 Visualiseur de Données Financières")
        self.root.geometry("1400x900")

        self.data_dir = Path('../data')
        self.data = {}

        # Configurer le style
        style = ttk.Style()
        style.theme_use('clam')

        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurer le redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Titre et boutons
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        title_label = ttk.Label(header_frame, text="📊 Visualiseur de Données Financières",
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=10)

        # Bouton de rafraîchissement
        refresh_btn = ttk.Button(header_frame, text="🔄 Rafraîchir",
                                command=self.rafraichir)
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Bouton pour sauvegarder
        save_btn = ttk.Button(header_frame, text="💾 Sauvegarder Graphiques",
                             command=self.sauvegarder_graphiques)
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Créer les onglets
        self.tab_overview = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_overview, text="📈 Vue d'ensemble")
        self.notebook.add(self.tab_stats, text="📊 Statistiques")

    def charger_donnees(self):
        """Charge tous les fichiers CSV et affiche les visualisations"""
        csv_files = list(self.data_dir.glob('*.csv'))

        if not csv_files:
            messagebox.showerror("Erreur", f"Aucun fichier CSV trouvé dans {self.data_dir}")
            return

        self.data = {}
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, index_col=0)
                nom_fichier = csv_file.stem
                self.data[nom_fichier] = df
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement de {csv_file.name}: {e}")

        if self.data:
            self.afficher_visualisations()
            self.afficher_statistiques()

    def afficher_visualisations(self):
        """Affiche toutes les visualisations dans l'onglet overview"""
        # Nettoyer l'onglet
        for widget in self.tab_overview.winfo_children():
            widget.destroy()

        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(self.tab_overview)
        scrollbar = ttk.Scrollbar(self.tab_overview, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Créer la figure principale avec toutes les visualisations
        fig = Figure(figsize=(14, 20))

        # Calculer le nombre de lignes nécessaires
        num_datasets = len(self.data)

        # Position pour les sous-graphiques
        plot_position = 1

        for nom, df in self.data.items():
            # 1. Série Temporelle
            ax1 = fig.add_subplot(num_datasets * 4, 1, plot_position)
            for col in df.columns:
                ax1.plot(df.index, df[col], label=col, linewidth=2)
            ax1.set_title(f'Série Temporelle - {nom}', fontsize=12, fontweight='bold', pad=10)
            ax1.set_xlabel('Temps')
            ax1.set_ylabel('Valeur')
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.3)
            plot_position += 1

            # 2. Rendements
            ax2 = fig.add_subplot(num_datasets * 4, 1, plot_position)
            rendements = df.pct_change().dropna() * 100
            for col in rendements.columns:
                ax2.plot(rendements.index, rendements[col], label=f'{col}', linewidth=1.5, alpha=0.7)
            ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
            ax2.set_title(f'Rendements (%) - {nom}', fontsize=12, fontweight='bold', pad=10)
            ax2.set_xlabel('Temps')
            ax2.set_ylabel('Rendement (%)')
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.3)
            plot_position += 1

            # 3. Distribution
            ax3 = fig.add_subplot(num_datasets * 4, 2, plot_position)
            for col in df.columns:
                ax3.hist(df[col], bins=30, alpha=0.6, label=col, edgecolor='black')
            ax3.set_title(f'Distribution - {nom}', fontsize=11, fontweight='bold')
            ax3.set_xlabel('Valeur')
            ax3.set_ylabel('Fréquence')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

            # 4. Boxplot
            ax4 = fig.add_subplot(num_datasets * 4, 2, plot_position + 1)
            df.boxplot(ax=ax4)
            ax4.set_title(f'Boîte à Moustaches - {nom}', fontsize=11, fontweight='bold')
            ax4.set_ylabel('Valeur')
            ax4.grid(True, alpha=0.3)
            plot_position += 3

        fig.tight_layout(pad=3.0)

        # Intégrer la figure dans tkinter
        canvas_fig = FigureCanvasTkAgg(fig, master=scrollable_frame)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Stocker la figure pour la sauvegarde
        self.main_figure = fig

    def afficher_statistiques(self):
        """Affiche les statistiques dans l'onglet stats"""
        # Nettoyer l'onglet
        for widget in self.tab_stats.winfo_children():
            widget.destroy()

        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(self.tab_stats)
        scrollbar = ttk.Scrollbar(self.tab_stats, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Afficher les statistiques pour chaque dataset
        for nom, df in self.data.items():
            # Frame pour ce dataset
            dataset_frame = ttk.LabelFrame(scrollable_frame, text=f"📊 {nom}", padding="10")
            dataset_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Statistiques descriptives
            stats_text = tk.Text(dataset_frame, height=15, width=100, font=('Courier', 10))
            stats_text.pack(fill=tk.BOTH, expand=True)

            # Ajouter les statistiques
            stats_text.insert('1.0', f"STATISTIQUES DESCRIPTIVES\n")
            stats_text.insert('end', "="*80 + "\n\n")
            stats_text.insert('end', str(df.describe()) + "\n\n")

            stats_text.insert('end', f"\nINFORMATIONS GÉNÉRALES\n")
            stats_text.insert('end', "="*80 + "\n")
            stats_text.insert('end', f"Nombre de lignes: {len(df)}\n")
            stats_text.insert('end', f"Nombre de colonnes: {len(df.columns)}\n")
            stats_text.insert('end', f"Colonnes: {', '.join(df.columns)}\n\n")

            stats_text.insert('end', f"\nPREMIÈRES LIGNES\n")
            stats_text.insert('end', "="*80 + "\n")
            stats_text.insert('end', str(df.head(10)) + "\n\n")

            stats_text.insert('end', f"\nDERNIÈRES LIGNES\n")
            stats_text.insert('end', "="*80 + "\n")
            stats_text.insert('end', str(df.tail(10)) + "\n")

            stats_text.config(state='disabled')

            # Calcul des rendements
            rendements = df.pct_change().dropna() * 100

            rend_frame = ttk.LabelFrame(dataset_frame, text="Statistiques des Rendements (%)", padding="10")
            rend_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

            rend_text = tk.Text(rend_frame, height=8, width=100, font=('Courier', 10))
            rend_text.pack(fill=tk.BOTH, expand=True)
            rend_text.insert('1.0', str(rendements.describe()))
            rend_text.config(state='disabled')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def rafraichir(self):
        """Rafraîchit toutes les données et visualisations"""
        self.charger_donnees()
        messagebox.showinfo("Info", "Données rafraîchies avec succès!")

    def sauvegarder_graphiques(self):
        """Sauvegarde tous les graphiques"""
        try:
            output_path = Path('graphiques_complets.png')
            self.main_figure.savefig(output_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Succès", f"Graphiques sauvegardés dans {output_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")


def main():
    root = tk.Tk()
    app = VisualiseurGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
