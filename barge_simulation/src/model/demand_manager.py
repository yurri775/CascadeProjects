# src/model/demand_manager.py

class DemandManager:
    """Gère les demandes de transport"""
    
    def __init__(self):
        self.demands = {}
        self.pending_demands = []
        self.completed_demands = []
        self.assigned_demands = []
    
    def add_demand(self, demand):
        """Ajoute une nouvelle demande"""
        self.demands[demand.demand_id] = demand
        self.pending_demands.append(demand.demand_id)
        return demand.demand_id
    
    def get_demand(self, demand_id):
        """Récupère une demande par son ID"""
        return self.demands.get(demand_id)
    
    def get_all_demands(self):
        """Récupère toutes les demandes"""
        return list(self.demands.values())
    
    def get_pending_demands(self):
        """Récupère les demandes en attente"""
        return [self.demands[d_id] for d_id in self.pending_demands]
    
    def mark_as_assigned(self, demand_id, barge_id):
        """Marque une demande comme assignée à une barge"""
        if demand_id in self.pending_demands:
            self.pending_demands.remove(demand_id)
            self.assigned_demands.append(demand_id)
            self.demands[demand_id].assigned_barge = barge_id
            self.demands[demand_id].status = "assigned"
    
    def mark_as_completed(self, demand_id):
        """Marque une demande comme complétée"""
        if demand_id in self.assigned_demands:
            self.assigned_demands.remove(demand_id)
            self.completed_demands.append(demand_id)
            self.demands[demand_id].status = "completed"
    
    def get_demand_statistics(self):
        """Retourne les statistiques sur les demandes"""
        return {
            "total": len(self.demands),
            "pending": len(self.pending_demands),
            "assigned": len(self.assigned_demands),
            "completed": len(self.completed_demands),
            "failed": 0  
        }
    
    def get_demands_for_loading(self, terminal_id, barge_id=None):
        """
        Récupère les demandes à charger sur une barge à un terminal donné
        
        Args:
            terminal_id: Identifiant du terminal
            barge_id: Optionnel, identifiant de la barge concernée
        
        Returns:
            Liste des demandes à charger
        """
        loading_demands = []
        
        for demand_id, demand in self.demands.items():
            # Vérifier si la demande est en attente à ce terminal
            if demand.origin == terminal_id and demand.status == "pending":
                # Si une barge spécifique est précisée et que la demande est assignée à cette barge
                if barge_id is not None and demand.assigned_barge == barge_id:
                    loading_demands.append(demand)
                # Si aucune barge n'est précisée et que la demande n'est assignée à aucune barge
                elif barge_id is None and demand.assigned_barge is None:
                    loading_demands.append(demand)
        
        return loading_demands

    def get_demands_for_unloading(self, terminal_id, barge_id=None):
        """
        Récupère les demandes à décharger d'une barge à un terminal donné
        
        Args:
            terminal_id: Identifiant du terminal
            barge_id: Optionnel, identifiant de la barge concernée
        
        Returns:
            Liste des demandes à décharger
        """
        unloading_demands = []
        
        for demand_id, demand in self.demands.items():
            # Vérifier si la demande doit être déchargée à ce terminal
            if demand.destination == terminal_id and demand.status == "assigned":
                # Si une barge spécifique est précisée
                if barge_id is not None and demand.assigned_barge == barge_id:
                    unloading_demands.append(demand)
                # Si aucune barge n'est précisée
                elif barge_id is None:
                    unloading_demands.append(demand)
        
        return unloading_demands