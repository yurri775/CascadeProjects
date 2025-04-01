#!/usr/bin/env python3
"""
Script pour générer des scénarios de simulation à partir de fichiers d'entrée standardisés.
"""

import os
import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class ScenarioGenerator:
    """
    Générateur de scénarios pour la simulation de barges.
    """
    
    def __init__(self, output_dir="scenarios"):
        """
        Initialise le générateur de scénarios.
        
        Args:
            output_dir (str): Répertoire de sortie pour les scénarios générés
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_scenario(self, scenario_name, config):
        """
        Génère un scénario complet à partir d'une configuration.
        
        Args:
            scenario_name (str): Nom du scénario
            config (dict): Configuration du scénario
        
        Returns:
            str: Chemin vers le répertoire du scénario
        """
        # Créer le répertoire du scénario
        scenario_dir = os.path.join(self.output_dir, scenario_name)
        if not os.path.exists(scenario_dir):
            os.makedirs(scenario_dir)
        
        # Générer les fichiers du scénario
        self._generate_network_file(scenario_dir, config.get('network', {}))
        self._generate_services_file(scenario_dir, config.get('services', {}))
        self._generate_demands_file(scenario_dir, config.get('demands', {}))
        self._generate_barges_file(scenario_dir, config.get('barges', {}))
        self._generate_config_file(scenario_dir, config.get('simulation', {}))
        
        print(f"Scénario '{scenario_name}' généré dans le répertoire: {scenario_dir}")
        return scenario_dir
    
    def _generate_network_file(self, scenario_dir, network_config):
        """
        Génère le fichier de réseau.
        
        Args:
            scenario_dir (str): Répertoire du scénario
            network_config (dict): Configuration du réseau
        """
        # Extraire les paramètres du réseau
        terminals = network_config.get('terminals', [])
        distances = network_config.get('distances', {})
        
        # Créer le fichier de réseau
        network_file = os.path.join(scenario_dir, 'network.csv')
        with open(network_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['origin', 'destination', 'distance', 'travel_time'])
            
            # Ajouter les distances entre les terminaux
            for origin in terminals:
                for destination in terminals:
                    if origin != destination:
                        distance = distances.get(f"{origin}-{destination}", 
                                               random.uniform(10, 100))
                        travel_time = distance / network_config.get('speed', 10)
                        writer.writerow([origin, destination, distance, travel_time])
    
    def _generate_services_file(self, scenario_dir, services_config):
        """
        Génère le fichier de services.
        
        Args:
            scenario_dir (str): Répertoire du scénario
            services_config (dict): Configuration des services
        """
        # Extraire les paramètres des services
        num_services = services_config.get('num_services', 5)
        terminals = services_config.get('terminals', [])
        
        # Créer le fichier de services
        services_file = os.path.join(scenario_dir, 'services.csv')
        with open(services_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['service_id', 'origin', 'destination', 'capacity', 'frequency', 'duration'])
            
            # Générer les services
            for i in range(1, num_services + 1):
                service_id = f"S{i}"
                origin = random.choice(terminals)
                destination = random.choice([t for t in terminals if t != origin])
                capacity = random.randint(50, 200)
                frequency = random.randint(1, 7)
                duration = random.randint(1, 5)
                
                writer.writerow([service_id, origin, destination, capacity, frequency, duration])
    
    def _generate_demands_file(self, scenario_dir, demands_config):
        """
        Génère le fichier de demandes.
        
        Args:
            scenario_dir (str): Répertoire du scénario
            demands_config (dict): Configuration des demandes
        """
        # Extraire les paramètres des demandes
        num_demands = demands_config.get('num_demands', 20)
        terminals = demands_config.get('terminals', [])
        simulation_duration = demands_config.get('simulation_duration', 100)
        
        # Créer le fichier de demandes
        demands_file = os.path.join(scenario_dir, 'demands.csv')
        with open(demands_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['demand_id', 'origin', 'destination', 'volume', 'availability_time', 
                           'due_date', 'priority', 'urgency'])
            
            # Générer les demandes
            for i in range(1, num_demands + 1):
                demand_id = f"D{i}"
                origin = random.choice(terminals)
                destination = random.choice([t for t in terminals if t != origin])
                volume = random.randint(10, 100)
                availability_time = random.uniform(0, simulation_duration * 0.7)
                due_date = availability_time + random.uniform(10, simulation_duration * 0.3)
                priority = random.randint(1, 5)
                urgency = random.choice(['low', 'medium', 'high'])
                
                writer.writerow([demand_id, origin, destination, volume, 
                               availability_time, due_date, priority, urgency])
    
    def _generate_barges_file(self, scenario_dir, barges_config):
        """
        Génère le fichier de barges.
        
        Args:
            scenario_dir (str): Répertoire du scénario
            barges_config (dict): Configuration des barges
        """
        # Extraire les paramètres des barges
        num_barges = barges_config.get('num_barges', 10)
        terminals = barges_config.get('terminals', [])
        
        # Créer le fichier de barges
        barges_file = os.path.join(scenario_dir, 'barges.csv')
        with open(barges_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['barge_id', 'capacity', 'initial_position', 'speed', 'service_id'])
            
            # Générer les barges
            for i in range(1, num_barges + 1):
                barge_id = f"B{i}"
                capacity = random.randint(50, 200)
                initial_position = random.choice(terminals)
                speed = random.uniform(8, 15)
                service_id = f"S{random.randint(1, barges_config.get('num_services', 5))}"
                
                writer.writerow([barge_id, capacity, initial_position, speed, service_id])
    
    def _generate_config_file(self, scenario_dir, simulation_config):
        """
        Génère le fichier de configuration de la simulation.
        
        Args:
            scenario_dir (str): Répertoire du scénario
            simulation_config (dict): Configuration de la simulation
        """
        # Extraire les paramètres de la simulation
        config = {
            'simulation_name': simulation_config.get('name', 'Default Simulation'),
            'duration': simulation_config.get('duration', 100),
            'random_seed': simulation_config.get('random_seed', 42),
            'logging_level': simulation_config.get('logging_level', 'INFO'),
            'output_directory': 'output',
            'visualization': simulation_config.get('visualization', True),
            'analysis': simulation_config.get('analysis', True),
            'parameters': {
                'loading_time_per_unit': simulation_config.get('loading_time_per_unit', 0.1),
                'unloading_time_per_unit': simulation_config.get('unloading_time_per_unit', 0.1),
                'terminal_capacity': simulation_config.get('terminal_capacity', 500),
                'barge_speed_factor': simulation_config.get('barge_speed_factor', 1.0),
                'demand_priority_weight': simulation_config.get('demand_priority_weight', 1.0),
                'urgency_factor': simulation_config.get('urgency_factor', 1.5)
            }
        }
        
        # Créer le fichier de configuration
        config_file = os.path.join(scenario_dir, 'config.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)

def generate_default_scenarios():
    """
    Génère un ensemble de scénarios par défaut.
    """
    generator = ScenarioGenerator()
    
    # Définir les terminaux communs
    terminals = ['A', 'B', 'C', 'D', 'E', 'F']
    
    # Scénario 1: Petit réseau, faible demande
    config_small = {
        'network': {
            'terminals': terminals[:3],
            'speed': 10
        },
        'services': {
            'num_services': 3,
            'terminals': terminals[:3]
        },
        'demands': {
            'num_demands': 10,
            'terminals': terminals[:3],
            'simulation_duration': 100
        },
        'barges': {
            'num_barges': 5,
            'terminals': terminals[:3],
            'num_services': 3
        },
        'simulation': {
            'name': 'Small Network Simulation',
            'duration': 100,
            'random_seed': 42,
            'visualization': True
        }
    }
    generator.generate_scenario('small_network', config_small)
    
    # Scénario 2: Réseau moyen, demande moyenne
    config_medium = {
        'network': {
            'terminals': terminals[:5],
            'speed': 12
        },
        'services': {
            'num_services': 7,
            'terminals': terminals[:5]
        },
        'demands': {
            'num_demands': 30,
            'terminals': terminals[:5],
            'simulation_duration': 150
        },
        'barges': {
            'num_barges': 12,
            'terminals': terminals[:5],
            'num_services': 7
        },
        'simulation': {
            'name': 'Medium Network Simulation',
            'duration': 150,
            'random_seed': 123,
            'visualization': True
        }
    }
    generator.generate_scenario('medium_network', config_medium)
    
    # Scénario 3: Grand réseau, forte demande
    config_large = {
        'network': {
            'terminals': terminals,
            'speed': 15
        },
        'services': {
            'num_services': 12,
            'terminals': terminals
        },
        'demands': {
            'num_demands': 50,
            'terminals': terminals,
            'simulation_duration': 200
        },
        'barges': {
            'num_barges': 20,
            'terminals': terminals,
            'num_services': 12
        },
        'simulation': {
            'name': 'Large Network Simulation',
            'duration': 200,
            'random_seed': 456,
            'visualization': True
        }
    }
    generator.generate_scenario('large_network', config_large)
    
    # Scénario 4: Réseau congestionné
    config_congested = {
        'network': {
            'terminals': terminals[:4],
            'speed': 8
        },
        'services': {
            'num_services': 5,
            'terminals': terminals[:4]
        },
        'demands': {
            'num_demands': 40,
            'terminals': terminals[:4],
            'simulation_duration': 120
        },
        'barges': {
            'num_barges': 8,
            'terminals': terminals[:4],
            'num_services': 5
        },
        'simulation': {
            'name': 'Congested Network Simulation',
            'duration': 120,
            'random_seed': 789,
            'visualization': True,
            'terminal_capacity': 300,
            'loading_time_per_unit': 0.2,
            'unloading_time_per_unit': 0.2
        }
    }
    generator.generate_scenario('congested_network', config_congested)
    
    print("\nScénarios générés avec succès!")
    print("Vous pouvez maintenant exécuter la simulation avec ces scénarios.")

if __name__ == "__main__":
    generate_default_scenarios()
