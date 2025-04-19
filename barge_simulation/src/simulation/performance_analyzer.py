from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class PerformanceMetrics:
    terminal_utilization: Dict[str, float]
    service_utilization: Dict[str, float]
    barge_utilization: Dict[str, float]
    demand_completion_rate: float
    average_waiting_time: float
    total_distance: float
    total_cost: float

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics_history = []
        
    def calculate_metrics(self, simulation_state) -> PerformanceMetrics:
        terminal_util = self._calculate_terminal_utilization(simulation_state)
        service_util = self._calculate_service_utilization(simulation_state)
        barge_util = self._calculate_barge_utilization(simulation_state)
        completion_rate = self._calculate_demand_completion_rate(simulation_state)
        avg_wait_time = self._calculate_average_waiting_time(simulation_state)
        total_dist = self._calculate_total_distance(simulation_state)
        total_cost = self._calculate_total_cost(simulation_state)
        
        metrics = PerformanceMetrics(
            terminal_util, service_util, barge_util,
            completion_rate, avg_wait_time, total_dist, total_cost
        )
        
        self.metrics_history.append(metrics)
        return metrics