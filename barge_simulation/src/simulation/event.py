#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module contenant la définition des événements pour la simulation.
"""
from enum import Enum, auto
from abc import ABC, abstractmethod

class EventType(Enum):
    """
    Types d'événements possibles dans la simulation.
    """
    # Événements liés aux demandes
    DEMAND_ARRIVAL = auto()       # Arrivée d'une nouvelle demande
    DEMAND_ASSIGNMENT = auto()    # Assignation d'une demande à une barge
    DEMAND_COMPLETION = auto()    # Complétion d'une demande
    DEMAND_EXPIRATION = auto()    # Expiration d'une demande (dépassement de la date limite)
    
    # Événements liés aux barges
    BARGE_DEPARTURE = auto()      # Départ d'une barge d'un terminal
    BARGE_ARRIVAL = auto()        # Arrivée d'une barge à un terminal
    BARGE_LOADING = auto()        # Début de chargement d'une barge
    BARGE_LOADING_COMPLETE = auto() # Fin de chargement d'une barge
    BARGE_UNLOADING = auto()      # Début de déchargement d'une barge
    BARGE_UNLOADING_COMPLETE = auto() # Fin de déchargement d'une barge
    BARGE_BREAKDOWN = auto()      # Panne d'une barge
    BARGE_REPAIR = auto()         # Réparation d'une barge
    
    # Événements liés aux terminaux
    TERMINAL_CONGESTION = auto()  # Congestion d'un terminal
    TERMINAL_DECONGESTION = auto() # Fin de congestion d'un terminal
    
    # Événements liés aux services
    SERVICE_START = auto()        # Début d'un service
    SERVICE_END = auto()          # Fin d'un service
    
    # Événements liés à la simulation
    SIMULATION_START = auto()     # Début de la simulation
    SIMULATION_END = auto()       # Fin de la simulation
    STATISTICS_COLLECTION = auto() # Collecte de statistiques
    
    # Événements génériques
    DELAY = auto()                # Retard générique
    CUSTOM = auto()               # Événement personnalisé

class Event:
    """
    Classe représentant un événement dans la simulation.
    """
    _next_id = 1
    
    def __init__(self, time, event_type, data=None):
        """
        Initialise un nouvel événement.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType ou str): Type de l'événement
            data (dict, optional): Données associées à l'événement
        """
        self.id = Event._next_id
        Event._next_id += 1
        self.time = time
        
        # Convertir le type d'événement en EventType si c'est une chaîne
        if isinstance(event_type, str):
            try:
                self.event_type = EventType[event_type.upper()]
            except KeyError:
                self.event_type = EventType.CUSTOM
                if data is None:
                    data = {}
                data["custom_type"] = event_type
        else:
            self.event_type = event_type
            
        self.data = data if data is not None else {}
        
        # Attributs supplémentaires
        self.quantity = self.data.get("quantity", 0)
        self.resource_id = self.data.get("resource_id", None)
        self.resource_type = self.data.get("resource_type", None)
        self.origin = self.data.get("origin", None)
        self.destination = self.data.get("destination", None)
        self.duration = self.data.get("duration", 0)
        
    def __str__(self):
        """
        Retourne une représentation textuelle de l'événement.
        
        Returns:
            str: Représentation textuelle
        """
        return f"Event(id={self.id}, time={self.time}, type={self.event_type.name if isinstance(self.event_type, EventType) else self.event_type}, data={self.data})"
    
    def __repr__(self):
        """
        Retourne une représentation textuelle de l'événement pour le débogage.
        
        Returns:
            str: Représentation textuelle
        """
        return self.__str__()
    
    def __lt__(self, other):
        """
        Compare deux événements en fonction de leur temps et de leur ID.
        
        Args:
            other (Event): Autre événement
            
        Returns:
            bool: True si cet événement se produit avant l'autre
        """
        if self.time == other.time:
            return self.id < other.id
        return self.time < other.time
    
    def get_resource(self):
        """
        Retourne l'identifiant de la ressource concernée par l'événement.
        
        Returns:
            str: Identifiant de la ressource
        """
        # Déterminer la ressource en fonction du type d'événement
        if self.event_type in [EventType.DEMAND_ARRIVAL, EventType.DEMAND_ASSIGNMENT, 
                              EventType.DEMAND_COMPLETION, EventType.DEMAND_EXPIRATION]:
            return self.data.get("demand_id", None)
        elif self.event_type in [EventType.BARGE_DEPARTURE, EventType.BARGE_ARRIVAL, 
                                EventType.BARGE_LOADING, EventType.BARGE_LOADING_COMPLETE,
                                EventType.BARGE_UNLOADING, EventType.BARGE_UNLOADING_COMPLETE,
                                EventType.BARGE_BREAKDOWN, EventType.BARGE_REPAIR]:
            return self.data.get("barge_id", None)
        elif self.event_type in [EventType.TERMINAL_CONGESTION, EventType.TERMINAL_DECONGESTION]:
            return self.data.get("terminal_id", None)
        elif self.event_type in [EventType.SERVICE_START, EventType.SERVICE_END]:
            return self.data.get("service_id", None)
        else:
            return self.resource_id
    
    def get_location(self):
        """
        Retourne la localisation de l'événement.
        
        Returns:
            str: Localisation de l'événement
        """
        if self.event_type in [EventType.BARGE_ARRIVAL, EventType.BARGE_LOADING, 
                              EventType.BARGE_LOADING_COMPLETE, EventType.BARGE_UNLOADING, 
                              EventType.BARGE_UNLOADING_COMPLETE]:
            return self.data.get("terminal_id", None)
        elif self.event_type == EventType.BARGE_DEPARTURE:
            return self.data.get("from", None)
        else:
            return None
    
    def get_destination(self):
        """
        Retourne la destination de l'événement.
        
        Returns:
            str: Destination de l'événement
        """
        if self.event_type == EventType.BARGE_DEPARTURE:
            return self.data.get("to", None)
        else:
            return self.destination
    
    def get_quantity(self):
        """
        Retourne la quantité associée à l'événement.
        
        Returns:
            float: Quantité
        """
        if "quantity" in self.data:
            return self.data["quantity"]
        elif "volume" in self.data:
            return self.data["volume"]
        else:
            return self.quantity
    
    def get_duration(self):
        """
        Retourne la durée associée à l'événement.
        
        Returns:
            float: Durée
        """
        if "duration" in self.data:
            return self.data["duration"]
        else:
            return self.duration

# Classes spécialisées pour différents types d'événements
class DemandEvent(Event):
    """
    Classe représentant un événement lié à une demande.
    """
    def __init__(self, time, event_type, demand_id, volume=0, origin=None, destination=None, data=None):
        """
        Initialise un nouvel événement de demande.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType): Type de l'événement
            demand_id (str): Identifiant de la demande
            volume (float, optional): Volume de la demande
            origin (str, optional): Origine de la demande
            destination (str, optional): Destination de la demande
            data (dict, optional): Données supplémentaires
        """
        if data is None:
            data = {}
        
        data.update({
            "demand_id": demand_id,
            "resource_type": "demand",
            "resource_id": demand_id,
            "quantity": volume,
            "origin": origin,
            "destination": destination
        })
        
        super().__init__(time, event_type, data)

class BargeEvent(Event):
    """
    Classe représentant un événement lié à une barge.
    """
    def __init__(self, time, event_type, barge_id, terminal=None, origin=None, destination=None, 
                 load=0, data=None):
        """
        Initialise un nouvel événement de barge.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType): Type de l'événement
            barge_id (str): Identifiant de la barge
            terminal (str, optional): Terminal concerné
            origin (str, optional): Origine du déplacement
            destination (str, optional): Destination du déplacement
            load (float, optional): Charge de la barge
            data (dict, optional): Données supplémentaires
        """
        if data is None:
            data = {}
        
        data.update({
            "barge_id": barge_id,
            "resource_type": "barge",
            "resource_id": barge_id,
            "quantity": load
        })
        
        if terminal:
            data["terminal_id"] = terminal
        
        if origin and destination:
            data["from"] = origin
            data["to"] = destination
        
        super().__init__(time, event_type, data)

class TerminalEvent(Event):
    """
    Classe représentant un événement lié à un terminal.
    """
    def __init__(self, time, event_type, terminal_id, capacity=0, data=None):
        """
        Initialise un nouvel événement de terminal.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType): Type de l'événement
            terminal_id (str): Identifiant du terminal
            capacity (float, optional): Capacité du terminal
            data (dict, optional): Données supplémentaires
        """
        if data is None:
            data = {}
        
        data.update({
            "terminal_id": terminal_id,
            "resource_type": "terminal",
            "resource_id": terminal_id,
            "quantity": capacity
        })
        
        super().__init__(time, event_type, data)

class ServiceEvent(Event):
    """
    Classe représentant un événement lié à un service.
    """
    def __init__(self, time, event_type, service_id, capacity=0, origin=None, destination=None, data=None):
        """
        Initialise un nouvel événement de service.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType): Type de l'événement
            service_id (str): Identifiant du service
            capacity (float, optional): Capacité du service
            origin (str, optional): Origine du service
            destination (str, optional): Destination du service
            data (dict, optional): Données supplémentaires
        """
        if data is None:
            data = {}
        
        data.update({
            "service_id": service_id,
            "resource_type": "service",
            "resource_id": service_id,
            "quantity": capacity,
            "origin": origin,
            "destination": destination
        })
        
        super().__init__(time, event_type, data)

class SimulationEvent(Event):
    """
    Classe représentant un événement lié à la simulation.
    """
    def __init__(self, time, event_type, duration=0, data=None):
        """
        Initialise un nouvel événement de simulation.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType): Type de l'événement
            duration (float, optional): Durée de l'événement
            data (dict, optional): Données supplémentaires
        """
        if data is None:
            data = {}
        
        data.update({
            "resource_type": "simulation",
            "duration": duration
        })
        
        super().__init__(time, event_type, data)

# Factory pour créer des événements spécifiques
class EventFactory:
    """
    Factory pour créer des événements spécifiques.
    """
    @staticmethod
    def create_demand_arrival(time, demand_id, volume=0, origin=None, destination=None, data=None):
        """
        Crée un événement d'arrivée de demande.
        
        Args:
            time (float): Temps auquel l'événement se produit
            demand_id (str): Identifiant de la demande
            volume (float, optional): Volume de la demande
            origin (str, optional): Origine de la demande
            destination (str, optional): Destination de la demande
            data (dict, optional): Données supplémentaires
            
        Returns:
            DemandEvent: Événement créé
        """
        return DemandEvent(time, EventType.DEMAND_ARRIVAL, demand_id, volume, origin, destination, data)
    
    @staticmethod
    def create_demand_assignment(time, demand_id, barge_id, data=None):
        """
        Crée un événement d'assignation de demande.
        
        Args:
            time (float): Temps auquel l'événement se produit
            demand_id (str): Identifiant de la demande
            barge_id (str): Identifiant de la barge
            data (dict, optional): Données supplémentaires
            
        Returns:
            DemandEvent: Événement créé
        """
        if data is None:
            data = {}
        data["barge_id"] = barge_id
        
        return DemandEvent(time, EventType.DEMAND_ASSIGNMENT, demand_id, data=data)
    
    @staticmethod
    def create_barge_departure(time, barge_id, origin, destination, load=0, data=None):
        """
        Crée un événement de départ de barge.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            origin (str): Terminal d'origine
            destination (str): Terminal de destination
            load (float, optional): Charge de la barge
            data (dict, optional): Données supplémentaires
            
        Returns:
            BargeEvent: Événement créé
        """
        return BargeEvent(time, EventType.BARGE_DEPARTURE, barge_id, None, origin, destination, load, data)
    
    @staticmethod
    def create_barge_arrival(time, barge_id, terminal, load=0, data=None):
        """
        Crée un événement d'arrivée de barge.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            terminal (str): Terminal d'arrivée
            load (float, optional): Charge de la barge
            data (dict, optional): Données supplémentaires
            
        Returns:
            BargeEvent: Événement créé
        """
        return BargeEvent(time, EventType.BARGE_ARRIVAL, barge_id, terminal, None, None, load, data)
    
    @staticmethod
    def create_loading_complete(time, barge_id, terminal, demands=None, data=None):
        """
        Crée un événement de fin de chargement.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            terminal (str): Terminal de chargement
            demands (list, optional): Liste des demandes chargées
            data (dict, optional): Données supplémentaires
            
        Returns:
            BargeEvent: Événement créé
        """
        if data is None:
            data = {}
        
        if demands:
            data["demands"] = demands
        
        return BargeEvent(time, EventType.BARGE_LOADING_COMPLETE, barge_id, terminal, data=data)
    
    @staticmethod
    def create_unloading_complete(time, barge_id, terminal, demands=None, data=None):
        """
        Crée un événement de fin de déchargement.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            terminal (str): Terminal de déchargement
            demands (list, optional): Liste des demandes déchargées
            data (dict, optional): Données supplémentaires
            
        Returns:
            BargeEvent: Événement créé
        """
        if data is None:
            data = {}
        
        if demands:
            data["demands"] = demands
        
        return BargeEvent(time, EventType.BARGE_UNLOADING_COMPLETE, barge_id, terminal, data=data)
    
    @staticmethod
    def create_simulation_end(time, data=None):
        """
        Crée un événement de fin de simulation.
        
        Args:
            time (float): Temps auquel l'événement se produit
            data (dict, optional): Données supplémentaires
            
        Returns:
            SimulationEvent: Événement créé
        """
        return SimulationEvent(time, EventType.SIMULATION_END, data=data)
