import logging
from datetime import datetime

class SimulationLogger:
    def __init__(self, simulation_id: str):
        self.logger = logging.getLogger(f"simulation_{simulation_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # Log file
        file_handler = logging.FileHandler(
            f"logs/simulation_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatage
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)