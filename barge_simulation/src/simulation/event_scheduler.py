#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module contenant l'implémentation de l'échéancier des événements.
"""
import heapq
from src.simulation.event import Event, EventType, EventFactory

class EventBag:
    """
    Classe représentant un sac d'événements qui se produisent au même moment.
    """
    def __init__(self, time):
        """
        Initialise un nouveau sac d'événements.
        
        Args:
            time (float): Temps auquel les événements du sac se produisent
        """
        self.time = time
        self.events = []
    
    def add_event(self, event):
        """
        Ajoute un événement au sac.
        
        Args:
            event (Event): Événement à ajouter
        """
        self.events.append(event)
    
    def __iter__(self):
        """
        Itérateur sur les événements du sac.
        
        Yields:
            Event: Prochain événement du sac
        """
        for event in self.events:
            yield event
    
    def __len__(self):
        """
        Retourne le nombre d'événements dans le sac.
        
        Returns:
            int: Nombre d'événements
        """
        return len(self.events)
    
    def __lt__(self, other):
        """
        Compare deux sacs d'événements en fonction de leur temps.
        
        Args:
            other (EventBag): Autre sac d'événements
            
        Returns:
            bool: True si ce sac se produit avant l'autre
        """
        return self.time < other.time
    
    def __gt__(self, other):
        """
        Compare deux sacs d'événements en fonction de leur temps.
        
        Args:
            other (EventBag): Autre sac d'événements
            
        Returns:
            bool: True si ce sac se produit après l'autre
        """
        return self.time > other.time
    
    def __eq__(self, other):
        """
        Compare deux sacs d'événements en fonction de leur temps.
        
        Args:
            other (EventBag): Autre sac d'événements
            
        Returns:
            bool: True si les deux sacs se produisent au même moment
        """
        return self.time == other.time
    
    def __str__(self):
        """
        Retourne une représentation textuelle du sac d'événements.
        
        Returns:
            str: Représentation textuelle
        """
        return f"EventBag(time={self.time}, events={len(self.events)})"
    
    def __repr__(self):
        """
        Retourne une représentation textuelle du sac d'événements pour le débogage.
        
        Returns:
            str: Représentation textuelle
        """
        return self.__str__()

class EventScheduler:
    """
    Classe représentant un échéancier d'événements pour la simulation.
    """
    def __init__(self):
        """
        Initialise un nouvel échéancier d'événements.
        """
        self.event_bags = []  # File de priorité des sacs d'événements
        self.current_time = 0.0  # Temps courant de la simulation
        self.event_count = 0  # Nombre total d'événements traités
    
    def add_event(self, time, event_type, data=None):
        """
        Ajoute un événement à l'échéancier.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType ou str): Type de l'événement
            data (dict, optional): Données associées à l'événement
            
        Returns:
            Event: Événement créé et ajouté
        """
        # Créer l'événement
        event = Event(time, event_type, data)
        
        # Trouver ou créer le sac d'événements correspondant
        for bag in self.event_bags:
            if bag.time == time:
                bag.add_event(event)
                break
        else:
            # Aucun sac trouvé, en créer un nouveau
            bag = EventBag(time)
            bag.add_event(event)
            heapq.heappush(self.event_bags, bag)
        
        self.event_count += 1
        return event
    
    def add_event_object(self, event):
        """
        Ajoute un objet événement existant à l'échéancier.
        
        Args:
            event (Event): Événement à ajouter
            
        Returns:
            Event: Événement ajouté
        """
        # Trouver ou créer le sac d'événements correspondant
        for bag in self.event_bags:
            if bag.time == event.time:
                bag.add_event(event)
                break
        else:
            # Aucun sac trouvé, en créer un nouveau
            bag = EventBag(event.time)
            bag.add_event(event)
            heapq.heappush(self.event_bags, bag)
        
        self.event_count += 1
        return event
    
    def add_demand_arrival(self, time, demand_id, volume=0, origin=None, destination=None, data=None):
        """
        Ajoute un événement d'arrivée de demande.
        
        Args:
            time (float): Temps auquel l'événement se produit
            demand_id (str): Identifiant de la demande
            volume (float, optional): Volume de la demande
            origin (str, optional): Origine de la demande
            destination (str, optional): Destination de la demande
            data (dict, optional): Données supplémentaires
            
        Returns:
            Event: Événement créé et ajouté
        """
        event = EventFactory.create_demand_arrival(time, demand_id, volume, origin, destination, data)
        return self.add_event_object(event)
    
    def add_barge_departure(self, time, barge_id, origin, destination, load=0, data=None):
        """
        Ajoute un événement de départ de barge.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            origin (str): Terminal d'origine
            destination (str): Terminal de destination
            load (float, optional): Charge de la barge
            data (dict, optional): Données supplémentaires
            
        Returns:
            Event: Événement créé et ajouté
        """
        event = EventFactory.create_barge_departure(time, barge_id, origin, destination, load, data)
        return self.add_event_object(event)
    
    def add_barge_arrival(self, time, barge_id, terminal, load=0, data=None):
        """
        Ajoute un événement d'arrivée de barge.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            terminal (str): Terminal d'arrivée
            load (float, optional): Charge de la barge
            data (dict, optional): Données supplémentaires
            
        Returns:
            Event: Événement créé et ajouté
        """
        event = EventFactory.create_barge_arrival(time, barge_id, terminal, load, data)
        return self.add_event_object(event)
    
    def add_loading_complete(self, time, barge_id, terminal, demands=None, data=None):
        """
        Ajoute un événement de fin de chargement.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            terminal (str): Terminal de chargement
            demands (list, optional): Liste des demandes chargées
            data (dict, optional): Données supplémentaires
            
        Returns:
            Event: Événement créé et ajouté
        """
        event = EventFactory.create_loading_complete(time, barge_id, terminal, demands, data)
        return self.add_event_object(event)
    
    def add_unloading_complete(self, time, barge_id, terminal, demands=None, data=None):
        """
        Ajoute un événement de fin de déchargement.
        
        Args:
            time (float): Temps auquel l'événement se produit
            barge_id (str): Identifiant de la barge
            terminal (str): Terminal de déchargement
            demands (list, optional): Liste des demandes déchargées
            data (dict, optional): Données supplémentaires
            
        Returns:
            Event: Événement créé et ajouté
        """
        event = EventFactory.create_unloading_complete(time, barge_id, terminal, demands, data)
        return self.add_event_object(event)
    
    def add_simulation_end(self, time, data=None):
        """
        Ajoute un événement de fin de simulation.
        
        Args:
            time (float): Temps auquel l'événement se produit
            data (dict, optional): Données supplémentaires
            
        Returns:
            Event: Événement créé et ajouté
        """
        event = EventFactory.create_simulation_end(time, data)
        return self.add_event_object(event)
    
    def pop_next_event_bag(self):
        """
        Récupère le prochain sac d'événements de l'échéancier.
        
        Returns:
            EventBag: Prochain sac d'événements, ou None si l'échéancier est vide
        """
        if not self.event_bags:
            return None
        
        bag = heapq.heappop(self.event_bags)
        self.current_time = bag.time
        return bag
    
    def get_next_event_time(self):
        """
        Retourne le temps du prochain événement.
        
        Returns:
            float: Temps du prochain événement, ou None si l'échéancier est vide
        """
        if not self.event_bags:
            return None
        
        return self.event_bags[0].time
    
    def is_empty(self):
        """
        Vérifie si l'échéancier est vide.
        
        Returns:
            bool: True si l'échéancier est vide
        """
        return len(self.event_bags) == 0
    
    def get_all_events(self):
        """
        Retourne tous les événements de l'échéancier.
        
        Returns:
            list: Liste de tous les événements, triés par temps
        """
        events = []
        for bag in sorted(self.event_bags):
            for event in bag.events:
                events.append(event)
        return events
    
    def get_event_count(self):
        """
        Retourne le nombre total d'événements traités.
        
        Returns:
            int: Nombre d'événements
        """
        return self.event_count
    
    def __str__(self):
        """
        Retourne une représentation textuelle de l'échéancier.
        
        Returns:
            str: Représentation textuelle
        """
        return f"EventScheduler(bags={len(self.event_bags)}, events={self.event_count})"
    
    def __repr__(self):
        """
        Retourne une représentation textuelle de l'échéancier pour le débogage.
        
        Returns:
            str: Représentation textuelle
        """
        return self.__str__()
