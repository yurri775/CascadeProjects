import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple
from ..model.network import Network
from ..model.service import Service
from ..model.demand import Demand, DemandStatus

class NetworkVisualizer:
    def __init__(self, network: Network):
        self.network = network
        self.colors = {
            'A': '#1f77b4',  # blue
            'B': '#2ca02c',  # green
            'C': '#ff7f0e',  # orange
            'D': '#d62728'   # red
        }
        
    def create_space_time_graph(self) -> nx.DiGraph:
        """Create a directed graph representing the space-time network."""
        G = nx.DiGraph()
        
        # Add nodes for each terminal at each time step
        for t in range(self.network.cycle_length):
            for terminal in self.network.terminals:
                node_id = f"{terminal}_{t}"
                G.add_node(node_id, 
                          pos=(t, ord(terminal) - ord('A')),
                          terminal=terminal,
                          time=t)
                
                # Add horizontal (waiting) edges
                if t < self.network.cycle_length - 1:
                    next_node = f"{terminal}_{t+1}"
                    G.add_edge(node_id, next_node, edge_type='wait')
        
        # Add service edges
        for service in self.network.services.values():
            for leg in service.legs:
                G.add_edge(
                    f"{leg.origin}_{leg.start_time}",
                    f"{leg.destination}_{leg.end_time}",
                    edge_type='service',
                    service_id=service.service_id
                )
                
        return G
        
    def plot_network_state(self, demands: Dict[int, Demand], time: int, 
                          save_path: str = None, show: bool = True):
        """Plot the current state of the network with demands."""
        G = self.create_space_time_graph()
        
        plt.figure(figsize=(15, 8))
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw nodes
        for node in G.nodes():
            terminal = G.nodes[node]['terminal']
            nx.draw_networkx_nodes(G, pos,
                                 nodelist=[node],
                                 node_color=self.colors[terminal],
                                 node_size=500)
        
        # Draw edges
        wait_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d['edge_type'] == 'wait']
        service_edges = [(u, v) for (u, v, d) in G.edges(data=True) if d['edge_type'] == 'service']
        
        nx.draw_networkx_edges(G, pos, edgelist=wait_edges, edge_color='gray', style='dashed')
        nx.draw_networkx_edges(G, pos, edgelist=service_edges, edge_color='black', arrows=True)
        
        # Draw labels
        labels = {node: f"{G.nodes[node]['terminal']}" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels)
        
        # Plot demands
        for demand in demands.values():
            if demand.status != DemandStatus.DELIVERED:
                if demand.current_position:
                    # Handle case where demand is between terminals
                    if demand.current_position.startswith('Between'):
                        # Extract terminals from "Between X and Y" format
                        parts = demand.current_position.split()
                        if len(parts) >= 4:  # "Between A and B" format
                            origin = parts[1]
                            destination = parts[3]
                            # Plot demand halfway between terminals
                            y1 = ord(origin) - ord('A')
                            y2 = ord(destination) - ord('A')
                            y = (y1 + y2) / 2
                            plt.plot(time, y, 'ko', markersize=10, label=f'Demand {demand.demand_id}')
                            plt.annotate(f'D{demand.demand_id}', (time, y), 
                                       xytext=(10, 10), textcoords='offset points')
                    else:
                        # Normal case - demand at a terminal
                        y = ord(demand.current_position) - ord('A')
                        plt.plot(time, y, 'ko', markersize=10, label=f'Demand {demand.demand_id}')
                        plt.annotate(f'D{demand.demand_id}', (time, y), 
                                   xytext=(10, 10), textcoords='offset points')
        
        plt.grid(True)
        plt.title(f'Network State at t={time}')
        plt.xlabel('Time (half-days)')
        plt.ylabel('Terminals')
        plt.yticks(range(len(self.network.terminals)), 
                  sorted(list(self.network.terminals)))
        
        if save_path:
            plt.savefig(save_path)
        if show:
            plt.show()
        plt.close()
        
    def plot_service_utilization(self, simulation, save_path: str = None, show: bool = True):
        """Plot service utilization over time."""
        plt.figure(figsize=(12, 6))
        
        for service_id, teus in simulation.performance_metrics['teus_per_service'].items():
            service = self.network.services[service_id]
            capacity = service.capacity
            utilization = (teus / capacity) * 100
            plt.bar(f'Service {service_id}', utilization,
                   color=plt.cm.Set3(service_id / len(self.network.services)))
            
        plt.axhline(y=100, color='r', linestyle='--', label='Max Capacity')
        plt.ylabel('Utilization (%)')
        plt.title('Service Utilization')
        plt.legend()
        
        if save_path:
            plt.savefig(save_path)
        if show:
            plt.show()
        plt.close()
        
    def plot_demand_status(self, demands: Dict[int, Demand], 
                          save_path: str = None, show: bool = True):
        """Plot demand status distribution."""
        status_counts = {}
        for demand in demands.values():
            status = demand.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
        plt.figure(figsize=(10, 6))
        plt.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%',
                colors=plt.cm.Set3(np.linspace(0, 1, len(status_counts))))
        plt.title('Demand Status Distribution')
        
        if save_path:
            plt.savefig(save_path)
        if show:
            plt.show()
        plt.close()
