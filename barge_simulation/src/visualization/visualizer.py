import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.animation import FuncAnimation

class SimulationVisualizer:
    """
    Visualizes the simulation results.
    """
    def __init__(self, network, simulator):
        """
        Initialize the visualizer.
        
        Args:
            network: Network instance (SpaceTimeNetwork or Network)
            simulator (BargeSimulator): Simulator instance
        """
        self.network = network
        self.simulator = simulator
        self.fig = None
        self.ax = None
        
    def plot_network(self, show_labels=True):
        """
        Plot the network.
        
        Args:
            show_labels (bool): Whether to show node labels
        """
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        
        # Create a NetworkX graph from our network
        G = nx.DiGraph()
        
        # Determine node positions based on network type
        node_positions = {}
        node_types = {}
        
        if hasattr(self.network, 'nodes'):
            # SpaceTimeNetwork
            for node_id, node_data in self.network.nodes.items():
                position = node_data.get('position', (0, 0))
                node_type = node_data.get('type', 'default')
                node_positions[node_id] = position
                node_types[node_id] = node_type
                G.add_node(node_id, pos=position)
        elif hasattr(self.network, 'terminals'):
            # Network - Generate fictional positions
            terminals = list(self.network.terminals.keys())
            for i, terminal in enumerate(terminals):
                angle = (i / len(terminals)) * 2 * np.pi
                x = np.cos(angle) * 10
                y = np.sin(angle) * 10
                position = (x, y)
                node_type = self.network.terminals[terminal].get('type', 'terminal')
                node_positions[terminal] = position
                node_types[terminal] = node_type
                G.add_node(terminal, pos=position)
            
        # Add edges based on network type
        if hasattr(self.network, 'edges'):
            # SpaceTimeNetwork
            for (from_node, to_node), edge_data in self.network.edges.items():
                G.add_edge(from_node, to_node, weight=edge_data.get('travel_time', 0))
        elif hasattr(self.network, 'arcs'):
            # Network
            for (from_node, to_node), arc_data in self.network.arcs.items():
                G.add_edge(from_node, to_node, weight=arc_data.get('travel_time', 0))
            
        # Get positions for nodes
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw nodes with appropriate colors based on node type
        node_colors = []
        for node in G.nodes():
            node_type = node_types.get(node, 'default')
            if node_type == 'port':
                node_colors.append('lightblue')
            else:
                node_colors.append('lightgreen')
                
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=500, 
                              alpha=0.8)
        
        # Draw edges with arrows
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=15, width=1.5, edge_color='gray')
        
        # Draw labels if requested
        if show_labels:
            nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
            
            # Draw edge labels (travel times)
            edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        # Set title and remove axis
        plt.title('Barge Transportation Network')
        plt.axis('off')
        
        return self.fig, self.ax
        
    def plot_barge_positions(self, time_point=None):
        """
        Plot the positions of barges at a specific time point.
        
        Args:
            time_point (float, optional): Time point to visualize. If None, uses the current time.
        """
        if self.fig is None or self.ax is None:
            self.plot_network(show_labels=True)
            
        # Use current time if not specified
        if time_point is None:
            time_point = self.simulator.current_time
            
        # Get positions for nodes
        pos = nx.get_node_attributes(nx.DiGraph(self.network.network), 'pos')
        
        # Plot barges
        for barge_id, barge in self.simulator.barges.items():
            if barge.position in pos:
                barge_pos = pos[barge.position]
                self.ax.plot(barge_pos[0], barge_pos[1], 'ro', markersize=10, alpha=0.7)
                self.ax.text(barge_pos[0], barge_pos[1] + 0.1, barge_id, fontsize=8, ha='center')
                
        plt.title(f'Barge Positions at Time {time_point}')
        
        return self.fig, self.ax
        
    def plot_demand_status(self):
        """
        Plot the status of demands.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get demand statistics
        stats = self.simulator.demand_manager.get_statistics()
        
        # Create a pie chart
        labels = ['Completed', 'In Progress', 'Assigned', 'Pending', 'Failed']
        sizes = [
            stats['completed'],
            stats['in_progress'],
            stats['assigned'],
            stats['pending'],
            stats['failed']
        ]
        
        # Remove zero values
        non_zero_labels = []
        non_zero_sizes = []
        for label, size in zip(labels, sizes):
            if size > 0:
                non_zero_labels.append(label)
                non_zero_sizes.append(size)
        
        if non_zero_sizes:
            colors = ['#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ff9999']
            ax.pie(non_zero_sizes, labels=non_zero_labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
        plt.title('Demand Status')
        
        return fig, ax
        
    def plot_barge_utilization(self):
        """
        Plot the utilization of barges.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get barge IDs and utilization
        barge_ids = list(self.simulator.barges.keys())
        utilization = [barge.get_utilization() for barge in self.simulator.barges.values()]
        
        # Create a bar chart
        ax.bar(barge_ids, utilization, color='skyblue')
        ax.set_ylim(0, 100)
        ax.set_xlabel('Barge ID')
        ax.set_ylabel('Utilization (%)')
        ax.set_title('Barge Utilization')
        
        # Add value labels on top of bars
        for i, v in enumerate(utilization):
            ax.text(i, v + 2, f"{v:.1f}%", ha='center')
            
        return fig, ax
        
    def create_animation(self, interval=1000, frames=None):
        """
        Create an animation of the simulation.
        
        Args:
            interval (int): Interval between frames in milliseconds
            frames (int, optional): Number of frames to generate
            
        Returns:
            FuncAnimation: Animation object
        """
        if self.fig is None or self.ax is None:
            self.plot_network(show_labels=True)
            
        # Get positions for nodes
        pos = nx.get_node_attributes(nx.DiGraph(self.network.network), 'pos')
        
        # Create a scatter plot for barges
        scatter = self.ax.scatter([], [], c='red', s=100, alpha=0.7)
        
        # Create text annotations for barge IDs
        barge_texts = [self.ax.text(0, 0, '', fontsize=8, ha='center') for _ in self.simulator.barges]
        
        def init():
            scatter.set_offsets(np.empty((0, 2)))
            for text in barge_texts:
                text.set_text('')
            return [scatter] + barge_texts
            
        def update(frame):
            # Get barge positions at this frame
            barge_positions = []
            barge_ids = []
            
            for barge in self.simulator.barges.values():
                if barge.position in pos:
                    barge_positions.append(pos[barge.position])
                    barge_ids.append(barge.barge_id)
            
            # Update scatter plot
            if barge_positions:
                scatter.set_offsets(barge_positions)
            else:
                scatter.set_offsets(np.empty((0, 2)))
                
            # Update text annotations
            for i, text in enumerate(barge_texts):
                if i < len(barge_positions):
                    text.set_position((barge_positions[i][0], barge_positions[i][1] + 0.1))
                    text.set_text(barge_ids[i])
                else:
                    text.set_text('')
                    
            self.ax.set_title(f'Barge Positions at Time {frame}')
            
            return [scatter] + barge_texts
            
        # Create animation
        if frames is None:
            frames = int(self.simulator.current_time) + 1
            
        anim = FuncAnimation(self.fig, update, frames=range(frames),
                             init_func=init, blit=True, interval=interval)
                             
        return anim
