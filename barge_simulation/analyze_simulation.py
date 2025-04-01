#!/usr/bin/env python3
"""
Script principal pour l'analyse complète de la simulation de barges.
"""

from src.model.barge import Barge
from src.model.network import SpaceTimeNetwork
from src.model.service import Service
from src.model.routing import RoutingManager
from src.model.demand import Demand, DemandManager
from src.simulation.barge_simulator import BargeSimulator
from src.simulation.event import Event, EventType, EventFactory
from src.simulation.event_scheduler import EventScheduler
from src.visualization.movement_visualizer import MovementVisualizer
from src.analysis.performance_analyzer import PerformanceAnalyzer
from load_real_data import RealDataLoader
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def ensure_output_directory():
    """Crée le répertoire de sortie s'il n'existe pas."""
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def run_and_analyze_simulation():
    """
    Exécute la simulation avec les données réelles et génère une analyse complète des résultats.
    """
    try:
        # Créer le répertoire de sortie
        output_dir = ensure_output_directory()
        print(f"\nDossier de sortie créé: {output_dir}")
        
        # Charger les données réelles
        print("\nChargement des données réelles...")
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        data_loader = RealDataLoader(data_dir)
        data_loader.load_data()
        
        # Créer le réseau et les composants de la simulation
        print("\nCréation des composants de la simulation...")
        network = data_loader.create_network()
        services = data_loader.create_services()
        print(f"Nombre de services créés: {len(services)}")
        demands = data_loader.create_demands()
        print(f"Nombre de demandes créées: {len(demands)}")
        barges = data_loader.create_barges(services)
        print(f"Nombre de barges créées: {len(barges)}")
        
        # Initialiser le simulateur
        print("\nInitialisation du simulateur...")
        routing_manager = RoutingManager()
        simulator = BargeSimulator(network, routing_manager)
        
        # Ajouter les services et les barges
        print("\nAjout des services et des barges...")
        for service in services:
            print(f"  Ajout du service {service.service_id}")
            simulator.add_service(service)
        
        for barge in barges:
            print(f"  Ajout de la barge {barge.barge_id} à la position {barge.position}")
            simulator.add_barge(barge)
        
        # Ajouter les demandes avec le nouveau système d'événements
        print("\nAjout des demandes...")
        for demand in demands:
            print(f"  Ajout de la demande {demand.demand_id} ({demand.origin} -> {demand.destination})")
            simulator.scheduler.add_demand_arrival(
                time=demand.availability_time,
                demand_id=demand.demand_id,
                volume=demand.volume,
                origin=demand.origin,
                destination=demand.destination
            )
        
        # Ajouter un événement de fin de simulation
        simulator.scheduler.add_simulation_end(time=100)
        
        # Exécuter la simulation
        print("\nDémarrage de la simulation...")
        simulator.run(until=100)  # Durée basée sur les données réelles
        print("Simulation terminée!")
        
        # Analyser les événements traités
        print("\nAnalyse des événements traités...")
        analyze_events(simulator.processed_events, output_dir)
        
        # Créer le visualiseur de mouvements
        print("\nCréation des visualisations...")
        visualizer = MovementVisualizer(network, simulator.barges, simulator.processed_events)
        
        # Générer l'animation des mouvements
        print("Génération de l'animation des mouvements...")
        animation_file = os.path.join(output_dir, 'barge_movement.gif')
        visualizer.create_animation(output_file=animation_file)
        print(f"Animation sauvegardée: {animation_file}")
        
        # Générer le chronogramme
        print("\nGénération du chronogramme...")
        timeline_file = os.path.join(output_dir, 'barge_timeline.png')
        visualizer.create_timeline(output_file=timeline_file)
        print(f"Chronogramme sauvegardé: {timeline_file}")
        
        # Créer l'analyseur de performances
        print("\nAnalyse des performances...")
        analyzer = PerformanceAnalyzer(simulator)
        
        # Générer les graphiques de statistiques
        demand_stats_file = os.path.join(output_dir, 'demand_statistics.png')
        analyzer.plot_demand_statistics(output_file=demand_stats_file)
        print(f"Statistiques des demandes sauvegardées: {demand_stats_file}")
        
        barge_stats_file = os.path.join(output_dir, 'barge_statistics.png')
        analyzer.plot_barge_statistics(output_file=barge_stats_file)
        print(f"Statistiques des barges sauvegardées: {barge_stats_file}")
        
        # Générer le rapport de performance
        report_file = os.path.join(output_dir, 'performance_report.txt')
        analyzer.generate_performance_report(output_file=report_file)
        print(f"Rapport de performance sauvegardé: {report_file}")
        
        print("\nAnalyse complète générée dans le répertoire 'output'")
        print("Les fichiers générés sont:")
        print("- event_analysis.csv : Analyse des événements de la simulation")
        print("- event_distribution.png : Distribution des types d'événements")
        print("- event_timeline.png : Chronologie des événements")
        print("- barge_movement.gif : Animation des mouvements des barges")
        print("- barge_timeline.png : Chronogramme des mouvements")
        print("- demand_statistics.png : Statistiques des demandes")
        print("- barge_statistics.png : Statistiques des barges")
        print("- performance_report.txt : Rapport détaillé des performances")
        
    except Exception as e:
        print(f"\nERREUR: {str(e)}")
        import traceback
        print("\nDétails de l'erreur:")
        print(traceback.format_exc())

def analyze_events(events, output_dir):
    """
    Analyse les événements traités pendant la simulation.
    
    Args:
        events (list): Liste des événements traités
        output_dir (str): Répertoire de sortie
    """
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
    csv_file = os.path.join(output_dir, 'event_analysis.csv')
    df.to_csv(csv_file, index=False)
    print(f"Analyse des événements sauvegardée: {csv_file}")
    
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
    distribution_file = os.path.join(output_dir, 'event_distribution.png')
    plt.savefig(distribution_file)
    plt.close()
    print(f"Distribution des événements sauvegardée: {distribution_file}")
    
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
    timeline_file = os.path.join(output_dir, 'event_timeline.png')
    plt.savefig(timeline_file)
    plt.close()
    print(f"Chronologie des événements sauvegardée: {timeline_file}")

if __name__ == "__main__":
    run_and_analyze_simulation()
