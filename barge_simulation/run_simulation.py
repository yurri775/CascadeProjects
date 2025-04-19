#!/usr/bin/env python3
"""
Module pour exécuter une simulation simplifiée du système de barges.
"""

from src.model.barge import Barge
from src.model.network import SpaceTimeNetwork
from src.model.service import Service
from src.model.routing import RoutingManager
from src.model.demand import Demand, DemandManager
from src.simulation.barge_simulator import BargeSimulator
from src.simulation.event import Event, EventType

def __init__(self, network=None, routing_manager=None, **kwargs):
    # ... autres initialisations ...
    
    self.stats = {
        "total_distance": 0,
        "events_processed": 0,
        "total_teus_transported": 0,
        "service_utilization": {},
        "terminal_utilization": {}
    }
    
    # Alias pour compatibilité
    self.statistics = self.stats

def create_sample_network():
    """Crée un réseau de test avec des terminaux et des connexions."""
    network = SpaceTimeNetwork()
    
    # Ajouter les nœuds (terminaux et intersections)
    terminals = {
        'A': (0, 0),   # Terminal A
        'B': (10, 0),  # Terminal B
        'C': (20, 0),  # Terminal C
        'D': (30, 0),  # Terminal D
    }
    
    # Ajouter les nœuds avec leurs positions
    for node_id, pos in terminals.items():
        network.add_node(node_id, pos, 'port', capacity=2)
    
    # Ajouter les arêtes avec les temps de trajet
    edges = [
        ('A', 'B', 4),  # Route directe A vers B
        ('B', 'C', 4),  # Route directe B vers C
        ('C', 'D', 4),  # Route directe C vers D
        ('D', 'C', 4),  # Route directe D vers C
        ('C', 'B', 4),  # Route directe C vers B
        ('B', 'A', 4)   # Route directe B vers A
    ]
    
    for from_node, to_node, travel_time in edges:
        network.add_edge(from_node, to_node, travel_time)
    
    return network

def create_services():
    """Crée des services pour le réseau."""
    # Service montant: A -> B -> C -> D
    legs1 = [('A', 'B', 4), ('B', 'C', 4), ('C', 'D', 4)]
    service1 = Service(
        service_id='S1',
        origin='A',
        destination='D',
        legs=legs1,
        start_time=0,
        end_time=24,
        vessel_types={'Medium': 2},
        capacity=30
    )
    
    # Service descendant: D -> C -> B -> A
    legs2 = [('D', 'C', 4), ('C', 'B', 4), ('B', 'A', 4)]
    service2 = Service(
        service_id='S2',
        origin='D',
        destination='A',
        legs=legs2,
        start_time=0,
        end_time=24,
        vessel_types={'Medium': 2},
        capacity=30
    )
    
    return [service1, service2]

def create_demands():
    """Crée des demandes de transport d'exemple."""
    demands = [
        Demand('D1', 'A', 'C', 10, 0, due_date=10),  # De A vers C, arrivée à t=0
        Demand('D2', 'B', 'D', 15, 5, due_date=15),  # De B vers D, arrivée à t=5
        Demand('D3', 'D', 'A', 20, 10, due_date=20)  # De D vers A, arrivée à t=10
    ]
    return demands

def main():
    # Créer le réseau
    network = create_sample_network()
    
    # Créer le gestionnaire de routage
    routing_manager = RoutingManager()
    
    # Créer le simulateur
    simulator = BargeSimulator(network, routing_manager)
    
    # Ajout d'un alias statistics -> stats pour compatibilité
    if not hasattr(simulator, 'statistics') and hasattr(simulator, 'stats'):
        simulator.statistics = simulator.stats
    
    # Créer et ajouter les services
    services = create_services()
    for service in services:
        simulator.add_service(service)
    
    # Créer et ajouter les barges
    barges = [
        Barge('B1', capacity=100, position='A', service_id='S1'),
        Barge('B2', capacity=150, position='D', service_id='S2')
    ]
    
    for barge in barges:
        simulator.add_barge(barge)
    
    # Créer et ajouter les demandes
    demands = create_demands()
    for demand in demands:
        # Ajouter un événement pour l'arrivée de la demande
        simulator.add_event(
            demand.arrival_time,  # Ou assurez-vous que availability_time est défini
            EventType.DEMAND_ARRIVAL,
            {'demand': demand}
        )
    
    # Exécuter la simulation
    print("Démarrage de la simulation...")
    
    # On désactive la collecte des statistiques pour simplifier
    simulator.run(until=50)
    
    print("Simulation terminée!")
    
    # Afficher les statistiques
    try:
        events_processed = getattr(simulator, 'events_processed', 0)
        if hasattr(simulator, 'statistics'):
            stats = simulator.statistics
        elif hasattr(simulator, 'stats'):
            stats = simulator.stats
        else:
            stats = {'total_distance': 0, 'events_processed': 0}
        
        print(f"Statistiques de la simulation:")
        print(f"Temps de simulation: {getattr(simulator, 'current_time', 0):.2f}")
        print(f"Événements traités: {stats.get('events_processed', events_processed)}")
        print(f"Distance totale parcourue: {stats.get('total_distance', 0):.2f}")
        
        # Essayer différentes approches pour obtenir les statistiques
        try:
            if hasattr(simulator, 'get_demand_statistics'):
                demand_statistics = simulator.get_demand_statistics()
            elif hasattr(simulator, 'demand_statistics'):
                demand_statistics = simulator.demand_statistics
            else:
                # Créer des statistiques par défaut
                demand_statistics = {
                    'total': len(simulator.demands),
                    'completed': sum(1 for d in simulator.demands.values() if d.status == 'completed'),
                    'pending': sum(1 for d in simulator.demands.values() if d.status == 'pending')
                }
        except Exception as e:
            print(f"Avertissement: Impossible d'obtenir les statistiques de demande: {e}")
            demand_statistics = {'total': 0, 'completed': 0, 'pending': 0, 'assigned': 0, 'failed': 0}
        
    except Exception as e:
        print(f"Erreur lors de l'affichage des statistiques: {e}")
        print("Statistiques non disponibles.")

if __name__ == "__main__":
    main()
