from utils.config import *

class FileManager:
    """Gestionnaire de fichiers pour éviter les accès répétés"""
    
    _instance = None
    _cached_data = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FileManager, cls).__new__(cls)
        return cls._instance
    
    def get_demand_data(self):
        """Charge les données de demande avec mise en cache"""
        if 'demand_data' not in self._cached_data:
            self._cached_data['demand_data'] = self._load_demand_file()
        return self._cached_data['demand_data']
    
    def _load_demand_file(self):
        """Charge le fichier de demandes"""
        demand_data = []
        with open(DEMAND_FILE, 'r', encoding='utf-8') as file:
            # Ignorer l'en-tête
            header = file.readline().strip().split('\t')
            
            # Lire toutes les demandes
            for line in file:
                if line.strip():  # Ignorer les lignes vides
                    values = line.strip().split('\t')
                    demand = dict(zip(header, values))
                    demand_data.append(demand)
                    
        return demand_data
    
    def write_performance_report(self, stats):
        """Écrit le rapport de performance"""
        with open(PERFORMANCE_REPORT, 'w', encoding='utf-8') as file:
            file.write("=== Rapport de performance de la simulation ===\n\n")
            
            # Statistiques globales
            file.write("== Statistiques globales ==\n")
            file.write(f"Temps total de simulation: {stats['current_time']:.2f}\n")
            file.write(f"Nombre total d'événements: {stats['events_processed']}\n\n")
            
            # Statistiques des demandes
            demand_stats = stats['demand_stats']
            file.write("== Statistiques des demandes ==\n")
            file.write(f"Total des demandes: {demand_stats['total']}\n")
            file.write(f"Demandes complétées: {demand_stats['completed']}\n")
            file.write(f"Demandes échouées: {demand_stats['failed']}\n")
            file.write(f"Demandes en attente: {demand_stats['pending']}\n")
            file.write(f"Demandes en cours: {demand_stats['in_progress']}\n")
            
            # Plus de statistiques sur les demandes
            completion_time = demand_stats.get('avg_completion_time', 0)
            waiting_time = demand_stats.get('avg_waiting_time', 0)
            ontime_rate = demand_stats.get('ontime_delivery_rate', 0) * 100
            
            file.write(f"Temps moyen de completion: {completion_time:.2f}\n")
            file.write(f"Temps moyen d'attente: {waiting_time:.2f}\n")
            file.write(f"Taux de livraison à temps: {ontime_rate:.1f}%\n\n")
            
            # Statistiques des barges
            file.write("== Statistiques des barges ==\n\n")
            for barge_id, barge_stats in stats['barge_stats'].items():
                file.write(f"Barge {barge_id}:\n")
                file.write(f"  Nombre de trajets: {barge_stats.get('trips', 0)}\n")
                file.write(f"  Temps total de trajet: {barge_stats.get('total_travel_time', 0):.2f}\n")
                file.write(f"  Taux d'utilisation: {barge_stats.get('utilization_rate', 0) * 100:.1f}%\n")
                file.write(f"  Charge moyenne: {barge_stats.get('avg_load', 0) * 100:.1f}%\n\n")
