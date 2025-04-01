import heapq
from simulation.event import Event, EventType
from model.demand import DemandManager
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class SimulationConfig:
    MAX_TIME: int = 100
    STEP_SIZE: float = 0.5  # Demi-journée

class EventScheduler:
    def __init__(self):
        self.event_queue = []

    def add_event(self, event):
        heapq.heappush(self.event_queue, event)

    def get_next_event(self):
        if not self.event_queue:
            return None
        return heapq.heappop(self.event_queue)

class BargeSimulator:
    """
    Simulator for the barge transportation system using discrete event simulation.
    """
    def __init__(self, network=None, routing_manager=None, config: SimulationConfig = None):
        """
        Initialize the simulator.
        
        Args:
            network (SpaceTimeNetwork): The space-time network
            routing_manager (RoutingManager): The routing manager
            config (SimulationConfig, optional): Configuration for the simulation
        """
        self.config = config or SimulationConfig()
        self.network = network
        self.routing_manager = routing_manager
        self.barges = {}  # Dictionary of barge_id -> Barge
        self.services = {}  # Dictionary of service_id -> Service
        self.current_time = 0
        self.max_time = self.config.MAX_TIME  # Maximum simulation time
        self.scheduler = EventScheduler()
        self.statistics = {
            'terminal_utilization': {},  # Terminal ID -> utilization percentage
            'service_utilization': {},   # Service ID -> utilization percentage
            'barge_statistics': {},      # Barge ID -> statistics
            'demand_statistics': {}      # Demand statistics
        }
        self.demand_manager = DemandManager()
        self.events = []

    def add_barge(self, barge):
        """
        Add a barge to the simulation.
        
        Args:
            barge (Barge): The barge to add
        """
        self.barges[barge.barge_id] = barge
        
        # If barge has a service, schedule initial departure
        if barge.service_id and barge.service_id in self.services:
            service = self.services[barge.service_id]
            if barge.position in service.route:
                # Find next node in the service route
                current_idx = service.route.index(barge.position)
                if current_idx < len(service.route) - 1:
                    next_node = service.route[current_idx + 1]
                    # Schedule departure
                    self._schedule_departure(barge, next_node, self.current_time)
        
    def add_service(self, service):
        """
        Add a service to the simulation.
        
        Args:
            service (Service): The service to add
        """
        self.services[service.service_id] = service
        
    def add_event(self, time, event_type, data=None):
        """
        Add an event to the event queue.
        
        Args:
            time (float): Time when the event occurs
            event_type (str): Type of event
            data (dict, optional): Additional data for the event
        """
        event = Event(time, event_type, data)
        self.scheduler.add_event(event)
        return event
        
    def run(self):
        print(f"Démarrage de la simulation: {datetime.now()}")
        while self.current_time < self.config.MAX_TIME:
            if not self.process_next_event():
                break
        print(f"Fin de la simulation: {datetime.now()}")

    def process_next_event(self):
        """Process the next event in the queue."""
        event = self.scheduler.get_next_event()
        if not event:
            print("Plus d'événements à traiter")
            return False
            
        print(f"\nt={event.time}: {event.event_type}")
        self._process_event(event)
        self._update_statistics()
        return True
        
    def _process_event(self, event):
        """Traite un événement selon son type."""
        handlers = {
            EventType.BARGE_ARRIVAL: self._handle_barge_arrival,
            EventType.BARGE_DEPARTURE: self._handle_barge_departure,
            EventType.LOADING_START: self._handle_loading_start,
            EventType.LOADING_END: self._handle_loading_end,
            EventType.DEMAND_ARRIVAL: self._handle_demand_arrival,
            EventType.SIMULATION_END: self._handle_simulation_end
        }
        
        handler = handlers.get(event.type)
        if handler:
            handler(event)
        else:
            print(f"Type d'événement inconnu: {event.type}")
            
    def _handle_barge_arrival(self, event):
        """
        Handle a barge arrival event.
        
        Args:
            event (Event): The arrival event
        """
        barge_id = event.data.get('barge_id')
        terminal_id = event.data.get('terminal_id')
        
        if barge_id not in self.barges:
            print(f"Error: Barge {barge_id} not found")
            return
            
        barge = self.barges[barge_id]
        
        # Update barge position
        barge.move_to(terminal_id, self.current_time)
        
        # Check if there are demands to load/unload
        demands_to_load = self.demand_manager.get_demands_for_loading(terminal_id, barge_id)
        demands_to_unload = self.demand_manager.get_demands_for_unloading(terminal_id, barge_id)
        
        # Handle loading/unloading
        if demands_to_load or demands_to_unload:
            # Start terminal operations
            if demands_to_unload:
                # Unload first
                barge.status = "unloading"
                # Schedule unloading completion (1 time unit)
                self.add_event(
                    self.current_time + 1, 
                    EventType.UNLOADING_COMPLETE, 
                    {'barge_id': barge_id, 'terminal_id': terminal_id, 'demands': demands_to_unload}
                )
            elif demands_to_load:
                # Then load
                barge.status = "loading"
                # Schedule loading completion (1 time unit)
                self.add_event(
                    self.current_time + 1, 
                    EventType.LOADING_COMPLETE, 
                    {'barge_id': barge_id, 'terminal_id': terminal_id, 'demands': demands_to_load}
                )
        else:
            # No operations, schedule departure based on service
            self._schedule_next_departure(barge, terminal_id)
            
    def _handle_barge_departure(self, event):
        """
        Handle a barge departure event.
        
        Args:
            event (Event): The departure event
        """
        barge_id = event.data.get('barge_id')
        from_terminal = event.data.get('from_terminal')
        to_terminal = event.data.get('to_terminal')
        
        if barge_id not in self.barges:
            print(f"Error: Barge {barge_id} not found")
            return
            
        barge = self.barges[barge_id]
        
        # Update barge status
        barge.status = "in_transit"
        
        # Calculate travel time
        travel_time = self.network.get_travel_time(from_terminal, to_terminal)
        
        if travel_time is None:
            print(f"Error: No route found from {from_terminal} to {to_terminal}")
            return
        
        # Schedule arrival at destination
        self.add_event(
            self.current_time + travel_time, 
            EventType.BARGE_ARRIVAL, 
            {'barge_id': barge_id, 'terminal_id': to_terminal}
        )
        
    def _handle_loading_complete(self, event):
        """
        Handle a loading complete event.
        
        Args:
            event (Event): The loading complete event
        """
        barge_id = event.data.get('barge_id')
        terminal_id = event.data.get('terminal_id')
        demands = event.data.get('demands', [])
        
        if barge_id not in self.barges:
            print(f"Error: Barge {barge_id} not found")
            return
            
        barge = self.barges[barge_id]
        
        # Update barge and demands
        for demand in demands:
            # Load cargo onto barge
            loaded = barge.load_cargo(demand.volume)
            if loaded:
                # Update demand status
                demand.status = "in_transit"
                demand.assigned_barge = barge_id
                print(f"Loaded demand {demand.demand_id} onto barge {barge_id} at terminal {terminal_id}")
            else:
                print(f"Failed to load demand {demand.demand_id}: Insufficient capacity")
        
        # Schedule departure
        self._schedule_next_departure(barge, terminal_id)
        
    def _handle_unloading_complete(self, event):
        """
        Handle an unloading complete event.
        
        Args:
            event (Event): The unloading complete event
        """
        barge_id = event.data.get('barge_id')
        terminal_id = event.data.get('terminal_id')
        demands = event.data.get('demands', [])
        
        if barge_id not in self.barges:
            print(f"Error: Barge {barge_id} not found")
            return
            
        barge = self.barges[barge_id]
        
        # Update barge and demands
        for demand in demands:
            # Unload cargo from barge
            unloaded = barge.unload_cargo(demand.quantity)
            if unloaded:
                # Update demand status
                demand.status = "completed"
                demand.completion_time = self.current_time
                print(f"Unloaded demand {demand.demand_id} from barge {barge_id} at terminal {terminal_id}")
            else:
                print(f"Failed to unload demand {demand.demand_id}")
        
        # Check if there are demands to load
        demands_to_load = self.demand_manager.get_demands_for_loading(terminal_id, barge_id)
        
        if demands_to_load:
            # Start loading
            barge.status = "loading"
            # Schedule loading completion (1 time unit)
            self.add_event(
                self.current_time + 1, 
                EventType.LOADING_COMPLETE, 
                {'barge_id': barge_id, 'terminal_id': terminal_id, 'demands': demands_to_load}
            )
        else:
            # No more operations, schedule departure
            self._schedule_next_departure(barge, terminal_id)
            
    def _handle_demand_arrival(self, event):
        """
        Handle a demand arrival event.
        
        Args:
            event (Event): The demand arrival event
        """
        demand = event.data.get('demand')
        
        if demand:
            # Add demand to the manager
            self.demand_manager.add_demand(demand)
            print(f"Demand {demand.demand_id} arrived at time {self.current_time}")
            
            # Check if there are barges at the origin terminal that can handle this demand
            for barge_id, barge in self.barges.items():
                if barge.position == demand.origin and barge.status == "idle":
                    # Barge is available at the origin, schedule loading
                    self.add_event(
                        self.current_time, 
                        EventType.LOADING_COMPLETE, 
                        {'barge_id': barge_id, 'terminal_id': demand.origin, 'demands': [demand]}
                    )
                    break
        
    def process_demand(self, demand, time):
        """
        Process a demand by finding an available barge and assigning it.
        
        Args:
            demand (Demand): Demand to process
            time (float): Current simulation time
        """
        # Find available barge
        for barge in self.barges.values():
            if barge.status == "idle" and barge.current_load + demand.volume <= barge.capacity:
                # Assign demand to barge
                barge.assigned_demands.append(demand)
                barge.current_load += demand.volume
                barge.status = "loading"
                demand.status = "in_progress"
                
                # Update statistics
                self.statistics['demand_statistics'][demand.demand_id] = {
                    'status': demand.status,
                    'assigned_barge': barge.barge_id
                }
                return True
        return False
        
    def _schedule_next_departure(self, barge, current_terminal):
        """
        Schedule the next departure for a barge based on its service.
        
        Args:
            barge (Barge): The barge
            current_terminal (str): Current terminal ID
        """
        if barge.service_id and barge.service_id in self.services:
            service = self.services[barge.service_id]
            
            # Find the next terminal in the service route
            if current_terminal in service.route:
                current_idx = service.route.index(current_terminal)
                if current_idx < len(service.route) - 1:
                    next_terminal = service.route[current_idx + 1]
                    # Schedule departure
                    self._schedule_departure(barge, next_terminal, self.current_time)
                else:
                    # End of route, barge becomes idle
                    barge.status = "idle"
                    print(f"Barge {barge.barge_id} reached end of service route at {current_terminal}")
            else:
                print(f"Terminal {current_terminal} not in service route for barge {barge.barge_id}")
        else:
            # No service assigned, barge becomes idle
            barge.status = "idle"
            
    def _schedule_departure(self, barge, to_terminal, time):
        """
        Schedule a departure event for a barge.
        
        Args:
            barge (Barge): The barge
            to_terminal (str): Destination terminal ID
            time (float): Current time
        """
        # Schedule departure immediately
        self.add_event(
            time, 
            EventType.BARGE_DEPARTURE, 
            {'barge_id': barge.barge_id, 'from_terminal': barge.position, 'to_terminal': to_terminal}
        )
        
    def _update_statistics(self):
        """Update simulation statistics."""
        # Terminal utilization
        for node_id, node in self.network.nodes.items():
            if node['type'] == 'port':
                # Calculate terminal utilization
                # This is a placeholder - actual calculation would depend on terminal usage data
                self.statistics['terminal_utilization'][node_id] = 0.0
        
        # Service utilization
        for service_id, service in self.services.items():
            # Calculate service utilization
            # This is a placeholder - actual calculation would depend on service usage data
            self.statistics['service_utilization'][service_id] = 0.0
        
        # Barge statistics
        for barge_id, barge in self.barges.items():
            # Collect barge statistics
            self.statistics['barge_statistics'][barge_id] = {
                'current_position': barge.position,
                'current_load': barge.current_load,
                'status': barge.status
            }
        
        # Demand statistics
        self.statistics['demand_statistics'] = self.demand_manager.get_statistics()
        
    def _collect_statistics(self):
        """Met à jour les statistiques de simulation."""
        # Utilisation des terminaux
        for terminal_id in self.network.terminals:
            usage = self._calculate_terminal_usage(terminal_id)
            self.statistics['terminal_utilization'][terminal_id] = usage

        # Utilisation des services
        for service_id, service in self.services.items():
            usage = self._calculate_service_usage(service)
            self.statistics['service_utilization'][service_id] = usage

        # Statistiques des barges
        for barge_id, barge in self.barges.items():
            self.statistics['barge_statistics'][barge_id] = {
                'distance_traveled': barge.total_distance,
                'cargo_handled': barge.total_cargo_handled,
                'utilization_rate': barge.calculate_utilization()
            }

    def get_statistics(self):
        """
        Get simulation statistics.
        
        Returns:
            dict: Simulation statistics
        """
        # Update statistics
        self._update_statistics()
        
        # Return combined statistics
        return {
            'current_time': self.current_time,
            'terminal_utilization': self.statistics['terminal_utilization'],
            'service_utilization': self.statistics['service_utilization'],
            'barge_stats': self.statistics['barge_statistics'],
            'demand_stats': self.statistics['demand_statistics']
        }
