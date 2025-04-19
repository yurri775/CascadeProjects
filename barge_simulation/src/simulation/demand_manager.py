from typing import List, Dict
import heapq
from dataclasses import dataclass

@dataclass
class AssignmentScore:
    demand_id: str
    barge_id: str
    score: float
    waiting_time: float
    distance: float

class DemandManager:
    def __init__(self, router, performance_analyzer):
        self.pending_demands = []
        self.router = router
        self.performance_analyzer = performance_analyzer
        
    def optimize_assignments(self, demands: List[Dict], available_barges: List[Dict]) -> List[Dict]:
        assignments = []
        scores = []
        
        # Calculer les scores pour chaque paire demande-barge
        for demand in demands:
            for barge in available_barges:
                score = self._calculate_assignment_score(demand, barge)
                if score:
                    heapq.heappush(scores, (-score.score, score))  # Négatif pour max-heap
        
        # Assigner les demandes en commençant par les meilleurs scores
        while scores and demands:
            _, score = heapq.heappop(scores)
            if self._is_valid_assignment(score):
                assignments.append({
                    'demand_id': score.demand_id,
                    'barge_id': score.barge_id,
                    'waiting_time': score.waiting_time,
                    'expected_distance': score.distance
                })
                
        return assignments