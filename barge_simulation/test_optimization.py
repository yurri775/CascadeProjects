#!/usr/bin/env python3
"""
Test de l'optimisation des assignations et de la gestion des capacités.
"""
from src.model.network import Network
from src.model.demand import Demand
from src.model.service import Service
from src.optimization.assignment_optimizer import AssignmentOptimizer

def create_test_scenario():
    """Crée un scénario de test avec réseau, services et demandes."""
    # Créer le réseau
    network = Network(schedule_length=13)
    
    # Ajouter les terminaux
    terminals = ['A', 'B', 'C', 'D']
    for terminal in terminals:
        network.add_physical_node(terminal, "terminal", capacity=50)
    
    # Ajouter les connexions (bidirectionnelles)
    connections = [
        ('A', 'B', 4), ('B', 'C', 4),
        ('C', 'D', 4), ('B', 'D', 2)
    ]
    for from_node, to_node, travel_time in connections:
        network.add_physical_edge(from_node, to_node, distance=travel_time*10, travel_time=travel_time)
        network.add_physical_edge(to_node, from_node, distance=travel_time*10, travel_time=travel_time)
    
    # Créer le réseau temps-espace
    network.create_time_space_network()
    network.create_all_paths()
    
    # Créer les services
    services = [
        Service("S1", "A", "D", ["A", "B", "C", "D"], 0, 6, "Large", 35),
        Service("S2", "D", "B", ["D", "B"], 0, 3, "Medium", 30),
        Service("S3", "B", "D", ["B", "D"], 4, 7, "Small", 10),
        Service("S4", "A", "C", ["A", "C"], 6, 9, "Medium", 15),
        Service("S5", "D", "B", ["D", "C", "B"], 7, 12, "Large", 25),
        Service("S6", "C", "A", ["C", "A"], 10, 13, "Small", 20)
    ]
    
    # Créer les demandes
    demands = [
        # Demandes régulières (prioritaires)
        Demand("3R", "A", "C", 20, 2, 13, customer_type="R", fare_class="E"),  # Express
        Demand("4R", "D", "B", 18, 0, 12, customer_type="R", fare_class="S"),  # Standard
        
        # Demandes complètes
        Demand("1F", "A", "D", 13, 0, 8, customer_type="F", fare_class="E"),   # Express
        Demand("5F", "B", "D", 15, 3, 10, customer_type="F", fare_class="S"),  # Standard
        
        # Demandes partielles
        Demand("2P", "D", "B", 15, 11, 1, customer_type="P", fare_class="E"),  # Express
        Demand("6P", "C", "A", 10, 8, 13, customer_type="P", fare_class="S")   # Standard
    ]
    
    return network, services, demands

def test_optimization():
    """Test l'optimisation des assignations."""
    print("=== Test d'optimisation des assignations ===\n")
    
    # Créer le scénario
    network, services, demands = create_test_scenario()
    
    # Créer l'optimiseur
    optimizer = AssignmentOptimizer()
    
    # Optimiser les assignations
    print("Optimisation des assignations...")
    assignments = optimizer.optimize_assignments(demands, services, network)
    
    # Afficher les résultats
    print("\nAssignations des demandes:")
    for demand_id, service_id in assignments.items():
        demand = next(d for d in demands if d.demand_id == demand_id)
        service = next(s for s in services if s.service_id == service_id)
        print(f"\nDemande {demand_id}:")
        print(f"  Type: {demand.customer_type} ({demand.fare_class})")
        print(f"  Volume: {demand.volume} TEUs")
        print(f"  Assignée au service {service_id}")
        print(f"  Trajet: {' -> '.join(service.route)}")
        print(f"  Départ: t={service.departure_time}, Arrivée: t={service.arrival_time}")
    
    # Afficher l'utilisation des services
    print("\nUtilisation des services:")
    utilization = optimizer.get_service_utilization(services)
    for service_id, usage in utilization.items():
        service = next(s for s in services if s.service_id == service_id)
        print(f"Service {service_id}: {usage:.1f}% "
              f"({optimizer.service_loads.get(service_id, 0)}/{service.capacity} TEUs)")
    
    # Afficher les demandes non assignées
    unassigned = [d for d in demands if d.demand_id not in assignments]
    if unassigned:
        print("\nDemandes non assignées:")
        for demand in unassigned:
            print(f"- Demande {demand.demand_id}: {demand.origin}->{demand.destination}, "
                  f"Type: {demand.customer_type} ({demand.fare_class})")

if __name__ == "__main__":
    test_optimization()
