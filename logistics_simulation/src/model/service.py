from dataclasses import dataclass
from typing import List, Tuple, Dict
from enum import Enum

class BargeType(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

    @property
    def capacity(self) -> int:
        capacities = {
            BargeType.SMALL: 10,
            BargeType.MEDIUM: 15,
            BargeType.LARGE: 25
        }
        return capacities[self]

@dataclass
class Leg:
    origin: str
    destination: str
    duration: int  # in half-days
    start_time: int  # start time in half-days
    end_time: int  # end time in half-days

class Service:
    def __init__(
        self,
        service_id: int,
        origin: str,
        destination: str,
        start_time: int,
        end_time: int,
        capacity: int,
        barges: Dict[BargeType, int]
    ):
        self.service_id = service_id
        self.origin = origin
        self.destination = destination
        self.start_time = start_time  # in half-days
        self.end_time = end_time  # in half-days
        self.capacity = capacity  # in TEUs
        self.barges = barges  # Dict[BargeType, count]
        self.legs: List[Leg] = []
        self.stops: List[Tuple[str, int]] = []  # List of (terminal, time) tuples
        self.current_load = 0  # Current load in TEUs
        
    def add_leg(self, origin: str, destination: str, duration: int, start_time: int) -> None:
        """Add a leg to the service."""
        leg = Leg(
            origin=origin,
            destination=destination,
            duration=duration,
            start_time=start_time,
            end_time=start_time + duration
        )
        self.legs.append(leg)

    def add_stop(self, terminal: str, time: int) -> None:
        """Add a stop at a terminal."""
        self.stops.append((terminal, time))

    def get_current_position(self, current_time: int) -> str:
        """Get the current position of the service at a given time."""
        if current_time < self.start_time or current_time > self.end_time:
            return None
            
        # Check if at a stop
        for terminal, time in self.stops:
            if time == current_time:
                return terminal
                
        # Check if on a leg
        for leg in self.legs:
            if leg.start_time <= current_time < leg.end_time:
                return f"Between {leg.origin} and {leg.destination}"
                
        return None

    def has_capacity(self, demand_teus: int) -> bool:
        """Check if the service has enough remaining capacity."""
        return self.current_load + demand_teus <= self.capacity

    def add_load(self, teus: int) -> bool:
        """Add load to the service if capacity allows."""
        if not self.has_capacity(teus):
            return False
        self.current_load += teus
        return True

    def remove_load(self, teus: int) -> bool:
        """Remove load from the service."""
        if self.current_load < teus:
            return False
        self.current_load -= teus
        return True

    def is_feasible_for_demand(self, origin: str, destination: str, start_time: int, end_time: int) -> bool:
        """Check if this service can handle a demand between given terminals within time constraints."""
        # Check if terminals are served by this service
        origin_served = False
        destination_served = False
        origin_time = None
        destination_time = None

        # Check stops including origin and destination
        for terminal, time in self.stops:
            if terminal == origin:
                origin_served = True
                origin_time = time
            elif terminal == destination and origin_served:
                destination_served = True
                destination_time = time

        if not (origin_served and destination_served):
            return False

        # Check time constraints
        if origin_time < start_time:
            return False
        if destination_time > end_time:
            return False

        return True
