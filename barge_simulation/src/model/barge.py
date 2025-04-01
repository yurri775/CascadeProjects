from dataclasses import dataclass
from typing import Optional

@dataclass
class Barge:
    barge_id: str
    capacity: float
    position: str
    current_load: float = 0
    status: str = "idle"
    
    
    def __init__(self, barge_id, capacity=50, position=None, service_id=None, loading_rate=10, unloading_rate=15):
        """
        Initialise une barge.
        
        Args:
            barge_id (str): Identifiant unique de la barge
            capacity (int): Capacité de transport de la barge
            position (str): Position initiale de la barge (ID du terminal)
            service_id (str): Identifiant du service assigné
            loading_rate (float): Taux de chargement (unités par heure)
            unloading_rate (float): Taux de déchargement (unités par heure)
        """
        self.barge_id = barge_id
        self.capacity = capacity
        self.current_load = 0
        self.position = position
        self.service_id = service_id
        self.status = "idle"  # idle, loading, moving, unloading
        self.route = []  # Liste des terminaux à visiter
        self.assigned_demands = []  # Liste des demandes assignées
        self.total_time = 0  # Temps total de simulation
        self.busy_time = 0  # Temps passé en charge
        self.loading_rate = loading_rate
        self.unloading_rate = unloading_rate
        
    def move_to(self, new_position, time):
        """
        Move the barge to a new position.
        
        Args:
            new_position (str): Target node ID in the network
            time (float): Current simulation time
        """
        self.position = new_position
        self.status = "moving"
        if self.current_load > 0:
            self.busy_time += time
        self.total_time = time
        
    def can_handle_load(self, load: float) -> bool:
        return self.current_load + load <= self.capacity
        
    def load_cargo(self, amount):
        """
        Load cargo onto the barge.
        
        Args:
            amount (float): Amount of cargo to load
            
        Returns:
            bool: True if loading successful, False if exceeds capacity
        """
        if self.current_load + amount <= self.capacity:
            self.current_load += amount
            self.status = "loading"
            return True
        return False
        
    def unload_cargo(self, amount):
        """
        Unload cargo from the barge.
        
        Args:
            amount (float): Amount of cargo to unload
            
        Returns:
            bool: True if unloading successful, False if not enough cargo
        """
        if self.current_load >= amount:
            self.current_load -= amount
            self.status = "unloading"
            return True
        return False
        
    def get_utilization(self):
        """
        Calculate the utilization of this barge.
        
        Returns:
            float: Utilization as a percentage (0-100)
        """
        # Calculate time spent in transit vs. idle
        if not self.route:
            return 0.0
        
        # This is a simplified calculation
        # In a real implementation, you would track actual times spent in each state
        transit_count = len(self.route)
        return min(100.0, (transit_count / 10.0) * 100.0)  # Arbitrary scaling
        
    def __str__(self):
        """
        Get a string representation of this barge.
        
        Returns:
            str: String representation
        """
        return f"Barge {self.barge_id}: pos={self.position}, load={self.current_load}/{self.capacity}, status={self.status}"
