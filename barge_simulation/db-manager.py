# src/utils/db_manager.py
from pymongo import MongoClient

class DBManager:
    def __init__(self):
        self.clients = {}
        self.dbs = {}
        
        # Connexion aux bases de données
        self.connect_to_db("eu-1", "localhost", 27020)
        self.connect_to_db("eu-2", "localhost", 27021)
        self.connect_to_db("asia-1", "localhost", 27030)
        self.connect_to_db("asia-2", "localhost", 27031)
        
    def connect_to_db(self, region, host, port):
        try:
            self.clients[region] = MongoClient(host, port)
            self.dbs[region] = self.clients[region]["barge_simulation"]
            print(f"Connexion à la base de données {region} établie")
        except Exception as e:
            print(f"Erreur de connexion à {region}: {e}")
            
    def save_demand(self, demand, region="eu-1"):
        """Sauvegarde une demande dans la base de données"""
        if region not in self.dbs:
            print(f"Région {region} non disponible")
            return False
            
        collection = self.dbs[region]["demands"]
        data = {
            "demand_id": demand.demand_id,
            "origin": demand.origin,
            "destination": demand.destination,
            "volume": demand.volume,
            "status": demand.status,
            "created_at": datetime.now()
        }
        
        result = collection.insert_one(data)
        return result.inserted_id
        
    def save_service(self, service, region="eu-1"):
        """Sauvegarde un service dans la base de données"""
        if region not in self.dbs:
            return False
            
        collection = self.dbs[region]["services"]
        data = {
            "service_id": service.service_id,
            "origin": service.origin,
            "destination": service.destination,
            "capacity": service.capacity,
            "route": service.route
        }
        
        result = collection.insert_one(data)
        return result.inserted_id
        
    def close(self):
        """Ferme toutes les connexions"""
        for client in self.clients.values():
            client.close()