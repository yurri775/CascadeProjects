from enum import Enum
from dataclasses import dataclass
from typing import Any

class SimulationErrorType(Enum):
    INVALID_TIME = "Erreur de temps"
    RESOURCE_NOT_FOUND = "Ressource non trouvée"
    CAPACITY_EXCEEDED = "Capacité dépassée"
    INVALID_ROUTE = "Route invalide"
    SYSTEM_ERROR = "Erreur système"

@dataclass
class SimulationError:
    error_type: SimulationErrorType
    message: str
    details: Any = None

class ErrorHandler:
    def __init__(self):
        self.errors = []
        self.warning_count = 0
        
    def handle_error(self, error: SimulationError):
        self.errors.append(error)
        print(f"ERREUR [{error.error_type.value}]: {error.message}")