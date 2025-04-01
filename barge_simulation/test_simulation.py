#!/usr/bin/env python3
"""
Script de test pour la simulation de transport fluvial.
"""
from src.model.network import Network
from src.model.demand import Demand
from src.model.service import Service

def test_network_creation():
    """Test la création du réseau physique et temps-espace."""
    print("\n=== Test de création du réseau ===")
    
    # Créer le réseau avec un horizon de 13 périodes
    network = Network(schedule_length=13)
    
    # Ajouter les terminaux (A, B, C, D)
    terminals = ['A', 'B', 'C', 'D']
    for terminal in terminals:
        network.add_physical_node(terminal, "terminal", capacity=50)
        print(f"Terminal {terminal} ajouté")
    
    # Ajouter les connexions entre terminaux (bidirectionnelles)
    connections = [
        ('A', 'B', 4), ('B', 'C', 4),
        ('C', 'D', 4), ('B', 'D', 2)
    ]
    for from_node, to_node, travel_time in connections:
        # Ajouter la connexion dans les deux sens
        network.add_physical_edge(from_node, to_node, distance=travel_time*10, travel_time=travel_time)
        network.add_physical_edge(to_node, from_node, distance=travel_time*10, travel_time=travel_time)
        print(f"Connexions {from_node}-{to_node} et {to_node}-{from_node} ajoutées (temps: {travel_time})")
    
    # Créer le réseau temps-espace
    network.create_time_space_network()
    network.create_all_paths()
    print(f"Réseau temps-espace créé avec {len(network.time_space_nodes)} nœuds")
    print(f"Nombre total de chemins possibles : {len(network.time_space_edges)}")
    return network

def test_service_creation():
    """Test la création des services."""
    print("\n=== Test de création des services ===")
    
    # Créer les services selon le tableau
    services = [
        Service("S1", "A", "D", ["A", "B", "C", "D"], 0, 6, "Large", 35),
        Service("S2", "D", "B", ["D", "B"], 0, 3, "Medium", 30),
        Service("S3", "B", "D", ["B", "D"], 4, 7, "Small", 10),
        Service("S4", "A", "C", ["A", "C"], 6, 9, "Medium", 15),
        Service("S5", "D", "B", ["D", "C", "B"], 7, 12, "Large", 25),
        Service("S6", "C", "A", ["C", "A"], 10, 13, "Small", 20)
    ]
    
    for service in services:
        print(f"Service {service.service_id} créé: {service.origin}->{service.destination}")
        
        # Ajouter les temps aux terminaux
        for terminal in service.route:
            service.set_terminal_times(terminal, loading_time=1, unloading_time=1, waiting_time=0)
    
    return services

def test_demand_creation():
    """Test la création des demandes."""
    print("\n=== Test de création des demandes ===")
    
    # Créer les demandes selon le tableau
    demands = [
        Demand("1F", "A", "D", 13, 0, 8, customer_type="F"),
        Demand("2P", "D", "B", 15, 11, 1, customer_type="P"),
        Demand("3R", "A", "C", 20, 2, 13, customer_type="R"),
        Demand("4R", "D", "B", 18, 0, 12, customer_type="R")
    ]
    
    for demand in demands:
        print(f"Demande {demand.demand_id} créée: {demand.origin}->{demand.destination}")
        print(f"  Type: {demand.customer_type}, Volume: {demand.volume} TEUs")
        print(f"  Disponible: t={demand.availability_time}, Due: t={demand.due_date}")
    
    return demands

def test_service_assignment():
    """Test l'assignation des demandes aux services."""
    print("\n=== Test d'assignation des services ===")
    
    network = test_network_creation()
    services = test_service_creation()
    demands = test_demand_creation()
    
    print("\nRecherche des services possibles pour chaque demande:")
    for demand in demands:
        feasible_services = network.get_feasible_services(demand)
        print(f"\nDemande {demand.demand_id}:")
        if feasible_services:
            print(f"  Services possibles trouvés: {len(feasible_services)}")
            for service in feasible_services:
                print(f"  - Départ à t={service['departure_time']}, "
                      f"Arrivée à t={service['arrival_time']}, "
                      f"Durée={service['travel_time']}")
        else:
            print("  Aucun service possible trouvé")

if __name__ == "__main__":
    print("=== Démarrage des tests de simulation ===")
    test_service_assignment()
    print("\n=== Tests terminés ===")
