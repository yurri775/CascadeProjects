import pandas as pd
from src.model.network import Network
from src.model.service import Service
from datetime import datetime

def load_services(file_path):
    """Charge les services depuis le fichier."""
    df = pd.read_csv(file_path, sep='\t')
    services = {}
    
    # Grouper par service_id pour obtenir tous les legs
    for service_id, group in df.groupby('id_service'):
        legs = []
        first_row = group.iloc[0]
        
        # Créer la liste des legs
        for i in range(len(group) - 1):
            legs.append((
                str(i),  # terminal de départ
                str(i + 1),  # terminal d'arrivée
                6  # durée fixe de 6 demi-journées pour commencer
            ))
        
        # Créer le service
        service = Service(
            service_id=str(service_id),
            origin="0",  # Premier terminal
            destination=str(len(group) - 1),  # Dernier terminal
            legs=legs,
            start_time=first_row['start_time'],
            end_time=first_row['start_time'] + first_row['periode'],
            vessel_types={"large": 1},  # Simplifié pour le test
            capacity=first_row['capacite']
        )
        
        services[str(service_id)] = service
    
    return services

def load_demands(file_path):
    """Charge les demandes depuis le fichier."""
    return pd.read_csv(file_path, sep='\t')

def main():
    print("=== Test avec données réelles ===")
    print(f"Exécution: {datetime.now()}\n")
    
    # Créer le réseau
    network = Network(cycle_length=24)  # 24 demi-journées
    
    # Ajouter les terminaux (0 à 3)
    for i in range(4):
        network.add_terminal(str(i))
    
    # Charger les services
    services = load_services('data/fichier_services_4_1_12_52.txt')
    for service in services.values():
        network.add_service(service)
    
    # Charger les demandes
    demands = load_demands('data/fichier_demande_4_1_12_52.txt')
    
    print("Services chargés:")
    for service_id, service in services.items():
        print(f"\nService {service_id}:")
        print(f"  Origine: {service.origin}")
        print(f"  Destination: {service.destination}")
        print(f"  Capacité: {service.capacity} TEUs")
        print(f"  Legs: {service.legs}")
    
    print("\nDemandes chargées:")
    for _, row in demands.iterrows():
        print(f"\nDemande {row['demand_id']}:")
        print(f"  Origine: {row['orig']} -> Destination: {row['dest']}")
        print(f"  Volume: {row['vol']} TEUs")
        print(f"  Réservation: t={row['t_resa']}, Due: t={row['t_due']}")
        
        # Chercher une route possible
        route = network.get_route(
            origin=str(row['orig']),
            destination=str(row['dest']),
            earliest_departure=row['t_resa'],
            latest_arrival=row['t_due']
        )
        
        if route:
            print("  Route trouvée:")
            for terminal, time, service_id in route:
                print(f"    {terminal} à t={time} via service {service_id}")
        else:
            print("  Aucune route trouvée")

if __name__ == "__main__":
    main()
