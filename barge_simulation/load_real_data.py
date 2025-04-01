"""
Module pour charger et traiter les données réelles de simulation.
"""
import pandas as pd
import numpy as np
from src.model.network import SpaceTimeNetwork
from src.model.service import Service
from src.model.barge import Barge
from src.model.demand import Demand

class RealDataLoader:
    """Chargeur de données réelles pour la simulation."""
    
    def __init__(self, data_dir):
        """
        Initialise le chargeur de données.
        
        Args:
            data_dir (str): Chemin vers le répertoire des données
        """
        self.data_dir = data_dir
        self.services_df = None
        self.demands_df = None
        self.paths_df = None
        self.results_df = None
        
    def load_data(self):
        """Charge toutes les données depuis les fichiers."""
        print(f"Chargement des données depuis {self.data_dir}")
        
        # Charger les services
        services_file = f"{self.data_dir}/fichier_services_4_1_12_52.txt"
        print(f"Lecture du fichier services: {services_file}")
        self.services_df = pd.read_csv(services_file, sep='\t')
        print(f"Nombre de services chargés: {len(self.services_df)}")
        
        # Charger les demandes
        demands_file = f"{self.data_dir}/fichier_demande_4_1_12_52.txt"
        print(f"Lecture du fichier demandes: {demands_file}")
        self.demands_df = pd.read_csv(demands_file, sep='\t')
        print(f"Nombre de demandes chargées: {len(self.demands_df)}")
        
        # Charger les chemins
        paths_file = f"{self.data_dir}/fichier_demandes_chemin_4_1_12_52.txt"
        print(f"Lecture du fichier chemins: {paths_file}")
        self.paths_df = pd.read_csv(paths_file, sep='\t')
        print(f"Nombre de chemins chargés: {len(self.paths_df)}")
        
        # Charger les résultats
        results_file = f"{self.data_dir}/Resultat_4_1_12_52.txt"
        print(f"Lecture du fichier résultats: {results_file}")
        self.results_df = pd.read_csv(results_file, sep='\t')
        print(f"Résultats chargés: {len(self.results_df)} lignes")
    
    def create_network(self):
        """
        Crée le réseau basé sur les données réelles.
        
        Returns:
            SpaceTimeNetwork: Le réseau créé
        """
        print("\nCréation du réseau...")
        network = SpaceTimeNetwork()
        
        # Positions des terminaux (approximatives basées sur le réseau)
        terminals = {
            '0': (0, 0),     # Terminal 0
            '1': (10, 20),   # Terminal 1
            '2': (20, 10),   # Terminal 2
            '3': (30, 0),    # Terminal 3
        }
        
        # Ajouter les nœuds
        print("Ajout des terminaux:")
        for node_id, pos in terminals.items():
            print(f"  Terminal {node_id} à la position {pos}")
            network.add_node(node_id, pos, 'port', capacity=50)
        
        # Ajouter les arêtes
        print("\nAjout des connexions:")
        for from_id in terminals.keys():
            for to_id in terminals.keys():
                if from_id != to_id:
                    print(f"  Connexion {from_id} -> {to_id}")
                    network.add_edge(from_id, to_id, 1)  # temps de trajet = 1
        
        return network
        
    def create_services(self):
        """
        Crée les services basés sur les données réelles.
        
        Returns:
            list[Service]: Liste des services créés
        """
        print("\nCréation des services...")
        services = []
        unique_services = self.services_df[['id_service', 'periode']].drop_duplicates()
        print(f"Nombre de services uniques: {len(unique_services)}")
        
        for _, row in unique_services.iterrows():
            service_id = row['id_service']
            period = row['periode']
            service_data = self.services_df[
                (self.services_df['id_service'] == service_id) & 
                (self.services_df['periode'] == period)
            ]
            
            # Créer la route du service
            legs = []
            for _, leg in service_data.iterrows():
                from_terminal = str(leg['id_leg'])
                to_terminal = str((int(leg['id_leg']) + 1) % 4)
                duration = 6  # Durée fixe pour chaque leg
                legs.append((from_terminal, to_terminal, duration))
            
            # Calculer la capacité du service
            initial_capacity = service_data['capacite'].iloc[0]  # Capacité initiale du service
            residual_capacity = service_data['cap_resid'].min()  # Capacité résiduelle minimale
            
            print(f"  Service S{service_id}_{period}: Legs = {legs}, Capacité = {initial_capacity} (Résiduelle: {residual_capacity})")
            
            # Créer le service avec tous les paramètres requis
            service = Service(
                service_id=f"S{service_id}_{period}",
                origin=legs[0][0],
                destination=legs[-1][1],
                legs=legs,
                start_time=0,  # Temps de début par défaut
                end_time=24,   # Temps de fin par défaut
                vessel_types={"standard": 1},  # Type de barge par défaut
                capacity=initial_capacity
            )
            services.append(service)
        
        return services
    
    def create_demands(self):
        """
        Crée les demandes basées sur les données réelles.
        
        Returns:
            list[Demand]: Liste des demandes créées
        """
        demands = []
        
        for _, row in self.demands_df.iterrows():
            # Créer une demande avec les paramètres requis
            demand = Demand(
                demand_id=f"D{len(demands)}_{row['cat']}",  # Inclure la catégorie dans l'ID
                origin=str(row['orig']),
                destination=str(row['dest']),
                volume=row['vol'],
                availability_time=row['t_resa'],
                due_date=row['t_due'],
                customer_type=row['cat'],  # Catégorie (F, R, P)
                fare_class='S',  # Standard par défaut
                unit_fare=1.0,  # Tarif unitaire par défaut
                container_type='Standard'  # Type de conteneur par défaut
            )
            demands.append(demand)
        
        return demands
    
    def create_barges(self, services):
        """
        Crée les barges basées sur les services.
        
        Args:
            services (list[Service]): Liste des services disponibles
            
        Returns:
            list[Barge]: Liste des barges créées
        """
        print("\nCréation des barges...")
        barges = []
        
        for service in services:
            # Extraire la capacité du service correspondant dans les données
            service_data = self.services_df[self.services_df['id_service'] == int(service.service_id.split('_')[0][1:])]
            service_capacity = service_data['capacite'].iloc[0]
            
            # Créer une barge avec la même capacité que son service
            barge = Barge(
                barge_id=f"B{len(barges)}",
                capacity=service_capacity,
                position=service.origin,  # Position initiale
                service_id=service.service_id
            )
            print(f"  Barge {barge.barge_id}: Service = {service.service_id}, Capacité = {barge.capacity}, Position = {barge.position}")
            barges.append(barge)
        
        return barges
