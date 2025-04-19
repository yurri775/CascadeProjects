from pymongo import MongoClient
from datetime import datetime

class DBManager:
    def __init__(self):
        self.clients = {}
        self.dbs = {}
        self.enabled = False  # Par défaut, désactivé
        
    def enable(self):
        """Active la connexion à la base de données"""
        self.enabled = True
        try:
            self.connect_to_db("local", "localhost", 27017)
            return True
        except Exception as e:
            print(f"Erreur de connexion à MongoDB: {e}")
            self.enabled = False
            return False
        
    def connect_to_db(self, region, host, port):
        """Tente de se connecter à une base de données MongoDB"""
        if not self.enabled:
            return False
            
        try:
            self.clients[region] = MongoClient(host, port)
            self.dbs[region] = self.clients[region]["barge_simulation"]
            print(f"Connexion à la base de données {region} établie")
            return True
        except Exception as e:
            print(f"Erreur de connexion à {region}: {e}")
            return False
            
    def save_demand(self, demand, region="local"):
        """Sauvegarde une demande dans la base de données"""
        if not self.enabled or region not in self.dbs:
            return None
            
        collection = self.dbs[region]["demands"]
        data = {
            "demand_id": demand.demand_id,
            "origin": demand.origin,
            "destination": demand.destination,
            "volume": demand.volume,
            "status": demand.status,
            "timestamp": datetime.now()
        }
        
        try:
            result = collection.insert_one(data)
            return result.inserted_id
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la demande: {e}")
            return None
        
    def close(self):
        """Ferme toutes les connexions"""
        if not self.enabled:
            return
            
        for client in self.clients.values():
            try:
                client.close()
            except:
                pass