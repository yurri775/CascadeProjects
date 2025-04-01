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

class BargeSimulator:
    """
    Simulateur pour le système de transport par barges utilisant la simulation à événements discrets.
    """
    def __init__(self, network, routing_manager):
        """
        Initialise le simulateur.
        
        Args:
            network (SpaceTimeNetwork): Le réseau espace-temps
            routing_manager (RoutingManager): Le gestionnaire de routage
        """
        self.network = network
        self.routing_manager = routing_manager
        self.barges = {}  # Dictionnaire barge_id -> Barge
        self.services = {}  # Dictionnaire service_id -> Service
        self.scheduler = EventScheduler()  # Échéancier des événements
        self.processed_events = []  # Liste des événements traités
        self.current_time = 0
        self.max_time = 0  # Temps maximum de simulation
        self.events_processed = 0
        self.total_distance = 0
        self.demand_manager = DemandManager()
        self.statistics = {
            'terminal_utilization': {},  # Terminal ID -> pourcentage d'utilisation
            'service_utilization': {},   # Service ID -> pourcentage d'utilisation
            'barge_statistics': {},      # Barge ID -> statistiques
            'demand_statistics': {}      # Statistiques des demandes
        }
        
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
        """
        Exécute la simulation jusqu'à un temps spécifié ou jusqu'à ce que l'échéancier soit vide.
        
        Args:
            until (float): Temps maximum de simulation
        """
        self.max_time = until
        
        # Ajouter l'événement de fin de simulation
        self.add_event(until, EventType.SIMULATION_END)
        
        # Boucle principale de simulation
        while self.current_time <= self.max_time:
            # Récupérer le prochain sac d'événements
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
                if event.event_type == EventType.SIMULATION_END or self.current_time > self.max_time:
                    print(f"Simulation terminée à t={self.current_time}: Temps maximum atteint.")
                    break
                
                # Traiter l'événement
                self._process_event(event)
                self.events_processed += 1
                
        # Collecter les statistiques finales
        self._collect_statistics()
        
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
        self.total_distance += self.network.get_distance(from_terminal, to_terminal)
        
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
        """
        Gère un événement d'arrivée de demande.
        
        Args:
            event (Event): L'événement à traiter
        """
        # Récupérer les informations de la demande depuis l'événement
        demand_id = event.data.get('demand_id')
        volume = event.data.get('quantity', 0)  # Utiliser 'quantity' au lieu de 'volume' avec une valeur par défaut de 0
        origin = event.data.get('origin')
        destination = event.data.get('destination')
        
        print(f"Demande {demand_id} arrivée à t={self.current_time}")
        
        # Créer la demande si elle n'existe pas déjà dans le gestionnaire de demandes
        demand = self.demand_manager.get_demand(demand_id)
        if not demand:
            # Créer une nouvelle demande avec les informations de l'événement
            # Définir une date d'échéance par défaut (temps actuel + délai basé sur le volume)
            due_date = self.current_time + max(10, float(volume or 0) * 0.2)  # Au moins 10 unités de temps ou 0.2 unités par volume
            
            from src.model.demand import Demand
            demand = Demand(
                demand_id=demand_id,
                origin=origin or "Unknown",  # Valeur par défaut si origin est None
                destination=destination or "Unknown",  # Valeur par défaut si destination est None
                volume=float(volume or 0),  # Valeur par défaut si volume est None
                availability_time=self.current_time,
                due_date=due_date
            )
            self.demand_manager.add_demand(demand)
        
        # Mettre à jour le statut de la demande
        demand.status = "pending"
        
        # Essayer de trouver une barge disponible pour cette demande
        self._assign_demand_to_barge(demand)
        
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
        """
        Vérifie s'il y a des demandes à charger ou décharger pour une barge à un terminal.
        
        Args:
            barge (Barge): La barge
            terminal_id (str): L'identifiant du terminal
        """
        # Vérifier s'il y a des demandes à décharger
        unloading_demands = []
        for demand_id in barge.assigned_demands:
            demand = self.demand_manager.get_demand(demand_id)
            if demand and demand.destination == terminal_id and demand.status == "in_transit":
                unloading_demands.append(demand)
                
        if unloading_demands:
            # Calculer le temps de déchargement
            unloading_time = sum(demand.volume / barge.unloading_rate for demand in unloading_demands)
            
            # Planifier l'événement de fin de déchargement
            self.add_event(self.current_time + unloading_time, EventType.BARGE_UNLOADING_COMPLETE, {
                'barge_id': barge.barge_id,
                'terminal_id': terminal_id,
                'demands': unloading_demands
            })
            
            # Mettre à jour le statut de la barge
            barge.status = "unloading"
            return
            
        # Vérifier s'il y a des demandes à charger
        loading_demands = self.demand_manager.get_demands_for_loading(terminal_id, barge.barge_id)
        
        if loading_demands:
            # Calculer la capacité disponible
            available_capacity = barge.capacity - barge.current_load
            
            # Vérifier la capacité disponible
            total_volume = sum(demand.volume for demand in loading_demands)
            if total_volume <= available_capacity:
                # Calculer le temps de chargement
                loading_time = sum(demand.volume / barge.loading_rate for demand in loading_demands)
                
                # Planifier l'événement de fin de chargement
                self.add_event(self.current_time + loading_time, EventType.BARGE_LOADING_COMPLETE, {
                    'barge_id': barge.barge_id,
                    'terminal_id': terminal_id,
                    'demands': loading_demands
                })
                
                # Mettre à jour le statut de la barge
                barge.status = "loading"
                
                # Mettre à jour les demandes
                for demand in loading_demands:
                    # Charger la demande sur la barge
                    barge.assigned_demands.append(demand.demand_id)
                    demand.status = "in_progress"
                    loaded = barge.load_cargo(demand.volume)
                    
                    # Mettre à jour les statistiques
                    self.demand_manager.start_demand(demand.demand_id, self.current_time)
                    
                    print(f"Chargement de la demande {demand.demand_id} sur la barge {barge.barge_id} au terminal {terminal_id}")
                
    def _assign_demand_to_barge(self, demand):
        """Assigne une demande à une barge disponible."""
        best_barge = None
        min_distance = float('inf')

        for barge_id, barge in self.barges.items():
            # Vérifier la capacité disponible
            available_capacity = barge.capacity - barge.current_load
            
            if available_capacity >= demand.volume:
                # Calculer la distance jusqu'à l'origine de la demande
                if barge.position != demand.origin:
                    distance = self.network.get_distance(barge.position, demand.origin)
                    if distance < min_distance:
                        min_distance = distance
                        best_barge = barge
                else:
                    # Priorité aux barges déjà à l'origine
                    best_barge = barge
                    break

        if best_barge:
            # Assigner la demande
            demand.assigned_barge = best_barge.barge_id
            demand.status = "assigned"
            best_barge.assigned_demands.append(demand.demand_id)
            
            # Planifier le mouvement si nécessaire
            if best_barge.position != demand.origin:
                self.add_event(
                    self.current_time,
                    EventType.BARGE_DEPARTURE,
                    {
                        'barge_id': best_barge.barge_id,
                        'from_terminal': best_barge.position,
                        'to_terminal': demand.origin
                    }
                )
            else:
                # Commencer le chargement immédiatement
                self._check_loading_unloading(best_barge, demand.origin)
                
            return True
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
