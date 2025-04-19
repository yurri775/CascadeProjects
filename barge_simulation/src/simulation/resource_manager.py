from dataclasses import dataclass
from typing import Dict, List
from src.utils.error_handler import ErrorHandler, SimulationError, SimulationErrorType

@dataclass
class ResourceUsage:
    resource_id: str
    start_time: float
    end_time: float
    usage_type: str

class ResourceManager:
    def __init__(self, error_handler: ErrorHandler):
        self.resources = {}
        self.usage_history = {}
        self.error_handler = error_handler
        
    def allocate_resource(self, resource_id: str, start_time: float, 
                         duration: float, usage_type: str) -> bool:
        if resource_id not in self.resources:
            self.error_handler.handle_error(
                SimulationError(
                    SimulationErrorType.RESOURCE_NOT_FOUND,
                    f"Ressource {resource_id} non trouvée"
                )
            )
            return False
            
        # Vérifier la disponibilité
        if self._is_resource_available(resource_id, start_time, start_time + duration):
            usage = ResourceUsage(resource_id, start_time, start_time + duration, usage_type)
            self.usage_history.setdefault(resource_id, []).append(usage)
            return True
            
        return False