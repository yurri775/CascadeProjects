#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour les types d'événements.
"""
from src.simulation.event import Event, EventType, EventFactory
from src.simulation.event import DemandEvent, BargeEvent, TerminalEvent, ServiceEvent, SimulationEvent
from src.simulation.event_scheduler import EventScheduler

def test_event_types():
    """
    Teste les différents types d'événements.
    """
    print("=== Test des types d'événements ===")
    
    # Créer des événements de différents types
    print("Création d'événements de différents types...")
    
    # Événement de demande
    demand_event = DemandEvent(
        time=10.0,
        event_type=EventType.DEMAND_ARRIVAL,
        demand_id="D1",
        volume=50,
        origin="A",
        destination="B"
    )
    print(f"Événement de demande: {demand_event}")
    print(f"  Ressource: {demand_event.get_resource()}")
    print(f"  Quantité: {demand_event.get_quantity()}")
    print(f"  Origine: {demand_event.origin}")
    print(f"  Destination: {demand_event.destination}")
    
    # Événement de barge
    barge_event = BargeEvent(
        time=15.0,
        event_type=EventType.BARGE_DEPARTURE,
        barge_id="B1",
        origin="A",
        destination="B",
        load=75
    )
    print(f"\nÉvénement de barge: {barge_event}")
    print(f"  Ressource: {barge_event.get_resource()}")
    print(f"  Quantité: {barge_event.get_quantity()}")
    print(f"  Origine: {barge_event.get_location()}")
    print(f"  Destination: {barge_event.get_destination()}")
    
    # Événement de terminal
    terminal_event = TerminalEvent(
        time=20.0,
        event_type=EventType.TERMINAL_CONGESTION,
        terminal_id="T1",
        capacity=100
    )
    print(f"\nÉvénement de terminal: {terminal_event}")
    print(f"  Ressource: {terminal_event.get_resource()}")
    print(f"  Quantité: {terminal_event.get_quantity()}")
    
    # Événement de service
    service_event = ServiceEvent(
        time=25.0,
        event_type=EventType.SERVICE_START,
        service_id="S1",
        capacity=200,
        origin="A",
        destination="C"
    )
    print(f"\nÉvénement de service: {service_event}")
    print(f"  Ressource: {service_event.get_resource()}")
    print(f"  Quantité: {service_event.get_quantity()}")
    print(f"  Origine: {service_event.origin}")
    print(f"  Destination: {service_event.destination}")
    
    # Événement de simulation
    simulation_event = SimulationEvent(
        time=30.0,
        event_type=EventType.SIMULATION_END,
        duration=100
    )
    print(f"\nÉvénement de simulation: {simulation_event}")
    print(f"  Durée: {simulation_event.get_duration()}")
    
    print("\n" + "-" * 80 + "\n")

def test_event_factory():
    """
    Teste la factory d'événements.
    """
    print("=== Test de la factory d'événements ===")
    
    # Créer des événements avec la factory
    print("Création d'événements avec la factory...")
    
    # Événement d'arrivée de demande
    demand_arrival = EventFactory.create_demand_arrival(
        time=5.0,
        demand_id="D1",
        volume=50,
        origin="A",
        destination="B"
    )
    print(f"Événement d'arrivée de demande: {demand_arrival}")
    
    # Événement d'assignation de demande
    demand_assignment = EventFactory.create_demand_assignment(
        time=7.0,
        demand_id="D1",
        barge_id="B1"
    )
    print(f"Événement d'assignation de demande: {demand_assignment}")
    
    # Événement de départ de barge
    barge_departure = EventFactory.create_barge_departure(
        time=10.0,
        barge_id="B1",
        origin="A",
        destination="B",
        load=75
    )
    print(f"Événement de départ de barge: {barge_departure}")
    
    # Événement d'arrivée de barge
    barge_arrival = EventFactory.create_barge_arrival(
        time=15.0,
        barge_id="B1",
        terminal="B",
        load=75
    )
    print(f"Événement d'arrivée de barge: {barge_arrival}")
    
    # Événement de fin de chargement
    loading_complete = EventFactory.create_loading_complete(
        time=20.0,
        barge_id="B1",
        terminal="B",
        demands=["D1", "D2"]
    )
    print(f"Événement de fin de chargement: {loading_complete}")
    
    # Événement de fin de déchargement
    unloading_complete = EventFactory.create_unloading_complete(
        time=25.0,
        barge_id="B1",
        terminal="C",
        demands=["D1", "D2"]
    )
    print(f"Événement de fin de déchargement: {unloading_complete}")
    
    # Événement de fin de simulation
    simulation_end = EventFactory.create_simulation_end(
        time=100.0
    )
    print(f"Événement de fin de simulation: {simulation_end}")
    
    print("\n" + "-" * 80 + "\n")

def test_scheduler_with_typed_events():
    """
    Teste l'échéancier avec des événements typés.
    """
    print("=== Test de l'échéancier avec des événements typés ===")
    
    # Créer un échéancier
    scheduler = EventScheduler()
    print(f"Échéancier créé: {scheduler}")
    
    # Ajouter des événements avec les méthodes spécifiques
    print("Ajout d'événements avec les méthodes spécifiques...")
    
    scheduler.add_demand_arrival(
        time=5.0,
        demand_id="D1",
        volume=50,
        origin="A",
        destination="B"
    )
    
    scheduler.add_barge_departure(
        time=10.0,
        barge_id="B1",
        origin="A",
        destination="B",
        load=75
    )
    
    scheduler.add_barge_arrival(
        time=15.0,
        barge_id="B1",
        terminal="B",
        load=75
    )
    
    scheduler.add_loading_complete(
        time=20.0,
        barge_id="B1",
        terminal="B",
        demands=["D1", "D2"]
    )
    
    scheduler.add_unloading_complete(
        time=25.0,
        barge_id="B1",
        terminal="C",
        demands=["D1", "D2"]
    )
    
    scheduler.add_simulation_end(
        time=100.0
    )
    
    print(f"Après ajout d'événements: {scheduler}")
    
    # Récupérer tous les événements
    print("\nTous les événements:")
    for event in scheduler.get_all_events():
        print(f"  - {event}")
    
    # Récupérer les sacs d'événements un par un
    print("\nRécupération des sacs d'événements:")
    while not scheduler.is_empty():
        bag = scheduler.pop_next_event_bag()
        print(f"\nSac récupéré: {bag}")
        print("Événements dans le sac:")
        for event in bag:
            print(f"  - {event}")
        print(f"Temps courant: {scheduler.current_time}")
    
    print("\nÉchéancier vide:", scheduler.is_empty())
    
    print("\n" + "-" * 80 + "\n")

def main():
    """
    Fonction principale.
    """
    test_event_types()
    test_event_factory()
    test_scheduler_with_typed_events()

if __name__ == "__main__":
    main()
