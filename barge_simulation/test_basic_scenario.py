from src.model.network import Network
from src.model.service import Service
from datetime import datetime

def create_test_network():
    """Crée un réseau de test avec 4 terminaux (A, B, C, D)."""
    network = Network(cycle_length=14)  # 14 demi-journées = 1 semaine
    
    # Ajouter les terminaux
    for terminal in ['A', 'B', 'C', 'D']:
        network.add_terminal(terminal)
    
    # Créer le service 1 (A -> B -> C)
    service1 = Service(
        service_id="S1",
        origin="A",
        destination="C",
        legs=[
            ("A", "B", 2),  # 1 journée de A à B
            ("B", "C", 2)   # 1 journée de B à C
        ],
        start_time=0,
        end_time=4,
        vessel_types={"large": 1, "small": 1},  # 1 grande barge (25 TEU) + 1 petite (10 TEU)
        capacity=35  # 25 + 10 TEU
    )
    
    # Créer le service 2 (D -> C -> B)
    service2 = Service(
        service_id="S2",
        origin="D",
        destination="B",
        legs=[
            ("D", "C", 2),
            ("C", "B", 2)
        ],
        start_time=2,
        end_time=6,
        vessel_types={"medium": 2},  # 2 barges moyennes (15 TEU chacune)
        capacity=30  # 2 * 15 TEU
    )
    
    # Ajouter les services au réseau
    network.add_service(service1)
    network.add_service(service2)
    
    return network

def test_demand_routing():
    """Teste le routage des demandes."""
    network = create_test_network()
    
    # Test pour une demande de A vers C
    route = network.get_route(
        origin="A",
        destination="C",
        earliest_departure=0,
        latest_arrival=8
    )
    
    print("\nTest de routage A -> C:")
    if route:
        print("Route trouvée:")
        for terminal, time, service_id in route:
            print(f"  {terminal} à t={time} via service {service_id}")
    else:
        print("Aucune route trouvée")
    
    # Test pour une demande de D vers B
    route = network.get_route(
        origin="D",
        destination="B",
        earliest_departure=2,
        latest_arrival=12
    )
    
    print("\nTest de routage D -> B:")
    if route:
        print("Route trouvée:")
        for terminal, time, service_id in route:
            print(f"  {terminal} à t={time} via service {service_id}")
    else:
        print("Aucune route trouvée")

def main():
    print("=== Test du scénario de base ===")
    print(f"Exécution: {datetime.now()}\n")
    
    test_demand_routing()

if __name__ == "__main__":
    main()
