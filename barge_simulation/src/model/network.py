import networkx as nx
from datetime import datetime, timedelta

class SpaceTimeNetwork:
    """
    Represents a space-time network for barge transportation.
    """
    def __init__(self):
        """
        Initialize an empty space-time network.
        """
        self.network = nx.DiGraph()
        self.nodes = {}  # Dictionary of node_id -> node_data
        self.edges = {}  # Dictionary of (from_node, to_node) -> edge_data
        self.resources = {}  # Dictionary to store resource availability
        self.terminals = {}  # Dictionary of terminal_id -> terminal_data
        self.connections = {}  # Dictionary of origin -> {destination -> edge_data}
        
    def add_node(self, node_id, position, node_type, capacity=None):
        """
        Add a node to the network.
        
        Args:
            node_id (str): Unique identifier for the node
            position (tuple): (x, y) coordinates of the node
            node_type (str): Type of node (port, intersection)
            capacity (int, optional): Capacity of the node (for ports)
        """
        self.nodes[node_id] = {
            'position': position,
            'type': node_type,
            'capacity': capacity if capacity is not None else float('inf')
        }
        self.network.add_node(node_id, **self.nodes[node_id])
        
    def add_terminal(self, terminal_id, position=(0, 0), terminal_type="terminal", capacity=float('inf')):
        """
        Add a terminal to the network.
        
        Args:
            terminal_id (str): Unique identifier for the terminal
            position (tuple): (x, y) coordinates of the terminal
            terminal_type (str): Type of terminal
            capacity (int, optional): Capacity of the terminal
        """
        self.terminals[terminal_id] = {
            'position': position,
            'type': terminal_type,
            'capacity': capacity
        }
        # Also add it as a node
        self.add_node(terminal_id, position, terminal_type, capacity)
        
    def add_edge(self, from_node, to_node, travel_time, capacity=None):
        """
        Add an edge to the network.
        
        Args:
            from_node (str): Origin node ID
            to_node (str): Destination node ID
            travel_time (float): Travel time for this edge
            capacity (int, optional): Maximum number of barges that can use the edge simultaneously
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError(f"Nodes {from_node} and/or {to_node} not in network")
            
        edge_id = (from_node, to_node)
        self.edges[edge_id] = {
            'travel_time': travel_time,
            'capacity': capacity if capacity is not None else float('inf'),
            'current_load': 0
        }
        self.network.add_edge(from_node, to_node, **self.edges[edge_id])
        
    def add_connection(self, origin, destination, distance, travel_time, capacity=None):
        """
        Add a connection between two terminals.
        
        Args:
            origin (str): Origin terminal ID
            destination (str): Destination terminal ID
            distance (float): Distance between terminals
            travel_time (float): Travel time between terminals
            capacity (int, optional): Maximum number of barges that can use the connection simultaneously
        """
        # Add the edge
        self.add_edge(origin, destination, travel_time, capacity)
        
        # Add to connections dictionary
        if origin not in self.connections:
            self.connections[origin] = {}
        self.connections[origin][destination] = {
            'distance': distance,
            'travel_time': travel_time,
            'capacity': capacity if capacity is not None else float('inf')
        }
        
    def get_travel_time(self, from_node, to_node):
        """
        Get the travel time between two nodes.
        
        Args:
            from_node (str): Origin node ID
            to_node (str): Destination node ID
            
        Returns:
            float: Travel time for this edge, or None if the edge doesn't exist
        """
        edge_id = (from_node, to_node)
        if edge_id in self.edges:
            return self.edges[edge_id]['travel_time']
        return None
        
    def get_distance(self, from_node, to_node):
        """
        Get the distance between two nodes.
        For simplicity, we'll use travel time as a proxy for distance.
        
        Args:
            from_node (str): Origin node ID
            to_node (str): Destination node ID
            
        Returns:
            float: Distance for this edge, or 0 if the edge doesn't exist
        """
        travel_time = self.get_travel_time(from_node, to_node)
        if travel_time is not None:
            return travel_time  # Using travel time as a proxy for distance
        return 0
        
    def has_edge(self, from_node, to_node):
        """
        Check if an edge exists between two nodes.
        
        Args:
            from_node (str): Origin node ID
            to_node (str): Destination node ID
            
        Returns:
            bool: True if edge exists, False otherwise
        """
        return (from_node, to_node) in self.edges
        
    def get_node_capacity(self, node_id):
        """
        Get the capacity of a node.
        
        Args:
            node_id (str): Node ID
            
        Returns:
            int: Capacity, or None if node doesn't exist or has no capacity
        """
        if node_id in self.nodes:
            return self.nodes[node_id].get('capacity')
        return None
        
    def check_capacity(self, node_id, current_occupancy):
        """
        Check if a node has available capacity.
        
        Args:
            node_id (str): Node ID
            current_occupancy (int): Current number of barges at the node
            
        Returns:
            bool: True if capacity is available, False otherwise
        """
        capacity = self.get_node_capacity(node_id)
        
        # If no capacity is defined, assume unlimited
        if capacity is None:
            return True
            
        return current_occupancy < capacity
        
    def check_capacity_at_time(self, node_id, time):
        """
        Check if a node has available capacity at a given time.
        
        Args:
            node_id (str): Node ID to check
            time (datetime): Time to check
            
        Returns:
            bool: True if capacity is available, False otherwise
        """
        if node_id not in self.resources:
            self.resources[node_id] = {}
            
        current_load = self.resources[node_id].get(time, 0)
        max_capacity = self.nodes[node_id]['capacity']
        return current_load < max_capacity
        
    def reserve_capacity(self, node_id, time, amount=1):
        """
        Reserve capacity at a node for a given time.
        
        Args:
            node_id (str): Node ID to reserve
            time (datetime): Time of reservation
            amount (int): Amount of capacity to reserve
            
        Returns:
            bool: True if reservation successful, False otherwise
        """
        if not self.check_capacity_at_time(node_id, time):
            return False
            
        if node_id not in self.resources:
            self.resources[node_id] = {}
        
        current = self.resources[node_id].get(time, 0)
        self.resources[node_id][time] = current + amount
        return True
        
    def get_shortest_path(self, start_node, end_node, departure_time):
        """
        Calculate the shortest path considering time windows.
        
        Args:
            start_node (str): Starting node ID
            end_node (str): Ending node ID
            departure_time (datetime): Departure time
            
        Returns:
            list: List of nodes representing the shortest path
        """
        return nx.shortest_path(self.network, start_node, end_node, weight='travel_time')


class Network:
    """
    Gère le réseau physique et le réseau temps-espace du système de transport fluvial.
    """
    
    def __init__(self, cycle_length=14):
        """
        Initialise le réseau.
        
        Args:
            cycle_length (int): Longueur du cycle en demi-journées (défaut: 14 pour une semaine)
        """
        self.cycle_length = cycle_length
        self.terminals = {}  # {id: {'type': str, 'capacity': int}}
        self.services = {}  # {id: Service}
        self.routes = {}  # {(origin, dest): [routes]}
        self.space_time_graph = {}  # {(terminal, time): [(next_terminal, next_time, service_id)]}
        
    def add_terminal(self, terminal_id, terminal_type="terminal", capacity=float('inf')):
        """
        Ajoute un terminal au réseau.
        
        Args:
            terminal_id (str): Identifiant du terminal
            terminal_type (str): Type de terminal
            capacity (int): Capacité en TEUs
        """
        self.terminals[terminal_id] = {
            'type': terminal_type,
            'capacity': capacity,
            'current_load': 0
        }
        
    def add_arc(self, origin, destination, distance, travel_time):
        """
        Ajoute un arc au réseau physique.
        
        Args:
            origin (str): Terminal d'origine
            destination (str): Terminal de destination
            distance (float): Distance entre les terminaux
            travel_time (float): Temps de trajet entre les terminaux
        """
        # Vérifier que les terminaux existent
        if origin not in self.terminals:
            self.add_terminal(origin)
        if destination not in self.terminals:
            self.add_terminal(destination)
        
        # Ajouter l'arc au réseau
        if not hasattr(self, 'arcs'):
            self.arcs = {}
        
        self.arcs[(origin, destination)] = {
            'distance': distance,
            'travel_time': travel_time
        }
        
    def add_service(self, service):
        """
        Ajoute un service au réseau.
        
        Args:
            service (Service): Service à ajouter
        """
        self.services[service.service_id] = service
        self._update_space_time_graph(service)
        
    def get_travel_time(self, from_node, to_node):
        """
        Récupère le temps de trajet entre deux terminaux.
        
        Args:
            from_node (str): Terminal d'origine
            to_node (str): Terminal de destination
            
        Returns:
            float: Temps de trajet, ou None si l'arc n'existe pas
        """
        if hasattr(self, 'arcs') and (from_node, to_node) in self.arcs:
            return self.arcs[(from_node, to_node)]['travel_time']
        return None
        
    def get_distance(self, from_node, to_node):
        """
        Récupère la distance entre deux terminaux.
        
        Args:
            from_node (str): Terminal d'origine
            to_node (str): Terminal de destination
            
        Returns:
            float: Distance, ou 0 si l'arc n'existe pas
        """
        if hasattr(self, 'arcs') and (from_node, to_node) in self.arcs:
            return self.arcs[(from_node, to_node)]['distance']
        return 0
        
    def _update_space_time_graph(self, service):
        """
        Met à jour le graphe temps-espace avec un nouveau service.
        
        Args:
            service (Service): Service à ajouter au graphe
        """
        # Ajouter les arcs pour chaque leg du service
        for leg in service.legs:
            from_terminal, to_terminal, duration = leg
            departure_time = service.schedule[from_terminal]['departure']
            arrival_time = service.schedule[to_terminal]['arrival']
            
            # Créer le nœud de départ s'il n'existe pas
            if (from_terminal, departure_time) not in self.space_time_graph:
                self.space_time_graph[(from_terminal, departure_time)] = []
                
            # Ajouter l'arc
            self.space_time_graph[(from_terminal, departure_time)].append(
                (to_terminal, arrival_time, service.service_id)
            )
            
            # Ajouter les arcs d'attente si nécessaire
            for t in range(departure_time - 1, -1, -1):
                if (from_terminal, t) not in self.space_time_graph:
                    self.space_time_graph[(from_terminal, t)] = []
                self.space_time_graph[(from_terminal, t)].append(
                    (from_terminal, t + 1, None)  # None indique un arc d'attente
                )
                
    def get_feasible_services(self, demand):
        """
        Trouve les services possibles pour une demande.
        
        Args:
            demand (Demand): Demande à satisfaire
            
        Returns:
            list: Liste des services possibles
        """
        feasible_services = []
        
        for service in self.services.values():
            if service.can_serve_demand(demand):
                feasible_services.append(service)
                
        return feasible_services
        
    def get_route(self, origin, destination, earliest_departure, latest_arrival):
        """
        Trouve un itinéraire possible entre deux terminaux.
        
        Args:
            origin (str): Terminal de départ
            destination (str): Terminal d'arrivée
            earliest_departure (int): Temps de départ au plus tôt
            latest_arrival (int): Temps d'arrivée au plus tard
            
        Returns:
            list: Liste de tuples (terminal, temps, service_id) ou None si pas de route
        """
        # File pour le parcours en largeur
        queue = [(origin, earliest_departure, [])]
        visited = set()
        
        while queue:
            current_terminal, current_time, path = queue.pop(0)
            
            # Si on est arrivé à destination dans les temps
            if current_terminal == destination and current_time <= latest_arrival:
                return path
                
            # Explorer les voisins
            current_node = (current_terminal, current_time)
            if current_node in self.space_time_graph:
                for next_terminal, next_time, service_id in self.space_time_graph[current_node]:
                    next_node = (next_terminal, next_time)
                    if next_node not in visited and next_time <= latest_arrival:
                        visited.add(next_node)
                        new_path = path + [(current_terminal, current_time, service_id)]
                        queue.append((next_terminal, next_time, new_path))
                        
        return None  # Pas de route trouvée
        
    def get_all_routes(self, origin, destination):
        """
        Trouve tous les itinéraires possibles entre deux terminaux.
        
        Args:
            origin (str): Terminal de départ
            destination (str): Terminal d'arrivée
            
        Returns:
            list: Liste des itinéraires possibles
        """
        if (origin, destination) in self.routes:
            return self.routes[(origin, destination)]
            
        routes = []
        for service in self.services.values():
            if service.origin == origin and service.destination == destination:
                routes.append([service])
                continue
                
            # Chercher les routes avec une escale
            for intermediate_service in self.services.values():
                if (service.origin == origin and 
                    service.destination == intermediate_service.origin and
                    intermediate_service.destination == destination):
                    routes.append([service, intermediate_service])
                    
        self.routes[(origin, destination)] = routes
        return routes
