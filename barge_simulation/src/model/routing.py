class RoutingManager:
    """
    Manages routing between terminals.
    """
    def __init__(self):
        """
        Initialize the routing manager.
        """
        self.services = {}  # Dictionary of service_id -> Service
        self.routing_matrix = {}  # Dictionary of (origin, destination) -> service_id
        
    def add_service(self, service):
        """
        Add a service to the routing manager.
        
        Args:
            service (Service): Service to add
        """
        self.services[service.service_id] = service
        self._update_routing_matrix(service)
        
    def _update_routing_matrix(self, service):
        """
        Update the routing matrix with a new service.
        
        Args:
            service (Service): Service to add to the routing matrix
        """
        route = service.route
        
        # For each pair of terminals in the route, add this service as an option
        for i in range(len(route)):
            for j in range(i + 1, len(route)):
                origin = route[i]
                destination = route[j]
                
                # Add forward direction
                self._add_to_routing_matrix(origin, destination, service.service_id)
                
        # Also add reverse connections if the service is bidirectional
        # Check if the service has the bidirectional attribute, default to False if not
        bidirectional = getattr(service, 'bidirectional', False)
        if bidirectional:
            for i in range(len(route) - 1, 0, -1):
                for j in range(i - 1, -1, -1):
                    origin = route[i]
                    destination = route[j]
                    
                    # Add reverse direction
                    self._add_to_routing_matrix(origin, destination, service.service_id)
                    
    def _add_to_routing_matrix(self, origin, destination, service_id):
        """
        Add a service to the routing matrix for a specific origin-destination pair.
        
        Args:
            origin (str): Origin terminal
            destination (str): Destination terminal
            service_id (str): Service ID
        """
        key = (origin, destination)
        
        if key not in self.routing_matrix:
            self.routing_matrix[key] = []
            
        if service_id not in self.routing_matrix[key]:
            self.routing_matrix[key].append(service_id)
            
    def get_service(self, origin, destination):
        """
        Get the best service for a specific origin-destination pair.
        
        Args:
            origin (str): Origin terminal
            destination (str): Destination terminal
            
        Returns:
            str: Service ID, or None if no service is available
        """
        key = (origin, destination)
        
        if key in self.routing_matrix and self.routing_matrix[key]:
            # For now, just return the first service
            # In a more advanced implementation, you could consider factors like:
            # - Service frequency
            # - Current utilization
            # - Travel time
            return self.routing_matrix[key][0]
            
        return None
        
    def get_all_services(self, origin, destination):
        """
        Get all services for a specific origin-destination pair.
        
        Args:
            origin (str): Origin terminal
            destination (str): Destination terminal
            
        Returns:
            list: List of service IDs, or empty list if no services are available
        """
        key = (origin, destination)
        
        if key in self.routing_matrix:
            return self.routing_matrix[key]
            
        return []
        
    def build_routing_matrix(self):
        """
        Build the routing matrix from scratch.
        """
        self.routing_matrix = {}
        
        for service in self.services.values():
            self._update_routing_matrix(service)
            
    def print_routing_matrix(self):
        """
        Print the routing matrix for debugging.
        """
        terminals = sorted(list(set([k[0] for k in self.routing_matrix.keys()] + [k[1] for k in self.routing_matrix.keys()])))
        
        # Print header
        print("O\\D", end="\t")
        for dest in terminals:
            print(dest, end="\t")
        print()
        
        # Print rows
        for origin in terminals:
            print(origin, end="\t")
            for dest in terminals:
                if origin == dest:
                    print("-", end="\t")
                elif (origin, dest) in self.routing_matrix:
                    print(self.routing_matrix[(origin, dest)][0], end="\t")
                else:
                    print("X", end="\t")
            print()

    def get_route(self, start, end, network):
        """Calcule la meilleure route entre deux points."""
        if not hasattr(network, 'get_distance'):
            return [start, end]  # Route directe par défaut
            
        route = []
        current = start
        
        while current != end:
            next_terminal = min(
                network.get_connected_terminals(current),
                key=lambda t: network.get_distance(t, end)
            )
            route.append(next_terminal)
            current = next_terminal
            
        return route

# Dans run_scenario.py
from src.model.network import Network

def load_network():
    """Charge le réseau de transport"""
    try:
        # Tentative de chargement à partir d'un fichier
        network = Network()
        # Configuration minimale pour garantir un réseau valide
        for i in range(4):
            network.add_terminal(f"{i}", (i*10, i*5))
        
        # Connexions entre terminaux
        for i in range(4):
            for j in range(4):
                if i != j:
                    network.add_connection(f"{i}", f"{j}")
        
        print(f"Réseau chargé: {len(network.terminals)} terminaux, {len(network.connections)} connexions")
        return network
    except Exception as e:
        print(f"Erreur lors du chargement du réseau: {e}")
        # En cas d'erreur, créer un réseau minimal par défaut
        default_network = Network()
        for i in range(4):
            default_network.add_terminal(str(i), (i*10, 0))
        for i in range(3):
            default_network.add_connection(str(i), str(i+1))
            default_network.add_connection(str(i+1), str(i))
        return default_network

# Dans la fonction principale
def main():
    # ...
    # Assurez-vous d'initialiser le réseau correctement
    network = load_network()
    if network is None:
        print("Erreur critique: Impossible de charger ou créer un réseau")
        return
    
    # Créer le simulateur seulement si le réseau est disponible
    simulator = BargeSimulator(network)
    # ...
