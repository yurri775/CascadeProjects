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
    demands = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 5:
                    demand_id = parts[0].strip()
                    origin = parts[1].strip()
                    destination = parts[2].strip()
                    volume = float(parts[3].strip())
                    arrival_time = float(parts[4].strip())
                    due_date = float(parts[5].strip()) if len(parts) > 5 else None
                    
                    # Utiliser arrival_time au lieu de availability_time
                    demands.append(Demand(
                        demand_id=demand_id,
                        origin=origin,
                        destination=destination,
                        volume=volume,
                        arrival_time=arrival_time,
                        due_date=due_date
                    ))
        print(f"Demandes chargées: {len(demands)}")
    except Exception as e:
        print(f"Erreur lors du chargement des demandes: {e}")
    return demands

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

def ensure_attributes(simulator):
    """Assure que tous les attributs nécessaires sont présents"""
    required_attrs = {
        'total_distance': 0,
        'events_processed': 0,
        'current_time': 0
    }
    
    for attr, default in required_attrs.items():
        if not hasattr(simulator, attr):
            if hasattr(simulator, 'stats') and attr in simulator.stats:
                setattr(simulator, attr, simulator.stats[attr])
            else:
                setattr(simulator, attr, default)

def print_statistics(simulator):
    """Imprime les statistiques de la simulation"""
    print("\nStatistiques de la simulation:")
    print(f"Temps de simulation: {simulator.current_time:.2f}")
    
    # Utilisation de getattr pour récupérer les attributs de façon sécurisée
    events_processed = getattr(simulator, 'events_processed', 0)
    print(f"Événements traités: {events_processed}")
    
    total_distance = getattr(simulator, 'total_distance', 0)
    if hasattr(simulator, 'stats') and 'total_distance' in simulator.stats:
        total_distance = simulator.stats['total_distance']
    print(f"Distance totale parcourue: {total_distance:.2f}")
    
    # Statistiques des demandes
    print("\nStatistiques des demandes:")
    demand_stats = {"total": 0, "completed": 0, "pending": 0, "assigned": 0, "failed": 0}
    
    # Tentative d'obtenir les statistiques depuis différentes sources
    try:
        if hasattr(simulator, 'demand_manager') and hasattr(simulator.demand_manager, 'get_demand_statistics'):
            demand_stats = simulator.demand_manager.get_demand_statistics()
        elif hasattr(simulator, 'demand_statistics'):
            demand_stats = simulator.demand_statistics
        elif hasattr(simulator, 'demands'):
            # Calcul manuel des statistiques
            demand_stats["total"] = len(simulator.demands)
            demand_stats["completed"] = sum(1 for d in simulator.demands.values() if getattr(d, 'status', '') == 'completed')
            demand_stats["assigned"] = sum(1 for d in simulator.demands.values() if getattr(d, 'status', '') == 'assigned')
            demand_stats["pending"] = sum(1 for d in simulator.demands.values() if getattr(d, 'status', '') == 'pending')
            demand_stats["failed"] = sum(1 for d in simulator.demands.values() if getattr(d, 'status', '') == 'failed')
    except Exception as e:
        print(f"Erreur lors de l'obtention des statistiques de demandes: {e}")
    
    # Affichage des statistiques
    print(f"Total: {demand_stats.get('total', 0)}")
    print(f"Complétées: {demand_stats.get('completed', 0)}")
    print(f"En attente: {demand_stats.get('pending', 0)}")
    print(f"Assignées: {demand_stats.get('assigned', 0)}")
    print(f"Échouées: {demand_stats.get('failed', 0)}")

def run_scenario(scenario_id, data_dir, output_dir, max_time=100):
    """Exécute un scénario avec logs détaillés."""
    print(f"\n=== Exécution du scénario {scenario_id} ===")
    print(f"Date d'exécution: {datetime.now()}")
    
    print("\nChargement des données...")
    try:
        network = load_topology(f"{data_dir}/{scenario_id}_topologie.txt")
        services = load_services(f"{data_dir}/{scenario_id}_services.txt", network)
        barges = load_barges(f"{data_dir}/{scenario_id}_flotte.txt", services)
        demands = load_demands(f"{data_dir}/{scenario_id}_demandes.txt")
        
        print(f"\nRéseau chargé: {len(network.terminals)} terminaux, {sum(len(dests) for dests in network.connections.values())} connexions")
        print(f"Services chargés: {len(services)}")
        print(f"Barges chargées: {len(barges)}")
        print(f"Demandes chargées: {len(demands)}")
        
        # Configuration du simulateur
        simulator = BargeSimulator(network, RoutingManager())
        
        # Assurer les attributs nécessaires
        ensure_attributes(simulator)
        
        # Ajout des composants avec logs
        for service in services:
            print(f"\nAjout du service {service.service_id}")
            print(f"  Route: {' -> '.join([leg[0] for leg in service.legs] + [service.legs[-1][1]])}")
            simulator.add_service(service)
            
        for barge in barges:
            print(f"\nAjout de la barge {barge.barge_id}")
            print(f"  Position: {barge.position}")
            print(f"  Capacité: {barge.capacity}")
            simulator.add_barge(barge)
        
        for demand in demands:
            print(f"\nAjout de la demande {demand.demand_id}")
            print(f"  Origine: {demand.origin}")
            print(f"  Destination: {demand.destination}")
            print(f"  Volume: {demand.volume}")
            simulator.add_demand(demand)
        
        print("\nDémarrage de la simulation...")
        simulator.run(until=max_time)
        
        print("\nSimulation terminée!")
        try:
            print_statistics(simulator)
        except Exception as e:
            print(f"Erreur lors de l'affichage des statistiques: {e}")
        
    except Exception as e:
        print(f"Erreur lors de l'exécution du scénario: {e}")

def get_statistics(self):
    """Retourne un dictionnaire de statistiques de simulation."""
    return {
        "simulation_time": self.current_time,
        "events_processed": self.events_processed,
        "processed_events_count": len(self.processed_events),
        "total_distance": self.stats.get("total_distance", 0),
        "total_teus": self.stats.get("total_teus_transported", 0),
        "barges": {b_id: {
            "position": b.position,
            "status": getattr(b, "status", "unknown"),
            "load": getattr(b, "current_load", 0)
        } for b_id, b in self.barges.items()},
        "demands_completed": sum(1 for d in self.demands.values() if getattr(d, "status", "") == "completed")
    }

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
