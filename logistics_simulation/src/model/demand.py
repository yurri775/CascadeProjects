from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from .service import Service

class DemandStatus(Enum):
    WAITING = "waiting"  # Waiting for containers to arrive at origin
    READY = "ready"  # Containers at origin terminal, ready for transport
    IN_TRANSIT = "in_transit"  # Being transported
    WAITING_TRANSFER = "waiting_transfer"  # Waiting for transfer at intermediate terminal
    DELIVERED = "delivered"  # Arrived at destination
    UNFEASIBLE = "unfeasible"  # No feasible route found

@dataclass
class Demand:
    demand_id: int
    demand_type: str  # F, P, R, T etc.
    origin: str
    destination: str
    start_time: int  # Earliest departure time in half-days
    end_time: int  # Latest arrival time in half-days
    volume: int  # In TEUs
    status: DemandStatus = DemandStatus.WAITING
    assigned_route: Optional[List[Tuple[Service, int, int]]] = None
    current_position: Optional[str] = None
    current_service: Optional[Service] = None
    
    def __post_init__(self):
        self.current_position = self.origin
        
    def update_status(self, current_time: int) -> None:
        """Update demand status based on current time and route."""
        if self.status == DemandStatus.UNFEASIBLE:
            return
            
        if not self.assigned_route:
            if current_time >= self.start_time:
                self.status = DemandStatus.READY
            return
            
        for service, board_time, alight_time in self.assigned_route:
            if current_time < board_time:
                if self.current_position == service.origin:
                    self.status = DemandStatus.READY
                else:
                    self.status = DemandStatus.WAITING_TRANSFER
                return
            elif board_time <= current_time < alight_time:
                self.status = DemandStatus.IN_TRANSIT
                self.current_service = service
                self.current_position = service.get_current_position(current_time)
                return
                
        if current_time >= self.assigned_route[-1][2]:  # After last alighting time
            self.status = DemandStatus.DELIVERED
            self.current_position = self.destination
            self.current_service = None

    def assign_route(self, route: List[Tuple[Service, int, int]]) -> bool:
        """Assign a route to this demand."""
        if not route:
            self.status = DemandStatus.UNFEASIBLE
            return False
            
        # Verify route feasibility
        total_route_time = route[-1][2] - route[0][1]  # Last alighting - First boarding
        if total_route_time > (self.end_time - self.start_time):
            self.status = DemandStatus.UNFEASIBLE
            return False
            
        # Check service capacities
        for service, _, _ in route:
            if not service.has_capacity(self.volume):
                self.status = DemandStatus.UNFEASIBLE
                return False
                
        # Assign route and update services
        self.assigned_route = route
        for service, _, _ in route:
            service.add_load(self.volume)
            
        return True
