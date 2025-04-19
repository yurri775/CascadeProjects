from tkinter import EventType
from utils.config import *
from utils.file_manager import FileManager
from datetime import datetime

class Event:
    """Types d'événements pour la simulation"""
    DEMAND_ARRIVAL = "demand_arrival"
    BARGE_DEPARTURE = "barge_departure"
    BARGE_ARRIVAL = "barge_arrival"
    LOADING_COMPLETE = "loading_complete"
    UNLOADING_COMPLETE = "unloading_complete"
    SIMULATION_END = "simulation_end"

class BargeSimulator:
    """Simulateur unifié pour les opérations de barges"""
    
    def __init__(self):
        self.current_time = 0.0
        self.events_processed = 0
        self.scheduler = self._create_scheduler()
        self.file_manager = FileManager()
        self.barges = {}
        self.demands = {}
        self.total_distance = 0.0
        self.max_time = 100.0  # Valeur par défaut
        
        self._initialize_simulation()
        
    def _create_scheduler(self):
        """Crée l'échéancier des événements"""
        # Implémentation de l'échéancier...
        pass
        
    def _initialize_simulation(self):
        """Initialise la simulation avec les données de demandes"""
        demand_data = self.file_manager.get_demand_data()
        
        for demand in demand_data:
            # Convertir et ajouter chaque demande
            availability_time = float(demand["t_avl"])
            self.add_event(
                availability_time,
                Event.DEMAND_ARRIVAL,
                {'demand': demand}
            )
    
    def add_event(self, time, event_type, data=None):
        """Ajoute un événement à l'échéancier"""
        # Implémentation de l'ajout d'événement...
        pass
    
    def _process_event(self, event):
        """Traite un événement de la simulation"""
        # Implémentation du traitement d'événement...
        pass
        
    def run(self, until=100):
        """Exécute la simulation jusqu'à un temps spécifié"""
        self.max_time = until
        
        # Ajouter l'événement de fin de simulation
        self.add_event(until, Event.SIMULATION_END)
        
        print("Démarrage de la simulation...")
        
        # Boucle principale de simulation
        while self.current_time <= self.max_time:
            # Récupérer le prochain événement
            event_bag = self.scheduler.pop_next_event_bag()
            
            # Si plus d'événements, terminer la simulation
            if event_bag is None:
                print(f"Simulation terminée à t={self.current_time}: Plus d'événements.")
                break
                
            # Mettre à jour le temps courant
            self.current_time = event_bag.time
            
            # Traiter tous les événements du sac
            for event in event_bag:
                # Vérifier si la simulation doit se terminer
                if event.event_type == Event.SIMULATION_END or self.current_time > self.max_time:
                    print(f"Simulation terminée à t={self.current_time}: Temps maximum atteint.")
                    break
                
                # Traiter l'événement
                self._process_event(event)
                self.events_processed += 1
                
        # Collecter les statistiques finales
        self._collect_statistics()
        
        print(f"Simulation terminée! Temps final: {self.current_time}")
        
    def _collect_statistics(self):
        """Collecte les statistiques de fin de simulation"""
        # Implémentation de la collecte de statistiques...
        pass
        
    def get_statistics(self):
        """Renvoie les statistiques de la simulation"""
        # Créer l'objet de statistiques
        stats = {
            'current_time': self.current_time,
            'events_processed': self.events_processed,
            'total_distance': self.total_distance,
            'barge_stats': {},
            'demand_stats': {
                'total': len(self.demands),
                'completed': sum(1 for d in self.demands.values() if d['status'] == 'completed'),
                'in_progress': sum(1 for d in self.demands.values() if d['status'] == 'in_progress'),
                'pending': sum(1 for d in self.demands.values() if d['status'] == 'pending'),
                'assigned': sum(1 for d in self.demands.values() if d['status'] == 'assigned'),
                'failed': sum(1 for d in self.demands.values() if d['status'] == 'failed'),
            }
        }
        
        # Ajouter les statistiques des barges
        for barge_id, barge in self.barges.items():
            stats['barge_stats'][barge_id] = {
                'current_position': barge.get('position', 0),
                'current_load': barge.get('load', 0),
                'status': barge.get('status', 'idle'),
                # Autres statistiques des barges...
            }
            
        return stats
        
    def save_results(self, scenario_id="1"):
        """Enregistre les résultats de la simulation dans un fichier"""
        stats = self.get_statistics()
        
        # Enregistrer le rapport de performance
        self.file_manager.write_performance_report(stats)
        
        # Enregistrer les résultats dans un fichier spécifique au scénario
        results_file = os.path.join(OUTPUT_DIR, f"{scenario_id}_results.txt")
        
        with open(results_file, 'w', encoding='utf-8') as file:
            file.write(f"=== Résultats de la simulation du scénario {scenario_id} ===\n")
            file.write(f"Date d'exécution: {datetime.now()}\n\n")
            
            # Écrire les statistiques générales
            file.write("Statistiques de la simulation:\n")
            file.write(f"Temps de simulation: {stats['current_time']:.2f}\n")
            file.write(f"Événements traités: {stats['events_processed']}\n")
            file.write(f"Distance totale parcourue: {stats['total_distance']:.2f}\n\n")
            
            # Écrire les statistiques des barges
            file.write("Statistiques des barges:\n")
            for barge_id, barge_stats in stats['barge_stats'].items():
                file.write(f"Barge {barge_id}: Position={barge_stats['current_position']}, ")
                file.write(f"Charge={barge_stats['current_load']}, Status={barge_stats['status']}\n")
            
            # Écrire les statistiques des demandes
            demand_stats = stats['demand_stats']
            file.write("\nStatistiques des demandes:\n")
            file.write(f"Total: {demand_stats['total']}\n")
            file.write(f"Complétées: {demand_stats['completed']}\n")
            file.write(f"En cours: {demand_stats['in_progress']}\n")
            file.write(f"En attente: {demand_stats['pending']}\n")
            file.write(f"Assignées: {demand_stats['assigned']}\n")
            file.write(f"Échouées: {demand_stats['failed']}\n")
    
    def _schedule_departure(self, barge, to_terminal, time):
        # Vérifier que le terminal de destination existe
        if to_terminal not in self.network.terminals:
            print(f"Erreur: Terminal {to_terminal} inconnu")
            return False
            
        # Vérifier que la connexion existe
        if to_terminal not in self.network.get_connections(barge.position):
            print(f"Erreur: Pas de connexion entre {barge.position} et {to_terminal}")
            return False
            
        self.add_event(time, EventType.BARGE_DEPARTURE, {
            'barge_id': barge.barge_id,
            'from_terminal': barge.position,
            'to_terminal': to_terminal
        })
        return True
