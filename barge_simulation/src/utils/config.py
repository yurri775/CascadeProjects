from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ProjectConfig:
    TERMINALS: List[str] = None
    SERVICES: Dict[str, Dict] = None
    
    def __post_init__(self):
        self.TERMINALS = ['A', 'B', 'C', 'D']
        self.SERVICES = {
            'S1': {'route': ['A', 'B', 'C', 'D'], 'capacity': 100},
            'S2': {'route': ['D', 'C', 'B', 'A'], 'capacity': 100}
        }