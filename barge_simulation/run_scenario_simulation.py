#!/usr/bin/env python3
"""
Script pour exécuter des simulations basées sur des scénarios générés.
"""

import os
import json
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
import logging
import ast

from src.model.barge import Barge
from src.model.network import Network
from src.model.service import Service
from src.model.routing import RoutingManager
from src.model.demand import Demand, DemandManager
from src.simulation.barge_simulator import BargeSimulator
from src.simulation.event import Event, EventType, EventFactory
from src.simulation.event_scheduler import EventScheduler
from src.visualization.movement_visualizer import MovementVisualizer
from src.analysis.performance_analyzer import PerformanceAnalyzer

class ScenarioSimulationRunner:
    """
    Exécuteur de simulations basées sur des scénarios.
    """
    
    def __init__(self, scenario_dir, output_dir=None):
        """
        Initialise l'exécuteur de simulations.
        
        Args:
            scenario_dir (str): Répertoire du scénario
            output_dir (str, optional): Répertoire de sortie pour les résultats
        """
        self.scenario_dir = scenario_dir
        self.scenario_name = os.path.basename(scenario_dir)
        
        # Charger la configuration
        config_file = os.path.join(scenario_dir, 'config.json')
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Définir le répertoire de sortie
        if output_dir is None:
            self.output_dir = os.path.join('output', self.scenario_name)
        else:
            self.output_dir = output_dir
        
        # Créer le répertoire de sortie s'il n'existe pas
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Configurer le logger
        self._setup_logger()
        
        self.logger.info(f"Initialisation de la simulation pour le scénario: {self.scenario_name}")
        self.logger.info(f"Répertoire de sortie: {self.output_dir}")
    
    def _setup_logger(self):
        """
        Configure le logger pour la simulation.
        """
        log_level = getattr(logging, self.config.get('logging_level', 'INFO'))
        log_file = os.path.join(self.output_dir, 'simulation.log')
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('ScenarioSimulation')
    
    def load_network(self):
        """
        Charge le réseau à partir du fichier de scénario.
        
        Returns:
            Network: Réseau chargé
        """
        network_file = os.path.join(self.scenario_dir, 'network.csv')
        self.logger.info(f"Chargement du réseau depuis: {network_file}")
        
        network = Network()
        
        # Charger les terminaux et les distances
        df = pd.read_csv(network_file)
        terminals = set(df['origin'].unique()) | set(df['destination'].unique())
        
        # Ajouter les terminaux
        for terminal in terminals:
            network.add_terminal(terminal)
        
        # Ajouter les arcs
        for _, row in df.iterrows():
            network.add_arc(
                row['origin'],
                row['destination'],
                distance=row['distance'],
                travel_time=row['travel_time']
            )
        
        self.logger.info(f"Réseau chargé avec {len(terminals)} terminaux")
        return network
    
    def load_services(self):
        """
        Charge les services à partir du fichier de scénario.
        
        Returns:
            list: Liste des services
        """
        services_file = os.path.join(self.scenario_dir, 'services.csv')
        self.logger.info(f"Chargement des services depuis: {services_file}")
        
        services = []
        df = pd.read_csv(services_file)
        
        for _, row in df.iterrows():
            # Charger les legs si disponibles
            legs = []
            if 'legs' in row and row['legs']:
                try:
                    # Format attendu: "[(origin1,destination1,duration1), (origin2,destination2,duration2), ...]"
                    legs_str = row['legs'].replace('(', '[').replace(')', ']')
                    legs_list = ast.literal_eval(legs_str)
                    for leg in legs_list:
                        if isinstance(leg, list) and len(leg) == 3:
                            legs.append(tuple(leg))
                except (SyntaxError, ValueError) as e:
                    self.logger.warning(f"Erreur lors du parsing des legs pour le service {row['service_id']}: {e}")
            
            # Charger les types de barges si disponibles
            vessel_types = {}
            if 'vessel_types' in row and row['vessel_types']:
                try:
                    # Format attendu: "{'type1': count1, 'type2': count2, ...}"
                    vessel_types = ast.literal_eval(row['vessel_types'])
                except (SyntaxError, ValueError) as e:
                    self.logger.warning(f"Erreur lors du parsing des types de barges pour le service {row['service_id']}: {e}")
            
            # Créer le service avec tous les paramètres disponibles
            service_params = {
                'service_id': row['service_id'],
                'origin': row['origin'],
                'destination': row['destination'],
                'capacity': row['capacity'] if 'capacity' in row else 0
            }
            
            # Ajouter les paramètres optionnels s'ils sont disponibles
            if legs:
                service_params['legs'] = legs
            if 'start_time' in row:
                service_params['start_time'] = row['start_time']
            if 'end_time' in row:
                service_params['end_time'] = row['end_time']
            if vessel_types:
                service_params['vessel_types'] = vessel_types
            if 'frequency' in row:
                service_params['frequency'] = row['frequency']
            if 'duration' in row:
                service_params['duration'] = row['duration']
            
            service = Service(**service_params)
            services.append(service)
        
        self.logger.info(f"Services chargés: {len(services)}")
        return services
    
    def load_demands(self):
        """
        Charge les demandes à partir du fichier de scénario.
        
        Returns:
            list: Liste des demandes
        """
        demands_file = os.path.join(self.scenario_dir, 'demands.csv')
        self.logger.info(f"Chargement des demandes depuis: {demands_file}")
        
        demands = []
        df = pd.read_csv(demands_file)
        
        for _, row in df.iterrows():
            # Préparer les paramètres de base pour la demande
            demand_params = {
                'demand_id': row['demand_id'],
                'origin': row['origin'],
                'destination': row['destination'],
                'volume': row['volume'],
                'availability_time': row['availability_time'],
                'due_date': row['due_date']
            }
            
            # Ajouter les paramètres optionnels s'ils sont disponibles
            if 'customer_type' in row:
                demand_params['customer_type'] = row['customer_type']
            if 'fare_class' in row:
                demand_params['fare_class'] = row['fare_class']
            if 'unit_fare' in row:
                demand_params['unit_fare'] = row['unit_fare']
            if 'container_type' in row:
                demand_params['container_type'] = row['container_type']
            
            demand = Demand(**demand_params)
            demands.append(demand)
        
        self.logger.info(f"Demandes chargées: {len(demands)}")
        return demands
    
    def load_barges(self, services):
        """
        Charge les barges à partir du fichier de scénario.
        
        Args:
            services (list): Liste des services
            
        Returns:
            list: Liste des barges
        """
        barges_file = os.path.join(self.scenario_dir, 'barges.csv')
        self.logger.info(f"Chargement des barges depuis: {barges_file}")
        
        barges = []
        df = pd.read_csv(barges_file)
        
        # Créer un dictionnaire des services par ID
        service_dict = {service.service_id: service for service in services}
        
        for _, row in df.iterrows():
            service_id = row['service_id'] if 'service_id' in row else None
            
            # Préparer les paramètres de base pour la barge
            barge_params = {
                'barge_id': row['barge_id'],
                'capacity': row['capacity'] if 'capacity' in row else 50,
                'position': row['initial_position'] if 'initial_position' in row else None,
                'service_id': service_id
            }
            
            barge = Barge(**barge_params)
            barges.append(barge)
            
            # Associer la barge à un service si nécessaire
            if service_id and service_id in service_dict:
                self.logger.info(f"Barge {row['barge_id']} assignée au service {service_id}")
            else:
                self.logger.warning(f"Service {service_id} non trouvé pour la barge {row['barge_id']}")
        
        self.logger.info(f"Barges chargées: {len(barges)}")
        return barges
    
    def run_simulation(self):
        """
        Exécute la simulation basée sur le scénario.
        
        Returns:
            BargeSimulator: Simulateur après exécution
        """
        self.logger.info("Démarrage de la simulation...")
        
        # Charger les composants de la simulation
        network = self.load_network()
        services = self.load_services()
        demands = self.load_demands()
        barges = self.load_barges(services)
        
        # Initialiser le simulateur
        routing_manager = RoutingManager()
        simulator = BargeSimulator(network, routing_manager)
        
        # Ajouter les services et les barges
        for service in services:
            self.logger.debug(f"Ajout du service {service.service_id}")
            simulator.add_service(service)
        
        for barge in barges:
            self.logger.debug(f"Ajout de la barge {barge.barge_id} à la position {barge.position}")
            simulator.add_barge(barge)
        
        # Ajouter les demandes avec le nouveau système d'événements
        for demand in demands:
            self.logger.debug(f"Ajout de la demande {demand.demand_id} ({demand.origin} -> {demand.destination})")
            simulator.scheduler.add_demand_arrival(
                time=demand.availability_time,
                demand_id=demand.demand_id,
                volume=demand.volume,
                origin=demand.origin,
                destination=demand.destination
            )
        
        # Ajouter un événement de fin de simulation
        simulation_duration = self.config.get('duration', 100)
        simulator.scheduler.add_simulation_end(time=simulation_duration)
        
        # Exécuter la simulation
        self.logger.info(f"Exécution de la simulation pour une durée de {simulation_duration}...")
        simulator.run(until=simulation_duration)
        self.logger.info("Simulation terminée!")
        
        return simulator
    
    def analyze_results(self, simulator):
        """
        Analyse les résultats de la simulation.
        
        Args:
            simulator (BargeSimulator): Simulateur après exécution
        """
        self.logger.info("Analyse des résultats de la simulation...")
        
        # Analyser les événements
        self._analyze_events(simulator.processed_events)
        
        # Créer les visualisations
        self._create_visualizations(simulator)
        
        # Générer le rapport de performance
        self._generate_performance_report(simulator)
        
        self.logger.info("Analyse des résultats terminée!")
    
    def _analyze_events(self, events):
        """
        Analyse les événements traités pendant la simulation.
        
        Args:
            events (list): Liste des événements traités
        """
        self.logger.info("Analyse des événements...")
        
        # Créer un DataFrame pour l'analyse des événements
        event_data = []
        for event in events:
            event_info = {
                'id': event.id,
                'time': event.time,
                'type': event.event_type.name if hasattr(event.event_type, 'name') else str(event.event_type),
                'resource_type': event.get_resource_type() if hasattr(event, 'get_resource_type') else 'unknown',
                'resource_id': event.get_resource() if hasattr(event, 'get_resource') else 'unknown',
                'quantity': event.get_quantity() if hasattr(event, 'get_quantity') else 0,
                'origin': event.get_location() if hasattr(event, 'get_location') else 'unknown',
                'destination': event.get_destination() if hasattr(event, 'get_destination') else 'unknown',
            }
            event_data.append(event_info)
        
        # Créer le DataFrame
        df = pd.DataFrame(event_data)
        
        # Sauvegarder les données
        csv_file = os.path.join(self.output_dir, 'event_analysis.csv')
        df.to_csv(csv_file, index=False)
        self.logger.info(f"Analyse des événements sauvegardée: {csv_file}")
        
        # Créer un graphique de distribution des types d'événements
        plt.figure(figsize=(12, 6))
        event_counts = df['type'].value_counts()
        event_counts.plot(kind='bar', color='skyblue')
        plt.title('Distribution des types d\'événements')
        plt.xlabel('Type d\'événement')
        plt.ylabel('Nombre d\'occurrences')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Sauvegarder le graphique
        distribution_file = os.path.join(self.output_dir, 'event_distribution.png')
        plt.savefig(distribution_file)
        plt.close()
        self.logger.info(f"Distribution des événements sauvegardée: {distribution_file}")
        
        # Créer un graphique de chronologie des événements
        plt.figure(figsize=(14, 8))
        
        # Créer un dictionnaire pour mapper les types d'événements à des couleurs
        event_types = df['type'].unique()
        colors = plt.cm.tab20(range(len(event_types)))
        color_map = dict(zip(event_types, colors))
        
        # Tracer les événements sur la chronologie
        for i, row in df.iterrows():
            plt.scatter(row['time'], i, color=color_map[row['type']], s=50, alpha=0.7)
            plt.text(row['time'] + 0.1, i, f"{row['type']} ({row['resource_id']})", fontsize=8)
        
        # Ajouter une légende
        for event_type, color in color_map.items():
            plt.scatter([], [], color=color, label=event_type)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.title('Chronologie des événements de la simulation')
        plt.xlabel('Temps de simulation')
        plt.ylabel('Événements')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Sauvegarder le graphique
        timeline_file = os.path.join(self.output_dir, 'event_timeline.png')
        plt.savefig(timeline_file)
        plt.close()
        self.logger.info(f"Chronologie des événements sauvegardée: {timeline_file}")
    
    def _create_visualizations(self, simulator):
        """
        Crée les visualisations de la simulation.
        
        Args:
            simulator (BargeSimulator): Simulateur après exécution
        """
        self.logger.info("Création des visualisations...")
        
        # Vérifier si les visualisations sont activées
        if not self.config.get('visualization', True):
            self.logger.info("Visualisations désactivées dans la configuration")
            return
        
        # Créer le visualiseur de mouvements
        visualizer = MovementVisualizer(
            simulator.network,
            simulator.barges,
            simulator.processed_events
        )
        
        # Générer l'animation des mouvements
        animation_file = os.path.join(self.output_dir, 'barge_movement.gif')
        visualizer.create_animation(output_file=animation_file)
        self.logger.info(f"Animation sauvegardée: {animation_file}")
        
        # Générer le chronogramme
        timeline_file = os.path.join(self.output_dir, 'barge_timeline.png')
        visualizer.create_timeline(output_file=timeline_file)
        self.logger.info(f"Chronogramme sauvegardé: {timeline_file}")
    
    def _generate_performance_report(self, simulator):
        """
        Génère le rapport de performance de la simulation.
        
        Args:
            simulator (BargeSimulator): Simulateur après exécution
        """
        self.logger.info("Génération du rapport de performance...")
        
        # Vérifier si l'analyse est activée
        if not self.config.get('analysis', True):
            self.logger.info("Analyse désactivée dans la configuration")
            return
        
        # Créer l'analyseur de performances
        analyzer = PerformanceAnalyzer(simulator)
        
        # Générer les graphiques de statistiques
        demand_stats_file = os.path.join(self.output_dir, 'demand_statistics.png')
        analyzer.plot_demand_statistics(output_file=demand_stats_file)
        self.logger.info(f"Statistiques des demandes sauvegardées: {demand_stats_file}")
        
        barge_stats_file = os.path.join(self.output_dir, 'barge_statistics.png')
        analyzer.plot_barge_statistics(output_file=barge_stats_file)
        self.logger.info(f"Statistiques des barges sauvegardées: {barge_stats_file}")
        
        # Générer le rapport de performance
        report_file = os.path.join(self.output_dir, 'performance_report.txt')
        analyzer.generate_performance_report(output_file=report_file)
        self.logger.info(f"Rapport de performance sauvegardé: {report_file}")

def main():
    """
    Fonction principale.
    """
    # Analyser les arguments de la ligne de commande
    parser = argparse.ArgumentParser(description='Exécute une simulation basée sur un scénario.')
    parser.add_argument('scenario', help='Nom du scénario ou chemin vers le répertoire du scénario')
    parser.add_argument('--output', help='Répertoire de sortie pour les résultats')
    args = parser.parse_args()
    
    # Déterminer le répertoire du scénario
    if os.path.isdir(args.scenario):
        scenario_dir = args.scenario
    else:
        scenario_dir = os.path.join('scenarios', args.scenario)
    
    # Vérifier que le répertoire du scénario existe
    if not os.path.exists(scenario_dir):
        print(f"Erreur: Le répertoire du scénario '{scenario_dir}' n'existe pas.")
        return
    
    # Créer et exécuter la simulation
    runner = ScenarioSimulationRunner(scenario_dir, args.output)
    simulator = runner.run_simulation()
    runner.analyze_results(simulator)
    
    print("\nSimulation terminée avec succès!")
    print(f"Les résultats sont disponibles dans le répertoire: {runner.output_dir}")

if __name__ == "__main__":
    main()
