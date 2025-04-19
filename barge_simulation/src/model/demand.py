class Demand:
    """
    Représente une demande de transport avec toutes ses caractéristiques.
    """
    
    CUSTOMER_TYPES = {
        'R': 'Regular',      # Regular customer demands
        'P': 'Partial',      # Partial-spot demands
        'F': 'Full'         # Fully-spot demands
    }
    
    FARE_CLASSES = {
        'S': 'Standard',
        'E': 'Express'
    }
    
    def __init__(self, demand_id, origin, destination, volume, 
                 arrival_time=None, availability_time=None, due_date=None,
                 customer_type=None, fare_class=None, unit_fare=0, 
                 container_type=None, **kwargs):  # Ajout de container_type et kwargs
        """
        Initialise une demande de transport.
        
        Args:
            demand_id (str): Identifiant unique de la demande
            origin (str): Terminal d'origine
            destination (str): Terminal de destination
            volume (int): Volume en TEUs
            arrival_time (int, optional): Temps d'arrivée à l'origine
            availability_time (int, optional): Temps de disponibilité à l'origine
            due_date (int, optional): Date limite d'arrivée à destination
            customer_type (str, optional): Type de client ('R', 'P', 'F')
            fare_class (str, optional): Classe tarifaire ('S', 'E')
            unit_fare (float, optional): Valeur tarifaire par TEU
            container_type (str, optional): Type de conteneur
        """
        self.demand_id = demand_id
        self.origin = origin
        self.destination = destination
        self.volume = volume
        
        # Gestion des différents noms d'attributs de temps
        self.arrival_time = arrival_time
        self.availability_time = availability_time if availability_time is not None else arrival_time
        self.due_date = due_date
        
        # Informations sur le client et la tarification
        self.customer_type = customer_type  # R (Regular), P (Partial-spot), F (Fully-spot)
        self.fare_class = fare_class        # S (Standard), E (Express)
        self.unit_fare = unit_fare          # Valeur tarifaire par TEU
        self.container_type = container_type # Type de conteneur
        
        # État initial
        self.status = "pending"
        self.assigned_barge = None
        self.current_position = origin
        self.assigned_route = []
        
    @property
    def is_regular(self):
        """Vérifie si c'est un client régulier."""
        return self.customer_type == 'R'
    
    @property
    def is_partial(self):
        """Vérifie si c'est une demande partielle."""
        return self.customer_type == 'P'
    
    @property
    def is_full(self):
        """Vérifie si c'est une demande complète."""
        return self.customer_type == 'F'
    
    @property
    def is_express(self):
        """Vérifie si c'est une demande express."""
        return self.fare_class == 'E'
        
    def is_on_time(self):
        """
        Check if the demand was completed on time.
        
        Returns:
            bool: True if completed on time, False otherwise
        """
        if self.status != "completed" or self.due_date is None:
            return False
        
        return self.completion_time <= self.due_date
        
    def __str__(self):
        """
        Get a string representation of this demand.
        
        Returns:
            str: String representation
        """
        return (f"Demand {self.demand_id}: {self.origin} -> {self.destination}, "
                f"volume={self.volume}, status={self.status}")


class DemandManager:
    """
    Manages demands in the simulation.
    """
    def __init__(self):
        """
        Initialize the demand manager.
        """
        self.demands = {}  # Dictionary of demand_id -> Demand
        
    def add_demand(self, demand):
        """
        Add a demand to the manager.
        
        Args:
            demand (Demand): Demand to add
        """
        self.demands[demand.demand_id] = demand
        
    def has_demand(self, demand_id):
        """
        Check if a demand exists.
        
        Args:
            demand_id (str): Demand ID to check
            
        Returns:
            bool: True if the demand exists, False otherwise
        """
        return demand_id in self.demands
        
    def get_demand(self, demand_id):
        """
        Get a demand by ID.
        
        Args:
            demand_id (str): Demand ID to get
            
        Returns:
            Demand: The demand, or None if not found
        """
        return self.demands.get(demand_id)
        
    def get_pending_demands(self, current_time):
        """
        Get all pending demands that have arrived by the current time.
        
        Args:
            current_time (float): Current simulation time
            
        Returns:
            list: List of pending demands
        """
        return [demand for demand in self.demands.values() 
                if demand.status == "pending" and demand.arrival_time <= current_time]
                
    def get_assigned_demands(self, barge_id):
        """
        Get all demands assigned to a specific barge.
        
        Args:
            barge_id (str): Barge ID
            
        Returns:
            list: List of assigned demands
        """
        return [demand for demand in self.demands.values() 
                if (demand.status == "assigned" or demand.status == "in_progress") 
                and demand.assigned_barge == barge_id]
                
    def assign_demand(self, demand_id, barge_id, time=None):
        """
        Assign a demand to a barge.
        
        Args:
            demand_id (str): Demand ID
            barge_id (str): Barge ID
            time (float, optional): Assignment time
            
        Returns:
            bool: True if assignment successful, False otherwise
        """
        if demand_id in self.demands:
            demand = self.demands[demand_id]
            
            if demand.status == "pending":
                demand.status = "assigned"
                demand.assigned_barge = barge_id
                demand.assignment_time = time
                return True
                
        return False
        
    def start_demand(self, demand_id, time=None):
        """
        Mark a demand as in progress.
        
        Args:
            demand_id (str): Demand ID
            time (float, optional): Start time
            
        Returns:
            bool: True if successful, False otherwise
        """
        if demand_id in self.demands:
            demand = self.demands[demand_id]
            
            if demand.status == "assigned":
                demand.status = "in_progress"
                demand.start_time = time
                return True
                
        return False
        
    def complete_demand(self, demand_id, time=None):
        """
        Mark a demand as completed.
        
        Args:
            demand_id (str): Demand ID
            time (float, optional): Completion time
            
        Returns:
            bool: True if successful, False otherwise
        """
        if demand_id in self.demands:
            demand = self.demands[demand_id]
            
            if demand.status == "in_progress":
                demand.status = "completed"
                demand.completion_time = time
                return True
                
        return False
        
    def fail_demand(self, demand_id, time=None):
        """
        Mark a demand as failed.
        
        Args:
            demand_id (str): Demand ID
            time (float, optional): Failure time
            
        Returns:
            bool: True if successful, False otherwise
        """
        if demand_id in self.demands:
            demand = self.demands[demand_id]
            
            if demand.status in ["pending", "assigned", "in_progress"]:
                demand.status = "failed"
                return True
                
        return False
        
    def get_statistics(self):
        """
        Get statistics about the demands.
        
        Returns:
            dict: Dictionary with demand statistics
        """
        status_counts = {
            "total": len(self.demands),
            "pending": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }
        
        for demand in self.demands.values():
            if demand.status in status_counts:
                status_counts[demand.status] += 1
                
        return status_counts
        
    def get_demands_for_loading(self, terminal_id, barge_id=None):
        """
        Get demands that need to be loaded at a terminal onto a specific barge.
        
        Args:
            terminal_id (str): Terminal ID where loading would occur
            barge_id (str, optional): Barge ID to load onto, or None for any barge
            
        Returns:
            list: List of demands ready for loading
        """
        loading_demands = []
        
        for demand in self.demands.values():
            # Check if demand is at origin terminal and pending or assigned to the specified barge
            if demand.origin == terminal_id and demand.status in ["pending", "assigned"]:
                if barge_id is None or demand.assigned_barge == barge_id:
                    loading_demands.append(demand)
                    
        return loading_demands
        
    def get_demands_for_unloading(self, terminal_id, barge_id=None):
        """
        Get demands that need to be unloaded at a terminal from a specific barge.
        
        Args:
            terminal_id (str): Terminal ID where unloading would occur
            barge_id (str, optional): Barge ID to unload from, or None for any barge
            
        Returns:
            list: List of demands ready for unloading
        """
        unloading_demands = []
        
        for demand in self.demands.values():
            # Check if demand destination matches terminal and is in progress with the specified barge
            if demand.destination == terminal_id and demand.status == "in_progress":
                if barge_id is None or demand.assigned_barge == barge_id:
                    unloading_demands.append(demand)
                    
        return unloading_demands
