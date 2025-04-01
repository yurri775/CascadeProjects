"""
Module d'optimisation des assignations de demandes aux services.
"""

class AssignmentOptimizer:
    """
    Optimise l'assignation des demandes aux services en tenant compte des contraintes
    de capacité et des priorités.
    """
    
    def __init__(self):
        self.assigned_demands = {}  # service_id -> liste de demandes
        self.service_loads = {}     # service_id -> charge actuelle
        
    def optimize_assignments(self, demands, services, network):
        """
        Optimise l'assignation des demandes aux services.
        
        Args:
            demands (list): Liste des demandes
            services (list): Liste des services
            network (Network): Réseau de transport
            
        Returns:
            dict: Dictionnaire {demand_id: service_id}
        """
        # Réinitialiser l'état
        self.service_loads = {}
        self.assigned_demands = {}
        assignments = {}
        
        # Trier les demandes par priorité
        sorted_demands = sorted(demands, 
                              key=lambda d: (
                                  # 1. Type de client (R > F > P)
                                  {'R': 0, 'F': 1, 'P': 2}[d.customer_type],
                                  # 2. Classe tarifaire (E > S)
                                  {'E': 0, 'S': 1}[d.fare_class],
                                  # 3. Volume (plus grand d'abord)
                                  -d.volume
                              ))
        
        # Assigner les demandes
        for demand in sorted_demands:
            # Trouver les services possibles
            feasible_services = network.get_feasible_services(demand)
            
            # Trouver le meilleur service
            best_service = self._find_best_service(demand, feasible_services, services)
            
            if best_service:
                # Assigner la demande au service
                self._assign_demand(demand, best_service)
                assignments[demand.demand_id] = best_service.service_id
        
        return assignments
    
    def _find_best_service(self, demand, feasible_services, services):
        """
        Trouve le meilleur service pour une demande.
        
        Critères:
        1. Capacité suffisante
        2. Temps d'arrivée au plus tôt
        3. Utilisation optimale de la capacité
        4. Minimisation des escales
        5. Flexibilité temporelle
        """
        best_service = None
        best_score = float('inf')
        
        # Vérifier d'abord les services qui peuvent servir la demande
        compatible_services = [s for s in services if s.can_serve_demand(demand)]
        
        for service in compatible_services:
            # Vérifier la capacité
            current_load = self.service_loads.get(service.service_id, 0)
            if current_load + demand.volume > service.capacity:
                continue
            
            # Calculer le score (plus petit = meilleur)
            score = (
                # 1. Priorité au temps d'arrivée
                service.arrival_time * 10 +
                
                # 2. Minimiser la capacité inutilisée
                (service.capacity - current_load - demand.volume) / service.capacity * 5 +
                
                # 3. Pénalité pour les escales
                len(service.route) * 3 +
                
                # 4. Bonus pour les services express
                (0 if demand.fare_class == 'E' and len(service.route) <= 3 else 5) +
                
                # 5. Pénalité pour les détours
                abs(service.arrival_time - demand.due_date)
            )
            
            if score < best_score:
                best_score = score
                best_service = service
        
        return best_service
    
    def _find_service_by_time(self, services, departure_time, arrival_time):
        """Trouve un service correspondant aux horaires donnés."""
        for service in services:
            if (service.departure_time == departure_time and
                service.arrival_time == arrival_time):
                return service
        return None
    
    def _assign_demand(self, demand, service):
        """Assigner une demande à un service."""
        current_load = self.service_loads.get(service.service_id, 0)
        self.service_loads[service.service_id] = current_load + demand.volume
        
        if service.service_id not in self.assigned_demands:
            self.assigned_demands[service.service_id] = []
        self.assigned_demands[service.service_id].append(demand)
    
    def get_service_utilization(self, services):
        """
        Calcule l'utilisation des services.
        
        Returns:
            dict: Dictionnaire {service_id: pourcentage_utilisation}
        """
        utilization = {}
        for service in services:
            load = self.service_loads.get(service.service_id, 0)
            utilization[service.service_id] = (load / service.capacity) * 100
        return utilization
