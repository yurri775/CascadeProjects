import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class DataAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.demands = None
        self.paths = None
        self.services = None
        self.results = None
        
    def read_demands(self):
        """Lit le fichier des demandes."""
        file_path = os.path.join(self.data_dir, "fichier_demande_4_1_12_52.txt")
        self.demands = pd.read_csv(file_path, sep='\t')
        print("\nAperçu des demandes:")
        print(f"Nombre total de demandes: {len(self.demands)}")
        print("\nColonnes disponibles:")
        print(self.demands.columns.tolist())
        print("\nPremières lignes:")
        print(self.demands.head())
        print("\nStatistiques descriptives:")
        print(self.demands.describe())
        
    def read_paths(self):
        """Lit le fichier des chemins."""
        file_path = os.path.join(self.data_dir, "fichier_demandes_chemin_4_1_12_52.txt")
        self.paths = pd.read_csv(file_path, sep='\t')
        print("\nAperçu des chemins:")
        print(f"Nombre total de chemins: {len(self.paths)}")
        print("\nColonnes disponibles:")
        print(self.paths.columns.tolist())
        print("\nPremières lignes:")
        print(self.paths.head())
        
    def read_services(self):
        """Lit le fichier des services."""
        file_path = os.path.join(self.data_dir, "fichier_services_4_1_12_52.txt")
        self.services = pd.read_csv(file_path, sep='\t')
        print("\nAperçu des services:")
        print(f"Nombre total de services: {len(self.services)}")
        print("\nColonnes disponibles:")
        print(self.services.columns.tolist())
        print("\nPremières lignes:")
        print(self.services.head())
        
    def read_results(self):
        """Lit le fichier des résultats."""
        file_path = os.path.join(self.data_dir, "Resultat_4_1_12_52.txt")
        with open(file_path, 'r') as f:
            self.results = f.read()
        print("\nRésultats:")
        print(self.results)
        
    def analyze_data(self):
        """Analyse les données et génère des statistiques."""
        if self.demands is not None:
            print("\nAnalyse des demandes:")
            
            # Statistiques sur les volumes
            print("\nStatistiques des volumes:")
            volume_stats = self.demands['vol'].describe()
            print(volume_stats)
            
            # Distribution des volumes
            plt.figure(figsize=(10, 6))
            sns.histplot(data=self.demands, x='vol', bins=20)
            plt.title('Distribution des volumes de demande')
            plt.xlabel('Volume')
            plt.ylabel('Nombre de demandes')
            plt.savefig('volume_distribution.png')
            plt.close()
            
            # Analyse par catégorie
            print("\nRépartition par catégorie:")
            cat_counts = self.demands['cat'].value_counts()
            print(cat_counts)
            
            # Visualisation des catégories
            plt.figure(figsize=(8, 6))
            cat_counts.plot(kind='bar')
            plt.title('Nombre de demandes par catégorie')
            plt.xlabel('Catégorie')
            plt.ylabel('Nombre de demandes')
            plt.tight_layout()
            plt.savefig('category_distribution.png')
            plt.close()
            
            # Taux de décision
            print("\nTaux de décision (acceptation):")
            decision_rate = (self.demands['decision'] == 1.0).mean() * 100
            print(f"{decision_rate:.2f}%")
            
            # Analyse des délais
            print("\nDélais moyens:")
            print(f"Délai disponibilité moyen: {self.demands['t_avl'].mean():.2f}")
            print(f"Délai dû moyen: {self.demands['t_due'].mean():.2f}")
            
            # Analyse origine-destination
            print("\nPaires Origine-Destination les plus fréquentes:")
            od_pairs = self.demands.groupby(['orig', 'dest']).size().sort_values(ascending=False)
            print(od_pairs.head(10))
            
            # Analyse des caractéristiques spéciales
            print("\nProportion de demandes anticipées:")
            anticipe_rate = (self.demands['anticipe'] == 1).mean() * 100
            print(f"{anticipe_rate:.2f}%")
            
            print("\nProportion de demandes urgentes:")
            urgente_rate = (self.demands['urgente'] == 1).mean() * 100
            print(f"{urgente_rate:.2f}%")
            
            # Analyse des tarifs
            print("\nDistribution des tarifs:")
            fare_stats = self.demands['fare'].value_counts()
            print(fare_stats)
            
        if self.services is not None:
            print("\nAnalyse des services:")
            # Afficher toutes les colonnes disponibles
            print("\nColonnes des services:")
            print(self.services.columns.tolist())
            
            # Statistiques descriptives pour toutes les colonnes numériques
            print("\nStatistiques descriptives des services:")
            print(self.services.describe())
            
        if self.paths is not None:
            print("\nAnalyse des chemins:")
            # Afficher toutes les colonnes disponibles
            print("\nColonnes des chemins:")
            print(self.paths.columns.tolist())
            
            # Statistiques descriptives pour toutes les colonnes numériques
            print("\nStatistiques descriptives des chemins:")
            print(self.paths.describe())

def main():
    data_dir = r"C:\Users\marwa\OneDrive\Desktop\CascadeProjects\logistics_simulation\20221004_Donnees_Simulation_Reelles_IWNET"
    analyzer = DataAnalyzer(data_dir)
    
    print("=== Lecture des données ===")
    analyzer.read_demands()
    analyzer.read_paths()
    analyzer.read_services()
    analyzer.read_results()
    
    print("\n=== Analyse des données ===")
    analyzer.analyze_data()

if __name__ == "__main__":
    main()
