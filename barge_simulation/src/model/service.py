class Service:
    """
    Représente un service de transport par barge avec gestion détaillée des legs et des arrêts.
    """
    
    def __init__(self, service_id, origin, destination, legs=None, start_time=0, end_time=0, 
                 vessel_types=None, capacity=0, frequency=None, duration=None):
        """
        Initialise un nouveau service.
        
        Args:
            service_id (str): Identifiant unique du service
            origin (str): Terminal de départ
            destination (str): Terminal d'arrivée
            legs (list, optional): Liste des legs [(terminal_from, terminal_to, duration)]
            start_time (int, optional): Temps de début du service (en demi-journées)
            end_time (int, optional): Temps de fin du service (en demi-journées)
            vessel_types (dict, optional): Types et nombres de barges {type: count}
            capacity (int, optional): Capacité totale en TEUs
            frequency (int, optional): Fréquence du service (pour la compatibilité avec les scénarios)
            duration (int, optional): Durée totale du service (pour la compatibilité avec les scénarios)
        """
        self.service_id = service_id
        self.origin = origin
        self.destination = destination
        self.legs = legs if legs is not None else []
        self.start_time = start_time
        self.end_time = end_time
        self.vessel_types = vessel_types if vessel_types is not None else {}
        self.capacity = capacity
        self.frequency = frequency
        self.duration = duration
        self.status = "Ouvert"  # Ouvert ou Fermé
        
        # Calculer la route à partir des legs
        self.route = [self.origin]
        for leg in self.legs:
            if leg[1] not in self.route:
                self.route.append(leg[1])
        
        # Calculer les temps de passage à chaque terminal
        self.schedule = self._compute_schedule()
        
        # État actuel du service
        self.current_load = 0
        self.assigned_demands = []
        
    def _compute_schedule(self):
        """
        Calcule l'horaire détaillé du service.
        
        Returns:
            dict: {terminal: {'arrival': time, 'departure': time}}
        """
        schedule = {}
        current_time = self.start_time
        
        # Ajouter le terminal de départ
        schedule[self.origin] = {
            'arrival': current_time,
            'departure': current_time
        }
        
        # Calculer les temps pour chaque leg
        for leg in self.legs:
            from_terminal, to_terminal, duration = leg
            
            # Mise à jour du temps de départ du terminal précédent
            if from_terminal in schedule:
                schedule[from_terminal]['departure'] = current_time
            
            # Ajouter le temps de trajet
            current_time += duration
            
            # Ajouter le terminal d'arrivée
            schedule[to_terminal] = {
                'arrival': current_time,
                'departure': current_time
            }
        
        return schedule
    
    def can_serve_demand(self, demand):
        """
        Vérifie si le service peut satisfaire une demande.
        
        Args:
            demand (Demand): La demande à vérifier
            
        Returns:
            bool: True si le service peut satisfaire la demande
        """
        # Vérifier si le service est ouvert
        if self.status == "Fermé":
            return False
            
        # Vérifier la capacité disponible
        if self.current_load + demand.volume > self.capacity:
            return False
            
        # Vérifier la compatibilité temporelle
        if demand.origin not in self.schedule or demand.destination not in self.schedule:
            return False
            
        origin_schedule = self.schedule[demand.origin]
        dest_schedule = self.schedule[demand.destination]
        
        # Vérifier les contraintes temporelles
        if hasattr(demand, 'earliest_departure') and hasattr(demand, 'latest_arrival'):
            if (origin_schedule['departure'] < demand.earliest_departure or 
                dest_schedule['arrival'] > demand.latest_arrival):
                return False
        elif hasattr(demand, 'availability_time') and hasattr(demand, 'due_date'):
            if (origin_schedule['departure'] < demand.availability_time or 
                dest_schedule['arrival'] > demand.due_date):
                return False
            
        return True
    
    def assign_demand(self, demand):
        """
        Assigne une demande au service.
        
        Args:
            demand (Demand): La demande à assigner
            
        Returns:
            bool: True si l'assignation est réussie
        """
        if not self.can_serve_demand(demand):
            return False
            
        self.current_load += demand.volume
        self.assigned_demands.append(demand)
        return True
        
    def get_arrival_time_at(self, terminal):
        """
        Retourne l'heure d'arrivée à un terminal.
        
        Args:
            terminal (str): Terminal cible
            
        Returns:
            int: Heure d'arrivée au terminal, ou None si non trouvé
        """
        if terminal in self.schedule:
            return self.schedule[terminal]['arrival']
        return None
