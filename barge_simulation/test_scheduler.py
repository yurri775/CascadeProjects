#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour l'échéancier des événements.
"""
from src.simulation.event import Event
from src.simulation.event_scheduler import EventScheduler, EventBag

def test_event_bag():
    """
    Teste la classe EventBag.
    """
    print("=== Test de la classe EventBag ===")
    
    # Créer un sac d'événements
    bag = EventBag(10.0)
    print(f"Sac créé: {bag}")
    
    # Ajouter des événements
    event1 = Event(10.0, "test1", {"data": "test1"})
    event2 = Event(10.0, "test2", {"data": "test2"})
    
    bag.add_event(event1)
    bag.add_event(event2)
    
    print(f"Après ajout d'événements: {bag}")
    
    # Itérer sur les événements
    print("Événements dans le sac:")
    for event in bag:
        print(f"  - {event}")
    
    # Tester la comparaison
    bag2 = EventBag(5.0)
    print(f"Comparaison: {bag} > {bag2} = {bag > bag2}")
    
    print()

def test_event_scheduler():
    """
    Teste la classe EventScheduler.
    """
    print("=== Test de la classe EventScheduler ===")
    
    # Créer un échéancier
    scheduler = EventScheduler()
    print(f"Échéancier créé: {scheduler}")
    
    # Ajouter des événements
    print("Ajout d'événements...")
    event1 = scheduler.add_event(10.0, "test1", {"data": "test1"})
    event2 = scheduler.add_event(5.0, "test2", {"data": "test2"})
    event3 = scheduler.add_event(15.0, "test3", {"data": "test3"})
    event4 = scheduler.add_event(5.0, "test4", {"data": "test4"})
    event5 = scheduler.add_event(10.0, "test5", {"data": "test5"})
    
    print(f"Après ajout d'événements: {scheduler}")
    
    # Récupérer tous les événements
    print("Tous les événements:")
    for event in scheduler.get_all_events():
        print(f"  - {event}")
    
    # Récupérer les sacs d'événements un par un
    print("\nRécupération des sacs d'événements:")
    while not scheduler.is_empty():
        bag = scheduler.pop_next_event_bag()
        print(f"Sac récupéré: {bag}")
        print("Événements dans le sac:")
        for event in bag:
            print(f"  - {event}")
        print(f"Temps courant: {scheduler.current_time}")
        print()
    
    print("Échéancier vide:", scheduler.is_empty())
    
    print()

def test_event_insertion():
    """
    Teste l'insertion d'événements dans l'échéancier.
    """
    print("=== Test d'insertion d'événements ===")
    
    # Créer un échéancier
    scheduler = EventScheduler()
    
    # Ajouter des événements dans un ordre aléatoire
    times = [10.0, 5.0, 15.0, 7.5, 12.5, 20.0, 3.0, 18.0]
    for i, time in enumerate(times):
        scheduler.add_event(time, f"test{i+1}", {"data": f"test{i+1}"})
    
    print(f"Échéancier après insertion: {scheduler}")
    
    # Vérifier que les événements sont bien triés
    print("Événements triés par temps:")
    for event in scheduler.get_all_events():
        print(f"  - {event}")
    
    # Récupérer les sacs d'événements un par un
    print("\nRécupération des sacs d'événements:")
    while not scheduler.is_empty():
        bag = scheduler.pop_next_event_bag()
        print(f"Sac récupéré: {bag}")
        print(f"Temps courant: {scheduler.current_time}")
    
    print()

def test_simulation_example():
    """
    Teste un exemple simple de simulation.
    """
    print("=== Test d'un exemple simple de simulation ===")
    
    # Créer un échéancier
    scheduler = EventScheduler()
    
    # Ajouter des événements de simulation
    print("Ajout d'événements de simulation...")
    
    # Arrivée de demandes
    scheduler.add_event(0.0, "demand_arrival", {"demand_id": "D1"})
    scheduler.add_event(5.0, "demand_arrival", {"demand_id": "D2"})
    
    # Départs de barges
    scheduler.add_event(0.0, "barge_departure", {"barge_id": "B1", "from": "A", "to": "B"})
    scheduler.add_event(0.0, "barge_departure", {"barge_id": "B2", "from": "C", "to": "D"})
    
    # Arrivées de barges
    scheduler.add_event(2.0, "barge_arrival", {"barge_id": "B1", "terminal": "B"})
    scheduler.add_event(3.0, "barge_arrival", {"barge_id": "B2", "terminal": "D"})
    
    # Chargement et déchargement
    scheduler.add_event(2.5, "loading_complete", {"barge_id": "B1", "demands": ["D1"]})
    scheduler.add_event(3.5, "unloading_complete", {"barge_id": "B2", "demands": ["D2"]})
    
    # Fin de simulation
    scheduler.add_event(10.0, "simulation_end", {})
    
    print(f"Échéancier après insertion: {scheduler}")
    
    # Simuler l'exécution
    print("\nExécution de la simulation:")
    while not scheduler.is_empty():
        bag = scheduler.pop_next_event_bag()
        print(f"\nTemps: {scheduler.current_time}")
        print(f"Sac d'événements: {bag}")
        
        # Traiter les événements du sac
        for event in bag:
            print(f"  Traitement de l'événement: {event}")
            
            # Simuler l'ajout d'événements en réponse à certains événements
            if event.event_type == "barge_arrival":
                barge_id = event.data["barge_id"]
                terminal = event.data["terminal"]
                
                # Planifier un nouveau départ
                departure_time = scheduler.current_time + 1.0
                scheduler.add_event(departure_time, "barge_departure", {
                    "barge_id": barge_id,
                    "from": terminal,
                    "to": "X"  # Destination fictive
                })
                print(f"    -> Planification d'un départ pour {barge_id} à t={departure_time}")
            
            # Arrêter la simulation si c'est la fin
            if event.event_type == "simulation_end":
                print("    -> Fin de la simulation")
                break
    
    print("\nSimulation terminée!")
    print()

def main():
    """
    Fonction principale.
    """
    test_event_bag()
    test_event_scheduler()
    test_event_insertion()
    test_simulation_example()

if __name__ == "__main__":
    main()
