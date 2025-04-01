from src.model.network import Network
from src.model.service import Service, BargeType
from src.model.demand import Demand
from src.model.simulation import Simulation
from src.visualization.network_visualizer import NetworkVisualizer
import os

def create_test_network() -> Network:
    """Create a test network with 4 terminals (A, B, C, D) and all services."""
    network = Network(cycle_length=14)  # 14 half-days cycle
    
    # Add terminals
    for terminal in ['A', 'B', 'C', 'D']:
        network.add_terminal(terminal)
        
    # Create service 1 (A -> D)
    service1 = Service(
        service_id=1,
        origin='A',
        destination='D',
        start_time=0,
        end_time=8,
        capacity=35,  # 1 large (25) + 1 small (10) barge
        barges={
            BargeType.LARGE: 1,
            BargeType.SMALL: 1
        }
    )
    
    # Add legs for service 1
    service1.add_leg('A', 'B', 2, 1)  # A->B from t=1 to t=3
    service1.add_leg('B', 'C', 2, 3)  # B->C from t=3 to t=5
    service1.add_leg('C', 'D', 2, 5)  # C->D from t=5 to t=7
    
    # Add stops for service 1
    service1.add_stop('A', 0)  # Loading at A at t=0
    service1.add_stop('B', 3)  # Stop at B at t=3
    service1.add_stop('C', 5)  # Stop at C at t=5
    service1.add_stop('D', 7)  # Final stop at D at t=7
    
    # Create service 2 (D -> B)
    service2 = Service(
        service_id=2,
        origin='D',
        destination='B',
        start_time=9,
        end_time=13,
        capacity=25,  # 1 large (25) barge
        barges={
            BargeType.LARGE: 1
        }
    )
    
    # Add legs for service 2
    service2.add_leg('D', 'C', 1, 10)  # D->C from t=10 to t=11
    service2.add_leg('C', 'B', 1, 11)  # C->B from t=11 to t=12
    
    # Add stops for service 2
    service2.add_stop('D', 9)   # Loading at D at t=9
    service2.add_stop('C', 11)  # Stop at C at t=11
    service2.add_stop('B', 12)  # Final stop at B at t=12
    
    # Create service 3 (A -> C)
    service3 = Service(
        service_id=3,
        origin='A',
        destination='C',
        start_time=2,
        end_time=7,
        capacity=15,  # 1 medium (15) barge
        barges={
            BargeType.MEDIUM: 1
        }
    )
    
    # Add legs for service 3
    service3.add_leg('A', 'B', 2, 3)  # A->B from t=3 to t=5
    service3.add_leg('B', 'C', 1, 5)  # B->C from t=5 to t=6
    
    # Add stops for service 3
    service3.add_stop('A', 2)  # Loading at A at t=2
    service3.add_stop('B', 5)  # Stop at B at t=5
    service3.add_stop('C', 6)  # Final stop at C at t=6
    
    # Add all services to network
    network.add_service(service1)
    network.add_service(service2)
    network.add_service(service3)
    
    return network

def create_test_demands() -> list[Demand]:
    """Create test demands as specified in the scenario."""
    demands = [
        Demand(
            demand_id=1,
            demand_type='F',
            origin='A',
            destination='D',
            start_time=0,
            end_time=8,
            volume=13
        ),
        Demand(
            demand_id=2,
            demand_type='P',
            origin='D',
            destination='B',
            start_time=11,
            end_time=15,  # 1 in next cycle = 15
            volume=15
        ),
        Demand(
            demand_id=3,
            demand_type='R',
            origin='A',
            destination='C',
            start_time=2,
            end_time=13,
            volume=20
        ),
        Demand(
            demand_id=4,
            demand_type='T',
            origin='D',
            destination='B',
            start_time=0,
            end_time=12,
            volume=18
        )
    ]
    return demands

def main():
    # Create output directory for visualizations
    os.makedirs('output', exist_ok=True)
    
    # Create network
    network = create_test_network()
    
    # Create simulation
    simulation = Simulation(network)
    
    # Create visualizer
    visualizer = NetworkVisualizer(network)
    
    # Add demands
    for demand in create_test_demands():
        simulation.add_demand(demand)
    
    # Run simulation for one cycle (14 half-days) with visualization
    for t in range(14):
        simulation.run(until_time=t+1)
        # Save network state visualization
        visualizer.plot_network_state(
            simulation.demands, t,
            save_path=f'output/network_state_{t}.png',
            show=False
        )
    
    # Generate final visualizations
    visualizer.plot_service_utilization(
        simulation,
        save_path='output/service_utilization.png',
        show=False
    )
    
    visualizer.plot_demand_status(
        simulation.demands,
        save_path='output/demand_status.png',
        show=False
    )
    
    # Print performance report
    report = simulation.get_performance_report()
    print("\nSimulation Performance Report:")
    print("-" * 30)
    print(f"Total TEUs transported: {report['total_teus_transported']}")
    print("\nTEUs per service:")
    for service_id, teus in report['teus_per_service'].items():
        print(f"  Service {service_id}: {teus} TEUs")
    print("\nTEUs per terminal:")
    for terminal, teus in report['teus_per_terminal'].items():
        print(f"  Terminal {terminal}: {teus} TEUs")
    print(f"\nAverage delay: {report['average_delay']:.2f} half-days")
    print(f"Unfeasible demands: {report['unfeasible_demands']}")
    print(f"Total demands: {report['total_demands']}")
    
    # Print final status of all demands
    print("\nDemand Status Report:")
    print("-" * 30)
    for demand_id, demand in simulation.demands.items():
        print(f"Demand {demand_id} ({demand.demand_type}):")
        print(f"  Status: {demand.status.value}")
        print(f"  Current position: {demand.current_position}")
        if demand.assigned_route:
            print("  Route:")
            for service, board_time, alight_time in demand.assigned_route:
                print(f"    Service {service.service_id}: {board_time} -> {alight_time}")
        print()

if __name__ == "__main__":
    main()
