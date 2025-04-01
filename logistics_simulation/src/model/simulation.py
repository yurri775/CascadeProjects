from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from .network import Network
from .service import Service, BargeType
from .demand import Demand, DemandStatus
import heapq

class EventType(Enum):
    DEMAND_ARRIVAL = "demand_arrival"
    SERVICE_DEPARTURE = "service_departure"
    SERVICE_ARRIVAL = "service_arrival"
    DEMAND_DELIVERY = "demand_delivery"
    TRANSFER = "transfer"

@dataclass
class Event:
    time: int
    event_type: EventType
    service: Optional[Service] = None
    demand: Optional[Demand] = None
    terminal: Optional[str] = None
    
    def __lt__(self, other):
        return self.time < other.time

class Simulation:
    def __init__(self, network: Network):
        self.network = network
        self.current_time = 0
        self.event_queue: List[Event] = []
        self.demands: Dict[int, Demand] = {}
        self.performance_metrics = {
            'total_teus_transported': 0,
            'teus_per_service': {},  # service_id -> TEUs
            'teus_per_terminal': {},  # terminal -> TEUs
            'delays': [],  # List of delay durations
            'unfeasible_demands': []  # List of unfeasible demand IDs
        }
        
    def add_demand(self, demand: Demand) -> None:
        """Add a new demand to the simulation."""
        self.demands[demand.demand_id] = demand
        # Schedule demand arrival event
        arrival_event = Event(
            time=demand.start_time,
            event_type=EventType.DEMAND_ARRIVAL,
            demand=demand
        )
        heapq.heappush(self.event_queue, arrival_event)
        
    def process_demand_arrival(self, event: Event) -> None:
        """Process a demand arrival event."""
        demand = event.demand
        if not demand:
            return
            
        # Find feasible route
        route = self.network.find_route(
            origin=demand.origin,
            destination=demand.destination,
            start_time=demand.start_time,
            end_time=demand.end_time,
            demand_teus=demand.volume
        )
        
        if demand.assign_route(route):
            # Schedule events for each leg of the route
            for service, board_time, alight_time in route:
                # Schedule departure
                departure_event = Event(
                    time=board_time,
                    event_type=EventType.SERVICE_DEPARTURE,
                    service=service,
                    demand=demand,
                    terminal=service.origin
                )
                heapq.heappush(self.event_queue, departure_event)
                
                # Schedule arrival
                arrival_event = Event(
                    time=alight_time,
                    event_type=EventType.SERVICE_ARRIVAL,
                    service=service,
                    demand=demand,
                    terminal=service.destination
                )
                heapq.heappush(self.event_queue, arrival_event)
        else:
            self.performance_metrics['unfeasible_demands'].append(demand.demand_id)
            
    def process_service_departure(self, event: Event) -> None:
        """Process a service departure event."""
        if not (event.service and event.demand):
            return
            
        # Update demand status
        event.demand.update_status(self.current_time)
        
        # Update performance metrics
        service_id = event.service.service_id
        if service_id not in self.performance_metrics['teus_per_service']:
            self.performance_metrics['teus_per_service'][service_id] = 0
        self.performance_metrics['teus_per_service'][service_id] += event.demand.volume
        
    def process_service_arrival(self, event: Event) -> None:
        """Process a service arrival event."""
        if not (event.service and event.demand and event.terminal):
            return
            
        # Update demand status
        event.demand.update_status(self.current_time)
        
        # Update terminal metrics
        if event.terminal not in self.performance_metrics['teus_per_terminal']:
            self.performance_metrics['teus_per_terminal'][event.terminal] = 0
        self.performance_metrics['teus_per_terminal'][event.terminal] += event.demand.volume
        
        # If this is the final destination, schedule delivery
        if event.terminal == event.demand.destination:
            delivery_event = Event(
                time=self.current_time,
                event_type=EventType.DEMAND_DELIVERY,
                demand=event.demand,
                terminal=event.terminal
            )
            heapq.heappush(self.event_queue, delivery_event)
            
    def process_demand_delivery(self, event: Event) -> None:
        """Process a demand delivery event."""
        if not event.demand:
            return
            
        event.demand.update_status(self.current_time)
        self.performance_metrics['total_teus_transported'] += event.demand.volume
        
        # Calculate and record delay if any
        actual_delivery_time = self.current_time
        planned_delivery_time = event.demand.end_time
        if actual_delivery_time > planned_delivery_time:
            delay = actual_delivery_time - planned_delivery_time
            self.performance_metrics['delays'].append(delay)
            
    def run(self, until_time: int) -> None:
        """Run the simulation until specified time."""
        while self.event_queue and self.current_time <= until_time:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            if event.event_type == EventType.DEMAND_ARRIVAL:
                self.process_demand_arrival(event)
            elif event.event_type == EventType.SERVICE_DEPARTURE:
                self.process_service_departure(event)
            elif event.event_type == EventType.SERVICE_ARRIVAL:
                self.process_service_arrival(event)
            elif event.event_type == EventType.DEMAND_DELIVERY:
                self.process_demand_delivery(event)
                
        # Update status of all demands at end of simulation
        for demand in self.demands.values():
            demand.update_status(self.current_time)
            
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report."""
        return {
            'total_teus_transported': self.performance_metrics['total_teus_transported'],
            'teus_per_service': self.performance_metrics['teus_per_service'],
            'teus_per_terminal': self.performance_metrics['teus_per_terminal'],
            'average_delay': sum(self.performance_metrics['delays']) / len(self.performance_metrics['delays']) 
                if self.performance_metrics['delays'] else 0,
            'unfeasible_demands': len(self.performance_metrics['unfeasible_demands']),
            'total_demands': len(self.demands)
        }
