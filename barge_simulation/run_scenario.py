#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour exécuter un scénario de simulation de barges à partir de fichiers d'entrée standardisés.
Format des fichiers:
    - <ID>_services.txt : liste des services ouverts pour le scénario numéro <ID>
    - <ID>_topologie.txt : topologie du réseau physique pour le scénario numéro <ID>
    - <ID>_flotte.txt : nombre et types des barges disponibles pour le scénario numéro <ID>
    - <ID>_demandes.txt : demandes de containers à transporter pour le scénario numéro <ID>
"""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
from src.model.service import Service
from src.model.demand import Demand
from src.model.network import SpaceTimeNetwork
from src.simulation.barge_simulator import BargeSimulator
from src.model.routing import RoutingManager
from src.model.barge import Barge

def load_topology(file_path):
    """
    Charge la topologie du réseau à partir d'un fichier.
    
    Args:
        file_path (str): Chemin vers le fichier de topologie
        
    Returns:
        SpaceTimeNetwork: Le réseau espace-temps
    """
    try:
        # Lire le fichier de topologie
        df = pd.read_csv(file_path, sep='\t')
        
        # Créer le réseau
        network = SpaceTimeNetwork()
        
        # Ajouter les terminaux
        terminals = set()
        for _, row in df.iterrows():
            terminals.add(str(row['origin']))
            terminals.add(str(row['destination']))
            
        for terminal in terminals:
            # Les coordonnées sont fictives pour l'instant
            network.add_terminal(terminal, (0, 0))
            
        # Ajouter les connexions
        for _, row in df.iterrows():
            origin = str(row['origin'])
            destination = str(row['destination'])
            distance = float(row['distance'])
            travel_time = float(row['travel_time'])
            
            network.add_connection(origin, destination, distance, travel_time)
            
        return network
    except Exception as e:
        print(f"Erreur lors du chargement de la topologie: {e}")
        return None

def load_services(file_path, network):
    """
    Charge les services à partir d'un fichier.
    
    Args:
        file_path (str): Chemin vers le fichier de services
        network (SpaceTimeNetwork): Le réseau espace-temps
        
    Returns:
        list: Liste des services
    """
    try:
        # Lire le fichier de services
        df = pd.read_csv(file_path, sep='\t')
        
        # Grouper par service_id
        services = []
        for service_id, group in df.groupby('id_service'):
            # Trier les legs par ordre
            group = group.sort_values('id_leg')
            
            # Extraire les informations du service
            legs = []
            for _, row in group.iterrows():
                # Trouver les terminaux correspondant à ce leg
                leg_id = row['id_leg']
                # Dans un cas réel, il faudrait extraire les terminaux de la topologie
                # Pour l'instant, on les génère à partir de l'ID du leg
                if leg_id < len(network.terminals) - 1:
                    origin = list(network.terminals.keys())[leg_id]
                    destination = list(network.terminals.keys())[leg_id + 1]
                    travel_time = network.get_travel_time(origin, destination)
                    legs.append((origin, destination, travel_time))
            
            # Créer le service
            if legs:
                service = Service(
                    service_id=f"S{service_id}",
                    origin=legs[0][0],
                    destination=legs[-1][1],
                    legs=legs,
                    start_time=float(group.iloc[0]['start_time']),
                    end_time=float(group.iloc[0]['start_time']) + float(group.iloc[0]['periode']),
                    vessel_types={"Standard": 1},  # Type de navire par défaut
                    capacity=float(group.iloc[0]['capacite'])
                )
                services.append(service)
        
        return services
    except Exception as e:
        print(f"Erreur lors du chargement des services: {e}")
        return []

def load_barges(file_path, services):
    """
    Charge les barges à partir d'un fichier.
    
    Args:
        file_path (str): Chemin vers le fichier de flotte
        services (list): Liste des services
        
    Returns:
        list: Liste des barges
    """
    try:
        # Lire le fichier de flotte
        df = pd.read_csv(file_path, sep='\t')
        
        # Créer les barges
        barges = []
        for _, row in df.iterrows():
            barge_id = f"B{row['id_barge']}"
            service_id = f"S{row['id_service']}" if 'id_service' in row else None
            capacity = float(row['capacite'])
            
            # Trouver le service correspondant
            service = None
            if service_id:
                for s in services:
                    if s.service_id == service_id:
                        service = s
                        break
            
            # Position initiale
            position = service.origin if service else list(row['position_initiale']) if 'position_initiale' in row else "0"
            
            # Créer la barge
            barge = Barge(
                barge_id=barge_id,
                capacity=capacity,
                position=position,
                service_id=service_id if service else None,
                loading_rate=10.0,  # Taux de chargement par défaut
                unloading_rate=10.0  # Taux de déchargement par défaut
            )
            barges.append(barge)
        
        return barges
    except Exception as e:
        print(f"Erreur lors du chargement des barges: {e}")
        return []

def load_demands(file_path):
    """
    Charge les demandes à partir d'un fichier.
    
    Args:
        file_path (str): Chemin vers le fichier de demandes
        
    Returns:
        list: Liste des demandes
    """
    try:
        # Lire le fichier de demandes
        df = pd.read_csv(file_path, sep='\t')
        
        # Créer les demandes
        demands = []
        for _, row in df.iterrows():
            demand_id = row['demand_id']
            origin = str(row['orig'])
            destination = str(row['dest'])
            volume = float(row['vol'])
            availability_time = float(row['t_resa'])
            due_date = float(row['t_due'])
            
            # Créer la demande
            demand = Demand(
                demand_id=demand_id,
                origin=origin,
                destination=destination,
                volume=volume,
                availability_time=availability_time,
                due_date=due_date
            )
            demands.append(demand)
        
        return demands
    except Exception as e:
        print(f"Erreur lors du chargement des demandes: {e}")
        return []

def visualize_network(network, output_file=None):
    """
    Visualise le réseau.
    
    Args:
        network (SpaceTimeNetwork): Le réseau à visualiser
        output_file (str, optional): Fichier de sortie pour la visualisation
    """
    # Créer un graphe NetworkX
    G = nx.DiGraph()
    
    # Ajouter les nœuds
    for terminal_id, terminal_data in network.terminals.items():
        G.add_node(terminal_id, pos=terminal_data['position'])
    
    # Ajouter les arêtes
    for origin, destinations in network.connections.items():
        for destination, connection_data in destinations.items():
            distance = connection_data['distance']
            travel_time = connection_data['travel_time']
            G.add_edge(origin, destination, weight=distance, label=f"{distance:.1f} km\n{travel_time:.1f} h")
    
    # Dessiner le graphe
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
    
    # Dessiner les arêtes
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrowsize=20)
    
    # Ajouter les labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')
    
    # Ajouter les poids des arêtes
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    plt.title("Réseau de Transport")
    plt.axis('off')
    
    # Enregistrer ou afficher
    if output_file:
        plt.savefig(output_file)
        print(f"Visualisation du réseau enregistrée dans '{output_file}'")
    else:
        plt.show()

def run_scenario(scenario_id, data_dir="data", output_dir="output", max_time=100):
    """
    Exécute un scénario de simulation.
    
    Args:
        scenario_id (str): Identifiant du scénario
        data_dir (str): Répertoire contenant les fichiers d'entrée
        output_dir (str): Répertoire pour les fichiers de sortie
        max_time (float): Temps maximum de simulation
    """
    print(f"\n=== Exécution du scénario {scenario_id} ===")
    print(f"Date d'exécution: {datetime.now()}")
    
    # Vérifier que les fichiers d'entrée existent
    topology_file = f"{data_dir}/{scenario_id}_topologie.txt"
    services_file = f"{data_dir}/{scenario_id}_services.txt"
    barges_file = f"{data_dir}/{scenario_id}_flotte.txt"
    demands_file = f"{data_dir}/{scenario_id}_demandes.txt"
    
    files_to_check = [topology_file, services_file, barges_file, demands_file]
    missing_files = [f for f in files_to_check if not os.path.exists(f)]
    
    if missing_files:
        print(f"\nErreur: Les fichiers suivants sont manquants:")
        for f in missing_files:
            print(f"  - {f}")
        return
    
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Fichiers de sortie
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    network_viz_file = f"{output_dir}/{scenario_id}_network.png"
    timeline_file = f"{output_dir}/{scenario_id}_timeline_{timestamp}.png"
    stats_file = f"{output_dir}/{scenario_id}_stats_{timestamp}.txt"
    
    print("\nChargement des données...")
    
    # Charger la topologie
    network = None
    try:
        network = load_topology(topology_file)
        if not network:
            raise ValueError("Impossible de charger la topologie")
    except Exception as e:
        print(f"Erreur lors du chargement de la topologie: {e}")
        print("Erreur: Impossible de charger la topologie du réseau.")
        return
    
    print(f"\nRéseau chargé: {len(network.terminals)} terminaux, {sum(len(dests) for dests in network.connections.values())} connexions")
    
    # Charger les services
    services = []
    try:
        services = load_services(services_file, network)
        print(f"Services chargés: {len(services)}")
    except Exception as e:
        print(f"Erreur lors du chargement des services: {e}")
        return
    
    # Charger les barges
    barges = []
    try:
        barges = load_barges(barges_file, services)
        print(f"Barges chargées: {len(barges)}")
    except Exception as e:
        print(f"Erreur lors du chargement des barges: {e}")
        return
    
    # Charger les demandes
    demands = []
    try:
        demands = load_demands(demands_file)
        print(f"Demandes chargées: {len(demands)}")
    except Exception as e:
        print(f"Erreur lors du chargement des demandes: {e}")
        return
    
    # Visualiser le réseau
    visualize_network(network, network_viz_file)
    
    # Créer le gestionnaire de routage
    routing_manager = RoutingManager()
    
    # Ajouter les services au gestionnaire de routage
    for service in services:
        routing_manager.add_service(service)
    
    # Créer le simulateur
    simulator = BargeSimulator(network, routing_manager)
    
    # Ajouter les barges
    for barge in barges:
        simulator.add_barge(barge)
    
    # Ajouter les demandes
    for demand in demands:
        simulator.add_demand(demand)
    
    # Exécuter la simulation
    print("\nDémarrage de la simulation...")
    simulator.run(until=max_time)
    
    # Récupérer les statistiques
    stats = simulator.get_statistics()
    
    # Afficher les résultats
    print("\nSimulation terminée!")
    print(f"\nStatistiques de la simulation:")
    print(f"Temps de simulation: {stats['simulation_time']:.2f}")
    print(f"Événements traités: {stats['events_processed']}")
    print(f"Distance totale parcourue: {stats['total_distance']:.2f}")
    
    print("\nStatistiques des barges:")
    for barge_id, barge_stats in stats['barge_statistics'].items():
        print(f"Barge {barge_id}: Position={barge_stats['position']}, Charge={barge_stats['load']}, Status={barge_stats['status']}")
    
    print("\nStatistiques des demandes:")
    demand_stats = stats['demand_statistics']
    print(f"Total: {demand_stats['total']}")
    print(f"Complétées: {demand_stats['completed']}")
    print(f"En cours: {demand_stats['in_progress']}")
    print(f"En attente: {demand_stats['pending']}")
    print(f"Assignées: {demand_stats['assigned']}")
    print(f"Échouées: {demand_stats['failed']}")
    
    # Enregistrer les résultats
    results_file = f"{output_dir}/{scenario_id}_results.txt"
    with open(results_file, 'w') as f:
        f.write(f"=== Résultats de la simulation du scénario {scenario_id} ===\n")
        f.write(f"Date d'exécution: {datetime.now()}\n\n")
        
        f.write(f"Statistiques de la simulation:\n")
        f.write(f"Temps de simulation: {stats['simulation_time']:.2f}\n")
        f.write(f"Événements traités: {stats['events_processed']}\n")
        f.write(f"Distance totale parcourue: {stats['total_distance']:.2f}\n\n")
        
        f.write(f"Statistiques des barges:\n")
        for barge_id, barge_stats in stats['barge_statistics'].items():
            f.write(f"Barge {barge_id}: Position={barge_stats['position']}, Charge={barge_stats['load']}, Status={barge_stats['status']}\n")
        
        f.write(f"\nStatistiques des demandes:\n")
        f.write(f"Total: {demand_stats['total']}\n")
        f.write(f"Complétées: {demand_stats['completed']}\n")
        f.write(f"En cours: {demand_stats['in_progress']}\n")
        f.write(f"En attente: {demand_stats['pending']}\n")
        f.write(f"Assignées: {demand_stats['assigned']}\n")
        f.write(f"Échouées: {demand_stats['failed']}\n")
    
    print(f"\nRésultats enregistrés dans {results_file}")

def main():
    """
    Fonction principale.
    """
    # Vérifier les arguments
    if len(sys.argv) < 2:
        print("Usage: python run_scenario.py <scenario_id> [data_dir] [output_dir] [max_time]")
        print("  scenario_id: Identifiant du scénario")
        print("  data_dir: Répertoire contenant les fichiers d'entrée (défaut: data)")
        print("  output_dir: Répertoire pour les fichiers de sortie (défaut: output)")
        print("  max_time: Temps maximum de simulation (défaut: 100)")
        return
    
    # Récupérer les arguments
    scenario_id = sys.argv[1]
    data_dir = sys.argv[2] if len(sys.argv) > 2 else "data"
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    max_time = float(sys.argv[4]) if len(sys.argv) > 4 else 100.0
    
    # Exécuter le scénario
    run_scenario(scenario_id, data_dir, output_dir, max_time)

if __name__ == "__main__":
    main()
