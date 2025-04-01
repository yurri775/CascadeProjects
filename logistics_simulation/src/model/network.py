from typing import Dict, List, Set, Tuple, Optional
from .service import Service

class Network:
    def __init__(self, cycle_length: int = 14):  # Default cycle of 14 half-days (1 week)
        self.terminals: Set[str] = set()
        self.services: Dict[int, Service] = {}  # service_id -> Service
        self.cycle_length = cycle_length
        self.terminal_capacities: Dict[str, int] = {}  # terminal -> max TEUs
        
    def add_terminal(self, terminal_id: str, capacity: int = float('inf')) -> None:
        """Add a terminal to the network with optional capacity."""
        self.terminals.add(terminal_id)
        self.terminal_capacities[terminal_id] = capacity

    def add_service(self, service: Service) -> None:
        """Add a service to the network."""
        self.services[service.service_id] = service
        # Add terminals if they don't exist
        self.terminals.add(service.origin)
        self.terminals.add(service.destination)
        for leg in service.legs:
            self.terminals.add(leg.origin)
            self.terminals.add(leg.destination)

    def get_direct_services(self, origin: str, destination: str) -> List[Service]:
        """Get all direct services between origin and destination."""
        direct_services = []
        for service in self.services.values():
            if service.is_feasible_for_demand(origin, destination, 0, self.cycle_length):
                direct_services.append(service)
        return direct_services

    def find_route(self, origin: str, destination: str, start_time: int, 
                  end_time: int, demand_teus: int) -> List[Tuple[Service, int, int]]:
        """
        Find a feasible route from origin to destination within time constraints.
        Returns list of (service, boarding_time, alighting_time) tuples.
        """
        # First try direct services
        direct_services = self.get_direct_services(origin, destination)
        for service in direct_services:
            if service.has_capacity(demand_teus):
                # Find exact boarding and alighting times from service schedule
                for i, (terminal, time) in enumerate(service.stops):
                    if terminal == origin:
                        boarding_time = time
                        # Find corresponding alighting time
                        for j in range(i + 1, len(service.stops)):
                            if service.stops[j][0] == destination:
                                alighting_time = service.stops[j][1]
                                if start_time <= boarding_time and alighting_time <= end_time:
                                    return [(service, boarding_time, alighting_time)]

        # If no direct service, try routes with one intermediate stop
        for intermediate in self.terminals:
            if intermediate != origin and intermediate != destination:
                # Find services to intermediate
                first_leg = self.get_direct_services(origin, intermediate)
                # Find services from intermediate
                second_leg = self.get_direct_services(intermediate, destination)
                
                for s1 in first_leg:
                    if not s1.has_capacity(demand_teus):
                        continue
                    for s2 in second_leg:
                        if not s2.has_capacity(demand_teus):
                            continue
                            
                        # Find connection times
                        s1_arrival = None
                        s2_departure = None
                        
                        for terminal, time in s1.stops:
                            if terminal == intermediate:
                                s1_arrival = time
                                break
                                
                        for terminal, time in s2.stops:
                            if terminal == intermediate:
                                s2_departure = time
                                if s1_arrival is not None and s2_departure > s1_arrival:
                                    # Found a valid connection
                                    s1_boarding = None
                                    s2_alighting = None
                                    
                                    # Find boarding time for first service
                                    for terminal, time in s1.stops:
                                        if terminal == origin:
                                            s1_boarding = time
                                            break
                                            
                                    # Find alighting time for second service
                                    for terminal, time in s2.stops:
                                        if terminal == destination:
                                            s2_alighting = time
                                            break
                                            
                                    if (s1_boarding is not None and s2_alighting is not None and
                                        start_time <= s1_boarding and s2_alighting <= end_time):
                                        return [
                                            (s1, s1_boarding, s1_arrival),
                                            (s2, s2_departure, s2_alighting)
                                        ]
        
        return []  # No feasible route found

    def get_terminal_load(self, terminal: str, time: int) -> int:
        """Get current TEU load at a terminal."""
        load = 0
        for service in self.services.values():
            if service.get_current_position(time) == terminal:
                load += service.current_load
        return load

    def is_terminal_capacity_respected(self, terminal: str, time: int) -> bool:
        """Check if terminal capacity is respected."""
        return self.get_terminal_load(terminal, time) <= self.terminal_capacities[terminal]
