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
        self.events = []  # Liste triée par temps
        self.current_time = 0
    
    def add_event(self, time, event_type, data):
        """
        Ajoute un événement avec vérification de temps.
        
        Args:
            time (float): Temps auquel l'événement se produit
            event_type (EventType ou str): Type de l'événement
            data (dict): Données associées à l'événement
            
        Returns:
            Event: Événement créé et ajouté
            
        Raises:
            ValueError: Si le temps de l'événement est dans le passé
        """
        if time < self.current_time:
            raise ValueError(f"Impossible de planifier un événement dans le passé: t={time} < {self.current_time}")
        
        event = Event(time, event_type, data)
        heapq.heappush(self.events, event)
        return event
    
    def get_next_event(self):
        """
        Récupère le prochain événement.
        
        Returns:
            Event: Prochain événement, ou None si l'échéancier est vide
        """
        if not self.events:
            return None
        return heapq.heappop(self.events)
    
    def pop_next_event_bag(self):
        """Récupère et supprime le prochain groupe d'événements simultanés."""
        if not self.events:
            return []
            
        next_time = self.events[0].time
        event_bag = []
        
        # Collecter tous les événements au même temps
        for i in range(len(self.events)):
            if i >= len(self.events):
                break
                
            if self.events[i].time == next_time:
                event_bag.append(self.events.pop(0))
            else:
                break
                
        return event_bag
