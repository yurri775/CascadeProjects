"""
Simulateur à événements discrets pour le système de transport par barges.
"""
import simpy
import random
import logging
from src.simulation.event import Event, EventType
from src.simulation.event_scheduler import EventScheduler
from src.model.demand import Demand
from src.model.demand import DemandManager
from src.model.demand_manager import DemandManager  # Ajoutez cette ligne en haut du fichier

class BargeSimulator:
    """
    Simulateur pour le système de transport par barges utilisant la simulation à événements discrets.
    """
    def __init__(self, network=None, routing_manager=None, **kwargs):
        from src.simulation.event_scheduler import EventScheduler
        
        self.network = network
        self.routing_manager = routing_manager
        self.scheduler = EventScheduler()
        self.current_time = 0
        self.events = []
        self.processed_events = []  # C'est probablement cet attribut qui est recherché
        self.events_processed = 0   # Ajoutez cette ligne
        self.barges = {}
        self.services = {}
        self.demands = {}
        
        # Ajoutez cette ligne pour créer le gestionnaire de demandes
        self.demand_manager = DemandManager()
        
        self.stats = {
            "total_distance": 0,
            "total_teus_transported": 0,
            "service_utilization": {},
            "terminal_utilization": {}
        }
        
        # Propriété pour compatibilité
        self.total_distance = 0
        
        # Gestion optionnelle de la base de données
        try:
            from src.utils.db_manager import DBManager
            self.db_manager = DBManager()
        except ImportError:
            self.db_manager = None

        # Alias pour compatibilité
        self.statistics = self.stats

    # Ajoutez cette méthode pour compatibilité
    def get_stat(self, stat_name, default=0):
        """Récupère une statistique de manière sécurisée"""
        if hasattr(self, 'stats') and stat_name in self.stats:
            return self.stats[stat_name]
        elif hasattr(self, stat_name):
            return getattr(self, stat_name)
        else:
            return default
    
    # Assurez-vous que cette méthode est mise à jour à chaque changement
    def _update_distance(self, distance):
        """Met à jour la distance totale"""
        self.stats["total_distance"] += distance
        self.total_distance += distance  # Pour compatibilité

    def add_barge(self, barge):
        """
        Ajoute une barge à la simulation.
        
        Args:
            barge (Barge): La barge à ajouter
        """
        self.barges[barge.barge_id] = barge
        
        # Si la barge a un service, planifier le départ initial
        if barge.service_id and barge.service_id in self.services:
            service = self.services[barge.service_id]
            if barge.position in service.route:
                # Trouver le prochain nœud dans la route du service
                current_idx = service.route.index(barge.position)
                if current_idx < len(service.route) - 1:
                    next_node = service.route[current_idx + 1]
                    # Planifier le départ
                    self.add_event(0, EventType.BARGE_DEPARTURE, {
                        'barge_id': barge.barge_id,
                        'from_terminal': barge.position,
                        'to_terminal': next_node
                    })
    
    def add_service(self, service):
        """
        Ajoute un service à la simulation.
        
        Args:
            service (Service): Le service à ajouter
        """
        self.services[service.service_id] = service
        
    def add_demand(self, demand):
        """
        Ajoute une demande à la simulation.
        
        Args:
            demand (Demand): La demande à ajouter
        """
        self.demand_manager.add_demand(demand)
        
        # Planifier l'arrivée de la demande
        self.add_event(demand.availability_time, EventType.DEMAND_ARRIVAL, {
            'demand': demand
        })
        
    def add_event(self, time, event_type, data=None):
        """
        Ajoute un événement à l'échéancier.
        
        Args:
            time (float): Instant auquel l'événement se produit
            event_type (str): Type d'événement
            data (dict, optional): Données supplémentaires pour l'événement
            
        Returns:
            Event: L'événement créé
        """
        return self.scheduler.add_event(time, event_type, data)
        
    def run(self, until=100):
        """Exécute la simulation jusqu'au temps spécifié."""
        print("Démarrage de la simulation...")
        
        while self.current_time < until:
            event_bag = self.scheduler.pop_next_event_bag()
            if not event_bag:
                print(f"Simulation terminée à t={self.current_time}: Plus d'événements.")
                break
                
            for event in event_bag:
                self._process_event(event)
                self.processed_events.append(event)
                self.events_processed += 1  # Incrémentez le compteur ici
                
            # Mise à jour du temps courant
            if event_bag:
                self.current_time = event_bag[-1].time
        
        print("\nSimulation terminée!")
        return self.events_processed  # Retournez ce compteur

    def _process_event(self, event):
        """
        Traite un événement en fonction de son type.
        
        Args:
            event (Event): L'événement à traiter
        """
        print(f"Traitement de l'événement: {event}")
        self.processed_events.append(event)
        
        # Traiter l'événement en fonction de son type
        if event.event_type == EventType.BARGE_DEPARTURE:
            self._handle_barge_departure(event)
        elif event.event_type == EventType.BARGE_ARRIVAL:
            self._handle_barge_arrival(event)
        elif event.event_type == EventType.DEMAND_ARRIVAL:
            self._handle_demand_arrival(event)
        elif event.event_type == EventType.BARGE_LOADING_COMPLETE:
            self._handle_loading_complete(event)
        elif event.event_type == EventType.BARGE_UNLOADING_COMPLETE:
            self._handle_unloading_complete(event)
            
    def _handle_barge_departure(self, event):
        """
        Gère un événement de départ de barge.
        
        Args:
            event (Event): L'événement à traiter
        """
        barge_id = event.data['barge_id']
        from_terminal = event.data['from_terminal']
        to_terminal = event.data['to_terminal']
        
        # Récupérer la barge
        barge = self.barges.get(barge_id)
        if not barge:
            print(f"Erreur: Barge {barge_id} non trouvée")
            return
            
        # Mettre à jour la position de la barge
        barge.status = "en_transit"
        
        # Calculer le temps de trajet
        travel_time = self.network.get_travel_time(from_terminal, to_terminal)
        if travel_time is None:
            print(f"Erreur: Pas de connexion entre {from_terminal} et {to_terminal}")
            return
            
        # Mettre à jour la distance totale parcourue
        distance = self.network.get_distance(from_terminal, to_terminal)
        self._update_distance(distance)
        
        # Planifier l'arrivée de la barge
        arrival_time = self.current_time + travel_time
        self.add_event(arrival_time, EventType.BARGE_ARRIVAL, {
            'barge_id': barge_id,
            'terminal_id': to_terminal
        })
        
    def _handle_barge_arrival(self, event):
        """
        Gère un événement d'arrivée de barge.
        
        Args:
            event (Event): L'événement à traiter
        """
        barge_id = event.data['barge_id']
        terminal_id = event.data['terminal_id']
        
        # Récupérer la barge
        barge = self.barges.get(barge_id)
        if not barge:
            print(f"Erreur: Barge {barge_id} non trouvée")
            return
            
        # Mettre à jour la position de la barge
        barge.position = terminal_id
        barge.status = "idle"
        
        # Vérifier si la barge a atteint la fin de sa route
        if barge.service_id and barge.service_id in self.services:
            service = self.services[barge.service_id]
            if terminal_id == service.route[-1]:
                print(f"Barge {barge_id} a atteint la fin de sa route à {terminal_id}")
                return
                
            # Sinon, planifier le prochain départ
            current_idx = service.route.index(terminal_id)
            if current_idx < len(service.route) - 1:
                next_node = service.route[current_idx + 1]
                # Planifier le départ
                self.add_event(self.current_time, EventType.BARGE_DEPARTURE, {
                    'barge_id': barge_id,
                    'from_terminal': terminal_id,
                    'to_terminal': next_node
                })
                
        # Vérifier s'il y a des demandes à charger ou décharger
        self._check_loading_unloading(barge, terminal_id)
        
    def _handle_demand_arrival(self, event):
        """Traite l'arrivée d'une demande"""
        demand = event.data.get('demand')
        
        if demand:
            # Ajouter la demande au gestionnaire
            demand_id = demand.demand_id
            if not hasattr(self, 'demand_manager'):
                from src.model.demand_manager import DemandManager
                self.demand_manager = DemandManager()
            
            self.demand_manager.add_demand(demand)
            self.demands[demand_id] = demand
            
            print(f"Demande {demand_id} arrivée à t={self.current_time}")
            
            # Tenter d'assigner la demande à une barge
            self._assign_demand(demand)
        else:
            print(f"Demande None arrivée à t={self.current_time}")
        
    def _handle_loading_complete(self, event):
        """
        Gère un événement de fin de chargement.
        
        Args:
            event (Event): L'événement à traiter
        """
        barge_id = event.data['barge_id']
        terminal_id = event.data['terminal_id']
        demands = event.data.get('demands', [])
        
        if barge_id not in self.barges:
            print(f"Erreur: Barge {barge_id} non trouvée")
            return
            
        # Mettre à jour le statut de la barge
        barge = self.barges[barge_id]
        barge.status = "idle"
        
        # Mettre à jour les demandes
        for demand in demands:
            print(f"Demande {demand.demand_id} chargée sur la barge {barge_id} au terminal {terminal_id}")
            
        # Vérifier si la barge doit partir
        if barge.service_id and barge.service_id in self.services:
            service = self.services[barge.service_id]
            
            # Vérifier si le terminal actuel est dans la route du service
            if terminal_id in service.route:
                current_idx = service.route.index(terminal_id)
                if current_idx < len(service.route) - 1:
                    next_node = service.route[current_idx + 1]
                    # Planifier le départ
                    self.add_event(self.current_time, EventType.BARGE_DEPARTURE, {
                        'barge_id': barge_id,
                        'from_terminal': terminal_id,
                        'to_terminal': next_node
                    })
            # Si le terminal n'est pas dans la route mais est l'origine du service
            elif terminal_id == service.origin:
                # Planifier le départ vers la première étape de la route
                if service.route:
                    next_node = service.route[0]
                    self.add_event(self.current_time, EventType.BARGE_DEPARTURE, {
                        'barge_id': barge_id,
                        'from_terminal': terminal_id,
                        'to_terminal': next_node
                    })
            # Si le terminal n'est pas dans la route mais est la destination du service
            elif terminal_id == service.destination:
                # Planifier le départ vers l'origine pour recommencer le service
                self.add_event(self.current_time, EventType.BARGE_DEPARTURE, {
                    'barge_id': barge_id,
                    'from_terminal': terminal_id,
                    'to_terminal': service.origin
                })
                
    def _handle_unloading_complete(self, event):
        """
        Gère un événement de fin de déchargement.
        
        Args:
            event (Event): L'événement à traiter
        """
        barge_id = event.data['barge_id']
        terminal_id = event.data['terminal_id']
        demands = event.data.get('demands', [])
        
        if barge_id not in self.barges:
            print(f"Erreur: Barge {barge_id} non trouvée")
            return
            
        # Mettre à jour le statut de la barge
        barge = self.barges[barge_id]
        barge.status = "idle"
        
        # Mettre à jour les demandes
        for demand in demands:
            print(f"Demande {demand.demand_id} déchargée de la barge {barge_id} au terminal {terminal_id}")
            demand.status = "completed"
            self.demand_manager.complete_demand(demand.demand_id, self.current_time)
            
        # Vérifier si la barge doit partir
        if barge.service_id and barge.service_id in self.services:
            service = self.services[barge.service_id]
            
            # Vérifier si le terminal actuel est dans la route du service
            if terminal_id in service.route:
                current_idx = service.route.index(terminal_id)
                if current_idx < len(service.route) - 1:
                    next_node = service.route[current_idx + 1]
                    # Planifier le départ
                    self.add_event(self.current_time, EventType.BARGE_DEPARTURE, {
                        'barge_id': barge_id,
                        'from_terminal': terminal_id,
                        'to_terminal': next_node
                    })
            # Si le terminal n'est pas dans la route mais est l'origine du service
            elif terminal_id == service.origin:
                # Planifier le départ vers la première étape de la route
                if service.route:
                    next_node = service.route[0]
                    self.add_event(self.current_time, EventType.BARGE_DEPARTURE, {
                        'barge_id': barge_id,
                        'from_terminal': terminal_id,
                        'to_terminal': next_node
                    })
            # Si le terminal n'est pas dans la route mais est la destination du service
            elif terminal_id == service.destination:
                # Planifier le départ vers l'origine pour recommencer le service
                self.add_event(self.current_time, EventType.BARGE_DEPARTURE, {
                    'barge_id': barge_id,
                    'from_terminal': terminal_id,
                    'to_terminal': service.origin
                })
                
    def _check_loading_unloading(self, barge, terminal_id):
        """Vérifie si des chargements/déchargements sont nécessaires à ce terminal"""
        
        # Protection contre les méthodes manquantes
        if not hasattr(self, 'demand_manager'):
            print("Pas de gestionnaire de demande disponible")
            return
        
        try:
            # Tentative de récupérer les demandes à charger
            loading_demands = self.demand_manager.get_demands_for_loading(terminal_id, barge.barge_id)
        except AttributeError:
            # En cas d'erreur, utilisation d'une approche alternative
            print("Méthode get_demands_for_loading non disponible, utilisation d'une approche alternative")
            loading_demands = []
            for demand_id, demand in self.demands.items():
                if demand.origin == terminal_id and demand.status == "pending":
                    if demand.assigned_barge == barge.barge_id:
                        loading_demands.append(demand)
        
        try:
            # Tentative de récupérer les demandes à décharger
            unloading_demands = self.demand_manager.get_demands_for_unloading(terminal_id, barge.barge_id)
        except AttributeError:
            # En cas d'erreur, utilisation d'une approche alternative
            print("Méthode get_demands_for_unloading non disponible, utilisation d'une approche alternative")
            unloading_demands = []
            for demand_id, demand in self.demands.items():
                if demand.destination == terminal_id and demand.status == "assigned":
                    if demand.assigned_barge == barge.barge_id:
                        unloading_demands.append(demand)
        
        # Traitement des chargements
        for demand in loading_demands:
            print(f"Chargement de la demande {demand.demand_id} sur la barge {barge.barge_id} au terminal {terminal_id}")
            # Code de chargement ici
        
        # Traitement des déchargements
        for demand in unloading_demands:
            print(f"Déchargement de la demande {demand.demand_id} de la barge {barge.barge_id} au terminal {terminal_id}")
            # Code de déchargement ici
            # Marquer la demande comme complétée
            if hasattr(self.demand_manager, 'mark_as_completed'):
                self.demand_manager.mark_as_completed(demand.demand_id)
                
    def _assign_demand(self, demand):
        """Tente d'assigner une demande à une barge disponible"""
        # Logique simplifiée pour attribuer une demande
        # Trouver une barge disponible ayant la capacité suffisante
        for barge_id, barge in self.barges.items():
            if getattr(barge, 'current_load', 0) + demand.volume <= barge.capacity:
                # Trouver un service approprié
                for service_id, service in self.services.items():
                    if demand.origin in service.route and demand.destination in service.route:
                        # Vérifier l'ordre des terminaux dans la route
                        route = service.route
                        origin_idx = route.index(demand.origin)
                        dest_idx = route.index(demand.destination)
                        
                        # Si l'origine est avant la destination dans la route
                        if origin_idx < dest_idx:
                            print(f"Demande {demand.demand_id} assignée à la barge {barge_id} sur le service {service_id}")
                            demand.assigned_barge = barge_id
                            demand.status = "assigned"
                            
                            # Mettre à jour le chargement de la barge
                            if not hasattr(barge, 'current_load'):
                                barge.current_load = 0
                            barge.current_load += demand.volume
                            
                            # Enregistrer l'affectation
                            if hasattr(self, 'demand_manager'):
                                self.demand_manager.mark_as_assigned(demand.demand_id, barge_id)
                            
                            # Programmer un événement de départ si nécessaire
                            return True
        
        print(f"Aucune barge disponible pour la demande {demand.demand_id}")
        return False
        
    def _collect_statistics(self):
        """
        Collecte les statistiques finales de la simulation.
        """
        # Statistiques des demandes
        self.statistics['demand_statistics'] = self.demand_manager.get_statistics()
        
        # Statistiques des barges
        for barge_id, barge in self.barges.items():
            self.statistics['barge_statistics'][barge_id] = {
                'position': barge.position,
                'load': barge.current_load,
                'status': barge.status
            }
            
    def get_statistics(self):
        """
        Récupère les statistiques de la simulation.
        
        Returns:
            dict: Les statistiques de la simulation
        """
        return {
            'simulation_time': self.current_time,
            'events_processed': self.events_processed,
            'total_distance': self.total_distance,
            'demand_statistics': self.statistics['demand_statistics'],
            'barge_statistics': self.statistics['barge_statistics']
        }
    
    def get_demand_statistics(self):
        """Retourne les statistiques pour les demandes"""
        completed = sum(1 for d in self.demands.values() if getattr(d, 'status', '') == 'completed')
        pending = sum(1 for d in self.demands.values() if getattr(d, 'status', '') == 'pending')
        in_progress = sum(1 for d in self.demands.values() if getattr(d, 'status', '') == 'in_progress')
        assigned = sum(1 for d in self.demands.values() if getattr(d, 'assigned_barge', None) is not None)
        failed = sum(1 for d in self.demands.values() if getattr(d, 'status', '') == 'failed')
        
        return {
            'total': len(self.demands),
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'assigned': assigned,
            'failed': failed
        }

