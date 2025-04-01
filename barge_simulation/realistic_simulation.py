#!/usr/bin/env python3
"""
Simulation réaliste du système de barges basée sur le tableau de services fourni.
"""

from src.model.barge import Barge
from src.model.network import SpaceTimeNetwork
from src.model.service import Service
from src.model.routing import RoutingManager
from src.model.demand import Demand, DemandManager
from src.simulation.simulator import BargeSimulator
from src.simulation.event import Event
import matplotlib.pyplot as plt
import numpy as np

def create_realistic_network():
    """Crée un réseau basé sur le tableau des services réels."""
    network = SpaceTimeNetwork()
    
    # Définir les terminaux de base
    terminals = {
        'A': (0, 0),    # Terminal A
        'B': (10, 20),  # Terminal B
        'C': (20, 10),  # Terminal C
        'D': (30, 0),   # Terminal D
    }
    
    # Ajouter les nœuds avec leurs positions
    for node_id, pos in terminals.items():
        network.add_node(node_id, pos, 'port', capacity=2)
    
    # Ajouter les arêtes avec les temps de trajet (basés sur le tableau)
    edges = [
        ('A', 'B', 1),  # a1 : A-B travel time=1
        ('B', 'C', 1),  # a2 : B-C travel time=1
        ('C', 'D', 1),  # a3 : C-D travel time=1
        ('D', 'B', 2),  # a1 : D-B travel time=2
        ('B', 'D', 2),  # a1 : B-D travel time=2
        ('A', 'C', 2),  # a1 : A-C travel time=2
        ('D', 'C', 1),  # a1 : D-C travel time=1
        ('C', 'B', 1),  # a2 : C-B travel time=1
        ('C', 'A', 2),  # a1 : C-A travel time=2
    ]
    
    for from_node, to_node, travel_time in edges:
        network.add_edge(from_node, to_node, travel_time)
    
    return network

def create_realistic_services():
    """Crée des services basés sur le tableau fourni."""
    services = []
    
    # Service 1: A -> D (via B, C)
    legs1 = [('A', 'B', 1), ('B', 'C', 1), ('C', 'D', 1)]
    service1 = Service(
        service_id='1',
        origin='A',
        destination='D',
        legs=legs1,
        start_time=0,
        end_time=24,
        vessel_types={'Large': 1, 'Small': 1},
        capacity=35
    )
    
    # Service 2: D -> B
    legs2 = [('D', 'B', 2)]
    service2 = Service(
        service_id='2',
        origin='D',
        destination='B',
        legs=legs2,
        start_time=0,
        end_time=24,
        vessel_types={'Medium': 2},
        capacity=30
    )
    
    # Service 3: B -> D
    legs3 = [('B', 'D', 2)]
    service3 = Service(
        service_id='3',
        origin='B',
        destination='D',
        legs=legs3,
        start_time=0,
        end_time=24,
        vessel_types={'Small': 1},
        capacity=10
    )
    
    # Service 4: A -> C
    legs4 = [('A', 'C', 2)]
    service4 = Service(
        service_id='4',
        origin='A',
        destination='C',
        legs=legs4,
        start_time=0,
        end_time=24,
        vessel_types={'Medium': 1},
        capacity=15
    )
    
    # Service 5: D -> B (via C)
    legs5 = [('D', 'C', 1), ('C', 'B', 1)]
    service5 = Service(
        service_id='5',
        origin='D',
        destination='B',
        legs=legs5,
        start_time=0,
        end_time=24,
        vessel_types={'Large': 1},
        capacity=25
    )
    
    # Service 6: C -> A
    legs6 = [('C', 'A', 2)]
    service6 = Service(
        service_id='6',
        origin='C',
        destination='A',
        legs=legs6,
        start_time=0,
        end_time=24,
        vessel_types={'Small': 2},
        capacity=20
    )
    
    services = [service1, service2, service3, service4, service5, service6]
    return services

def create_realistic_barges():
    """Crée des barges basées sur les données du tableau."""
    barges = [
        # Service 1: A -> D
        Barge('B1-L', capacity=25, position='A', service_id='1'),
        Barge('B1-S', capacity=10, position='A', service_id='1'),
        
        # Service 2: D -> B
        Barge('B2-M1', capacity=15, position='D', service_id='2'),
        Barge('B2-M2', capacity=15, position='D', service_id='2'),
        
        # Service 3: B -> D
        Barge('B3-S', capacity=10, position='B', service_id='3'),
        
        # Service 4: A -> C
        Barge('B4-M', capacity=15, position='A', service_id='4'),
        
        # Service 5: D -> B (via C)
        Barge('B5-L', capacity=25, position='D', service_id='5'),
        
        # Service 6: C -> A
        Barge('B6-S1', capacity=10, position='C', service_id='6'),
        Barge('B6-S2', capacity=10, position='C', service_id='6')
    ]
    return barges

def create_realistic_demands():
    """Crée des demandes de transport réalistes pour la simulation."""
    demands = [
        # Demande 1: De A vers D
        Demand('D1', 'A', 'D', 20, 0, due_date=8),
        
        # Demande 2: De D vers B
        Demand('D2', 'D', 'B', 25, 1, due_date=5),
        
        # Demande 3: De B vers D
        Demand('D3', 'B', 'D', 5, 4, due_date=9),
        
        # Demande 4: De A vers C
        Demand('D4', 'A', 'C', 10, 6, due_date=10),
        
        # Demande 5: De D vers B via C
        Demand('D5', 'D', 'B', 15, 7, due_date=13),
        
        # Demande 6: De C vers A
        Demand('D6', 'C', 'A', 15, 10, due_date=14)
    ]
    return demands

def visualize_network(network, services):
    """Visualise le réseau et les services."""
    plt.figure(figsize=(12, 8))
    
    # Dessiner les nœuds
    for node_id, node_data in network.nodes.items():
        x, y = node_data['position']
        color = 'blue' if node_data['type'] == 'port' else 'green'
        plt.scatter(x, y, s=100, c=color, label=f"{node_id} ({node_data['type']})" if node_id == 'A' else "")
        plt.text(x, y + 1, node_id, fontsize=12, ha='center')
    
    # Dessiner les arêtes
    for (from_node, to_node), edge_data in network.edges.items():
        from_pos = network.nodes[from_node]['position']
        to_pos = network.nodes[to_node]['position']
        plt.arrow(from_pos[0], from_pos[1], 
                 (to_pos[0] - from_pos[0]) * 0.8, 
                 (to_pos[1] - from_pos[1]) * 0.8,
                 head_width=1, head_length=1, fc='black', ec='black', 
                 length_includes_head=True)
        
        # Ajouter le temps de voyage
        mid_x = (from_pos[0] + to_pos[0]) / 2
        mid_y = (from_pos[1] + to_pos[1]) / 2
        plt.text(mid_x, mid_y, f"{edge_data['travel_time']}", fontsize=10, 
                ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))
    
    # Dessiner les services
    colors = ['red', 'green', 'blue', 'purple', 'orange', 'brown']
    for i, service in enumerate(services):
        color = colors[i % len(colors)]
        route = service.route
        for j in range(len(route) - 1):
            from_pos = network.nodes[route[j]]['position']
            to_pos = network.nodes[route[j + 1]]['position']
            
            # Décaler légèrement pour distinguer les services
            offset = i * 0.5 - (len(services) - 1) * 0.25
            dx = to_pos[0] - from_pos[0]
            dy = to_pos[1] - from_pos[1]
            norm = np.sqrt(dx**2 + dy**2)
            
            if norm > 0:
                # Calculer les décalages perpendiculaires
                offset_x = -dy / norm * offset
                offset_y = dx / norm * offset
                
                # Dessiner la ligne de service
                plt.plot([from_pos[0] + offset_x, to_pos[0] + offset_x], 
                         [from_pos[1] + offset_y, to_pos[1] + offset_y], 
                         c=color, linewidth=2, alpha=0.7, 
                         label=f"Service {service.service_id}" if j == 0 else "")
    
    plt.title("Réseau de transport de barges avec services")
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.axis('equal')
    
    # Enregistrer l'image
    plt.savefig('network_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualisation du réseau enregistrée dans 'network_visualization.png'")

def main():
    """Fonction principale pour exécuter la simulation réaliste."""
    # Créer le réseau
    network = create_realistic_network()
    
    # Créer le gestionnaire de routage
    routing_manager = RoutingManager()
    
    # Créer les services
    services = create_realistic_services()
    
    # Visualiser le réseau et les services
    visualize_network(network, services)
    
    # Créer le simulateur
    simulator = BargeSimulator(network, routing_manager)
    
    # Ajouter les services au simulateur
    for service in services:
        simulator.add_service(service)
    
    # Créer et ajouter les barges
    barges = create_realistic_barges()
    for barge in barges:
        simulator.add_barge(barge)
    
    # Créer et ajouter les demandes
    demands = create_realistic_demands()
    for demand in demands:
        # Ajouter un événement pour l'arrivée de la demande
        simulator.add_event(
            demand.availability_time,
            Event.DEMAND_ARRIVAL,
            {'demand': demand}
        )
    
    # Exécuter la simulation
    print("Démarrage de la simulation réaliste...")
    simulator.run(until=50)
    print("Simulation terminée!")
    
    # Afficher les statistiques
    stats = simulator.get_statistics()
    print("\nStatistiques de la simulation:")
    print(f"Temps de simulation: {stats['current_time']}")
    print(f"Événements traités: {stats['events_processed']}")
    print(f"Distance totale parcourue: {stats['total_distance']}")
    
    # Statistiques sur les barges
    print("\nStatistiques des barges:")
    for barge_id, barge_stats in stats['barge_stats'].items():
        print(f"Barge {barge_id}: Position={barge_stats['current_position']}, "
              f"Charge={barge_stats['current_load']}, Status={barge_stats['status']}")
    
    # Statistiques sur les demandes
    demand_stats = stats['demand_stats']
    print("\nStatistiques des demandes:")
    print(f"Total: {demand_stats['total']}")
    print(f"Complétées: {demand_stats['completed']}")
    print(f"En cours: {demand_stats['in_progress']}")
    print(f"En attente: {demand_stats['pending']}")
    print(f"Assignées: {demand_stats['assigned']}")
    print(f"Échouées: {demand_stats['failed']}")

if __name__ == "__main__":
    main()
