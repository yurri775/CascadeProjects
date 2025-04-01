"""
Module d'analyse des performances de la simulation de barges.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict

class PerformanceAnalyzer:
    """Analyseur de performances pour la simulation de barges."""
    
    def __init__(self, simulator):
        """
        Initialise l'analyseur avec les données de simulation.
        
        Args:
            simulator: Instance du simulateur après exécution
        """
        self.simulator = simulator
        self.events = simulator.processed_events
        self.barges = simulator.barges
        self.demands = simulator.demand_manager.demands
        self.network = simulator.network
        
    def analyze_demand_performance(self):
        """
        Analyse la performance du traitement des demandes.
        
        Returns:
            dict: Statistiques sur les demandes
        """
        stats = {
            'total_demands': len(self.demands),
            'completed_demands': 0,
            'failed_demands': 0,
            'pending_demands': 0,
            'in_progress_demands': 0,
            'avg_completion_time': 0,
            'avg_waiting_time': 0,
            'on_time_delivery_rate': 0
        }
        
        completion_times = []
        waiting_times = []
        on_time_deliveries = 0
        
        for demand in self.demands.values():
            if demand.status == 'completed':
                stats['completed_demands'] += 1
                if demand.completion_time and demand.arrival_time:
                    completion_time = demand.completion_time - demand.arrival_time
                    completion_times.append(completion_time)
                if demand.start_time and demand.arrival_time:
                    waiting_time = demand.start_time - demand.arrival_time
                    waiting_times.append(waiting_time)
                if demand.deadline and demand.completion_time <= demand.deadline:
                    on_time_deliveries += 1
            elif demand.status == 'failed':
                stats['failed_demands'] += 1
            elif demand.status == 'pending':
                stats['pending_demands'] += 1
            elif demand.status == 'in_progress':
                stats['in_progress_demands'] += 1
        
        # Calculer les moyennes
        if completion_times:
            stats['avg_completion_time'] = sum(completion_times) / len(completion_times)
        if waiting_times:
            stats['avg_waiting_time'] = sum(waiting_times) / len(waiting_times)
        if stats['completed_demands'] > 0:
            stats['on_time_delivery_rate'] = on_time_deliveries / stats['completed_demands']
            
        return stats
    
    def analyze_barge_utilization(self):
        """
        Analyse l'utilisation des barges.
        
        Returns:
            dict: Statistiques sur l'utilisation des barges
        """
        stats = defaultdict(lambda: {
            'total_distance': 0,
            'total_load_time': 0,
            'total_unload_time': 0,
            'total_travel_time': 0,
            'avg_load': 0,
            'utilization_rate': 0,
            'number_of_trips': 0
        })
        
        # Analyser les événements pour chaque barge
        for event in self.events:
            if event.event_type in ['barge_departure', 'barge_arrival']:
                barge_id = event.data.get('barge_id')
                if barge_id:
                    if event.event_type == 'barge_departure':
                        stats[barge_id]['number_of_trips'] += 1
                    
                    # Calculer le temps de trajet
                    if event.event_type == 'barge_arrival':
                        # Trouver l'événement de départ correspondant
                        departure_event = self._find_previous_departure(event)
                        if departure_event:
                            travel_time = event.time - departure_event.time
                            stats[barge_id]['total_travel_time'] += travel_time
        
        # Calculer les statistiques finales pour chaque barge
        for barge_id, barge in self.barges.items():
            stats[barge_id]['avg_load'] = barge.current_load / barge.capacity
            total_time = self.simulator.current_time
            if total_time > 0:
                stats[barge_id]['utilization_rate'] = (
                    stats[barge_id]['total_travel_time'] / total_time
                )
        
        return dict(stats)
    
    def _find_previous_departure(self, arrival_event):
        """
        Trouve l'événement de départ correspondant à une arrivée.
        
        Args:
            arrival_event: Événement d'arrivée
            
        Returns:
            Event: Événement de départ correspondant ou None
        """
        barge_id = arrival_event.data.get('barge_id')
        for event in reversed(self.events):
            if (event.time < arrival_event.time and 
                event.event_type == 'barge_departure' and
                event.data.get('barge_id') == barge_id):
                return event
        return None
    
    def plot_demand_statistics(self, output_file='demand_statistics.png'):
        """
        Génère un graphique des statistiques de demandes.
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        stats = self.analyze_demand_performance()
        
        # Créer la figure avec plusieurs sous-graphiques
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Graphique en secteurs du statut des demandes
        status_data = {
            'Complétées': stats['completed_demands'],
            'Échouées': stats['failed_demands'],
            'En attente': stats['pending_demands'],
            'En cours': stats['in_progress_demands']
        }
        ax1.pie(status_data.values(), labels=status_data.keys(), autopct='%1.1f%%')
        ax1.set_title('Statut des demandes')
        
        # 2. Graphique à barres des temps moyens
        times = {
            'Temps de completion': stats['avg_completion_time'],
            'Temps d\'attente': stats['avg_waiting_time']
        }
        ax2.bar(times.keys(), times.values())
        ax2.set_title('Temps moyens')
        ax2.set_ylabel('Temps')
        
        # 3. Taux de livraison à temps
        ax3.bar(['À temps', 'En retard'], 
                [stats['on_time_delivery_rate'], 1 - stats['on_time_delivery_rate']])
        ax3.set_title('Taux de livraison à temps')
        ax3.set_ylabel('Proportion')
        
        # 4. Progression des demandes dans le temps
        demand_progression = self._calculate_demand_progression()
        times = sorted(demand_progression.keys())
        completed = [demand_progression[t]['completed'] for t in times]
        in_progress = [demand_progression[t]['in_progress'] for t in times]
        pending = [demand_progression[t]['pending'] for t in times]
        
        ax4.stackplot(times, [completed, in_progress, pending],
                     labels=['Complétées', 'En cours', 'En attente'])
        ax4.set_title('Progression des demandes')
        ax4.set_xlabel('Temps')
        ax4.set_ylabel('Nombre de demandes')
        ax4.legend()
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Enregistrer le graphique
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Statistiques des demandes enregistrées dans {output_file}")
    
    def plot_barge_statistics(self, output_file='barge_statistics.png'):
        """
        Génère un graphique des statistiques des barges.
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        stats = self.analyze_barge_utilization()
        
        # Créer la figure avec plusieurs sous-graphiques
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Taux d'utilisation des barges
        barge_ids = list(stats.keys())
        utilization_rates = [stats[bid]['utilization_rate'] for bid in barge_ids]
        ax1.bar(barge_ids, utilization_rates)
        ax1.set_title('Taux d\'utilisation des barges')
        ax1.set_ylabel('Taux d\'utilisation')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 2. Nombre de trajets par barge
        trips = [stats[bid]['number_of_trips'] for bid in barge_ids]
        ax2.bar(barge_ids, trips)
        ax2.set_title('Nombre de trajets par barge')
        ax2.set_ylabel('Nombre de trajets')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # 3. Temps de trajet total par barge
        travel_times = [stats[bid]['total_travel_time'] for bid in barge_ids]
        ax3.bar(barge_ids, travel_times)
        ax3.set_title('Temps de trajet total par barge')
        ax3.set_ylabel('Temps')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        # 4. Charge moyenne par barge
        loads = [stats[bid]['avg_load'] for bid in barge_ids]
        ax4.bar(barge_ids, loads)
        ax4.set_title('Charge moyenne par barge')
        ax4.set_ylabel('Charge moyenne')
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Enregistrer le graphique
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Statistiques des barges enregistrées dans {output_file}")
    
    def _calculate_demand_progression(self):
        """
        Calcule la progression des demandes au fil du temps.
        
        Returns:
            dict: Nombre de demandes par statut à chaque instant
        """
        progression = defaultdict(lambda: {'completed': 0, 'in_progress': 0, 'pending': 0})
        
        # Parcourir les événements dans l'ordre chronologique
        for event in sorted(self.events, key=lambda e: e.time):
            if event.event_type in ['demand_arrival', 'loading_complete', 'unloading_complete']:
                time = event.time
                
                # Copier l'état précédent
                if time > 0:
                    prev_time = max(t for t in progression.keys() if t < time)
                    progression[time] = progression[prev_time].copy()
                
                # Mettre à jour selon le type d'événement
                if event.event_type == 'demand_arrival':
                    progression[time]['pending'] += 1
                elif event.event_type == 'loading_complete':
                    progression[time]['pending'] -= 1
                    progression[time]['in_progress'] += 1
                elif event.event_type == 'unloading_complete':
                    progression[time]['in_progress'] -= 1
                    progression[time]['completed'] += 1
        
        return dict(progression)
    
    
        def _process_pending_demands(self):
            """Traite les demandes en attente."""
            pending_demands = self.demand_manager.get_pending_demands(self.current_time)
            
            # Trier par priorité (date limite la plus proche)
            pending_demands.sort(key=lambda d: d.due_date)
            
            for demand in pending_demands:
                if self._assign_demand_to_barge(demand):
                    print(f"Demande {demand.demand_id} assignée à la barge {demand.assigned_barge}")
                else:
                    print(f"Impossible d'assigner la demande {demand.demand_id}")
    
    def run(self, until=100):
        """Exécute la simulation avec gestion périodique des demandes."""
        print("\nDémarrage de la simulation...")
        
        while self.current_time < until and self.event_queue:
            event = self.event_queue.pop_next()
            self._process_event(event)
            
            # Vérifier les demandes en attente périodiquement
            if self.current_time % 5 == 0:  # Toutes les 5 unités de temps
                self._process_pending_demands()
    
    def generate_performance_report(self, output_file='performance_report.txt'):
        """
        Génère un rapport détaillé des performances.
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        demand_stats = self.analyze_demand_performance()
        barge_stats = self.analyze_barge_utilization()
        
        with open(output_file, 'w') as f:
            f.write("=== Rapport de performance de la simulation ===\n\n")
            
            # Statistiques globales
            f.write("== Statistiques globales ==\n")
            f.write(f"Temps total de simulation: {self.simulator.current_time:.2f}\n")
            f.write(f"Nombre total d'événements: {len(self.events)}\n\n")
            
            # Statistiques des demandes
            f.write("== Statistiques des demandes ==\n")
            f.write(f"Total des demandes: {demand_stats['total_demands']}\n")
            f.write(f"Demandes complétées: {demand_stats['completed_demands']}\n")
            f.write(f"Demandes échouées: {demand_stats['failed_demands']}\n")
            f.write(f"Demandes en attente: {demand_stats['pending_demands']}\n")
            f.write(f"Demandes en cours: {demand_stats['in_progress_demands']}\n")
            f.write(f"Temps moyen de completion: {demand_stats['avg_completion_time']:.2f}\n")
            f.write(f"Temps moyen d'attente: {demand_stats['avg_waiting_time']:.2f}\n")
            f.write(f"Taux de livraison à temps: {demand_stats['on_time_delivery_rate']*100:.1f}%\n\n")
            
            # Statistiques des barges
            f.write("== Statistiques des barges ==\n")
            for barge_id, stats in barge_stats.items():
                f.write(f"\nBarge {barge_id}:\n")
                f.write(f"  Nombre de trajets: {stats['number_of_trips']}\n")
                f.write(f"  Temps total de trajet: {stats['total_travel_time']:.2f}\n")
                f.write(f"  Taux d'utilisation: {stats['utilization_rate']*100:.1f}%\n")
                f.write(f"  Charge moyenne: {stats['avg_load']*100:.1f}%\n")
            
        print(f"Rapport de performance enregistré dans {output_file}")
