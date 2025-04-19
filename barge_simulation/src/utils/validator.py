from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ValidationRule:
    field_name: str
    field_type: type
    min_value: float = None
    max_value: float = None
    required: bool = True

class DataValidator:
    def __init__(self):
        self.rules = {
            'barge': [
                ValidationRule('capacity', float, min_value=0),
                ValidationRule('position', str, required=True)
            ],
            'demand': [
                ValidationRule('volume', float, min_value=0),
                ValidationRule('origin', str, required=True),
                ValidationRule('destination', str, required=True),
                ValidationRule('due_time', float, min_value=0)
            ]
        }
    
    def validate(self, data_type: str, data: Dict[str, Any]) -> bool:
        if data_type not in self.rules:
            raise ValueError(f"Type de données inconnu: {data_type}")
            
        for rule in self.rules[data_type]:
            if rule.required and rule.field_name not in data:
                return False
            
            value = data.get(rule.field_name)
            if value is not None:
                if not isinstance(value, rule.field_type):
                    return False
                if rule.min_value is not None and value < rule.min_value:
                    return False
                if rule.max_value is not None and value > rule.max_value:
                    return False
                    
        return True