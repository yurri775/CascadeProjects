import matplotlib.pyplot as plt
from model.barge import Barge
from model.network import SpaceTimeNetwork
from model.service import Service
from model.routing import RoutingManager
from model.demand import Demand
from simulation.simulator import BargeSimulator
from visualization.visualizer import SimulationVisualizer

class Demand:
    def __init__(self, id, origin, destination, quantity, time, deadline=None):
        self.id = id
        self.origin = origin
        self.destination = destination
        self.quantity = quantity
        self.time = time
        self.deadline = deadline

def create_sample_network():
    """Create a sample network for testing."""
    network = SpaceTimeNetwork()
    
    # Add nodes (ports and intersections)
    terminals = {
        'A': (0, 0),   # Port A
        'B': (10, 0),  # Port B
        'C': (20, 0),  # Port C
        'D': (30, 0),  # Port D
        'I1': (5, 5),  # Intersection 1
        'I2': (15, 5), # Intersection 2
        'I3': (25, 5)  # Intersection 3
    }
    
    # Add nodes with their positions
    for node_id, pos in terminals.items():
        if node_id.startswith('I'):
            # Intersection
            network.add_node(node_id, pos, 'intersection')
        else:
            # Port
            network.add_node(node_id, pos, 'port', capacity=2)
    
    # Add edges with travel times
    edges = [
        # Edges via intersections
        ('A', 'I1', 2),
        ('I1', 'B', 2),
        ('B', 'I2', 2),
        ('I2', 'C', 2),
        ('C', 'I3', 2),
        ('I3', 'D', 2),
        ('D', 'I3', 2),
        ('I3', 'C', 2),
        ('C', 'I2', 2),
        ('I2', 'B', 2),
        ('B', 'I1', 2),
        ('I1', 'A', 2),
        
        # Direct edges for services
        ('A', 'B', 4),  # Direct route A to B with time equal to A->I1->B
        ('B', 'C', 4),  # Direct route B to C with time equal to B->I2->C
        ('C', 'D', 4),  # Direct route C to D with time equal to C->I3->D
        ('D', 'C', 4),  # Direct route D to C with time equal to D->I3->C
        ('C', 'B', 4),  # Direct route C to B with time equal to C->I2->B
        ('B', 'A', 4)   # Direct route B to A with time equal to B->I1->A
    ]
    
    for from_node, to_node, travel_time in edges:
        network.add_edge(from_node, to_node, travel_time)
    
    return network

def create_services():
    """Create services for the network."""
    # Upstream service: A -> B -> C -> D
    service1 = Service('S1', 'A', 'D', legs=[('A', 'B', 4), ('B', 'C', 4), ('C', 'D', 4)], frequency=10)
    
    # Downstream service: D -> C -> B -> A
    service2 = Service('S2', 'D', 'A', legs=[('D', 'C', 4), ('C', 'B', 4), ('B', 'A', 4)], frequency=10)
    
    return [service1, service2]

def create_demands():
    """Create sample transportation demands."""
    demands = [
        # From A to C
        Demand('D1', 'A', 'C', 50, 0, due_date=20),
        
        # From B to D
        Demand('D2', 'B', 'D', 75, 5, due_date=25),
        
        # From D to A
        Demand('D3', 'D', 'A', 60, 10, due_date=30),
        
        # From C to B
        Demand('D4', 'C', 'B', 40, 15, due_date=35)
    ]
    
    return demands

def main():
    # Create network
    network = create_sample_network()
    
    # Create routing manager
    routing_manager = RoutingManager()
    
    # Create simulator
    simulator = BargeSimulator(network, routing_manager)
    
    # Create and add services
    services = create_services()
    for service in services:
        simulator.add_service(service)
    
    # Create and add barges
    barges = [
        Barge('B1', capacity=100, position='A', service_id='S1'),
        Barge('B2', capacity=150, position='D', service_id='S2')
    ]
    
    for barge in barges:
        simulator.add_barge(barge)
    
    # Create and add demands
    demands = create_demands()
    for demand in demands:
        simulator.demand_manager.add_demand(demand)
    
    # Run simulation
    print("Starting simulation...")
    simulator.run(until=50)
    print("Simulation completed!")
    
    # Print statistics
    stats = simulator.get_statistics()
    print("\nSimulation Statistics:")
    print(f"Simulation time: {stats['current_time']}")
    print(f"Events processed: {stats['events_processed']}")
    print(f"Total distance traveled: {stats['total_distance']}")
    
    demand_stats = simulator.demand_manager.get_statistics()
    print("\nDemand Statistics:")
    print(f"Total demands: {demand_stats['total']}")
    print(f"Completed: {demand_stats['completed']}")
    print(f"Failed: {demand_stats['failed']}")
    print(f"Pending: {demand_stats['pending']}")
    print(f"Assigned: {demand_stats['assigned']}")
    print(f"In progress: {demand_stats['in_progress']}")
    if 'avg_completion_time' in demand_stats:
        print(f"Average completion time: {demand_stats['avg_completion_time']:.2f}")
    
    # Create visualizer
    visualizer = SimulationVisualizer(network, simulator)
    
    # Plot network
    fig1, ax1 = visualizer.plot_network()
    plt.savefig('network.png')
    
    # Plot final barge positions
    fig2, ax2 = visualizer.plot_barge_positions()
    plt.savefig('barge_positions.png')
    
    # Plot demand status
    fig3, ax3 = visualizer.plot_demand_status()
    plt.savefig('demand_status.png')
    
    # Plot barge utilization
    fig4, ax4 = visualizer.plot_barge_utilization()
    plt.savefig('barge_utilization.png')
    
    print("\nVisualization images saved to disk.")
    
    # Show plots
    plt.show()

if __name__ == "__main__":
    main()
