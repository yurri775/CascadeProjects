"""
Visualisation des mouvements de barges dans l'espace et le temps.
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch, Patch
import json

class MovementVisualizer:
    """Visualiseur des mouvements de barges."""
    
    def __init__(self, network, barges, events):
        """
        Initialise le visualiseur.
        
        Args:
            network: Réseau spatio-temporel
            barges: Dictionnaire des barges
            events: Liste des événements traités
        """
        self.network = network
        self.barges = barges
        self.events = events
        self.movement_data = self._extract_movement_data()
        
    def _extract_movement_data(self):
        """Extrait les données de mouvement des barges."""
        movement_data = {}
        terminal_positions = {}
        
        # Obtenir les positions initiales
        if hasattr(self.network, 'nodes'):
            for node_id, node_data in self.network.nodes.items():
                terminal_positions[node_id] = node_data['position']
        elif hasattr(self.network, 'terminals'):
            for i, terminal in enumerate(self.network.terminals.keys()):
                angle = (i / len(self.network.terminals)) * 2 * np.pi
                x = np.cos(angle) * 10
                y = np.sin(angle) * 10
                terminal_positions[terminal] = (x, y)

        # Utiliser les attributs de l'objet Event au lieu de l'indexation
        initial_time = min(event.time for event in self.events)
        movement_data[initial_time] = {}

        for barge_id, barge in self.barges.items():
            initial_position = barge.position
            if initial_position in terminal_positions:
                movement_data[initial_time][barge_id] = terminal_positions[initial_position]

        return movement_data
    
    def create_animation(self, output_file='barge_animation.gif', fps=5):
        """
        Crée une animation des mouvements des barges.
        
        Args:
            output_file: Chemin du fichier de sortie
            fps: Images par seconde
        """
        # Créer la figure et les axes
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Dessiner le réseau
        self._draw_network(ax)
        
        # Obtenir les temps triés
        timestamps = sorted(self.movement_data.keys())
        
        # Créer un scatter plot pour les barges (initialement vide)
        barge_scatter = ax.scatter([], [], s=150, c='red', edgecolor='black', zorder=10)
        
        # Fonction de mise à jour pour l'animation
        def update(frame):
            time = timestamps[frame]
            positions = self.movement_data[time]
            
            if positions:
                # Extraire les coordonnées x et y des barges
                x = [pos[0] for pos in positions.values()]
                y = [pos[1] for pos in positions.values()]
                
                # Mettre à jour les positions des barges
                barge_scatter.set_offsets(np.column_stack([x, y]))
                
                # Ajouter des étiquettes pour les barges
                for barge_id, pos in positions.items():
                    # Supprimer les anciennes étiquettes
                    for txt in ax.texts:
                        if hasattr(txt, 'barge_id') and txt.barge_id == barge_id:
                            txt.remove()
                    
                    # Ajouter une nouvelle étiquette
                    text = ax.text(pos[0], pos[1] + 1.5, barge_id, fontsize=10, 
                                  ha='center', color='red', weight='bold')
                    text.barge_id = barge_id  # Stocker l'ID de la barge pour pouvoir la supprimer plus tard
            
            # Mettre à jour le titre avec le temps actuel
            ax.set_title(f'Time: {time:.1f}')
            return [barge_scatter] if barge_scatter else []
        
        # Créer l'animation
        ani = animation.FuncAnimation(fig, update, frames=len(timestamps),
                                    interval=1000/fps, blit=True)
        
        # Enregistrer l'animation
        ani.save(output_file, writer='pillow', fps=fps)
        plt.close()
        
    def _draw_network(self, ax):
        """
        Dessine le réseau sur les axes fournis.
        
        Args:
            ax: Axes matplotlib
        """
        # Dessiner les nœuds
        node_positions = {}
        
        # Déterminer les positions des terminaux en fonction du type de réseau
        if hasattr(self.network, 'nodes'):
            # SpaceTimeNetwork
            for node_id, node_data in self.network.nodes.items():
                position = node_data.get('position', (0, 0))
                node_type = node_data.get('type', 'default')
                node_positions[node_id] = {
                    'position': position,
                    'type': node_type
                }
        elif hasattr(self.network, 'terminals'):
            # Network - Générer des positions fictives
            terminals = list(self.network.terminals.keys())
            for i, terminal in enumerate(terminals):
                angle = (i / len(terminals)) * 2 * np.pi
                x = np.cos(angle) * 10
                y = np.sin(angle) * 10
                node_positions[terminal] = {
                    'position': (x, y),
                    'type': self.network.terminals[terminal].get('type', 'terminal')
                }
        
        # Dessiner les nœuds
        for node_id, node_data in node_positions.items():
            x, y = node_data['position']
            color = 'blue' if node_data['type'] == 'port' else 'green'
            ax.scatter(x, y, s=200, c=color, edgecolor='black', zorder=5)
            ax.text(x, y - 1.5, node_id, fontsize=12, ha='center', weight='bold')
        
        # Dessiner les arêtes
        if hasattr(self.network, 'edges'):
            # SpaceTimeNetwork
            for (from_node, to_node), edge_data in self.network.edges.items():
                if from_node in node_positions and to_node in node_positions:
                    from_pos = node_positions[from_node]['position']
                    to_pos = node_positions[to_node]['position']
                    
                    # Dessiner une flèche
                    arrow = FancyArrowPatch(
                        from_pos, to_pos,
                        arrowstyle='-|>',
                        mutation_scale=15,
                        linewidth=1.5,
                        color='gray',
                        alpha=0.6,
                        zorder=1
                    )
                    ax.add_patch(arrow)
                    
                    # Ajouter le temps de voyage
                    mid_x = (from_pos[0] + to_pos[0]) / 2
                    mid_y = (from_pos[1] + to_pos[1]) / 2
                    ax.text(mid_x, mid_y, f"{edge_data.get('travel_time', 0)}", fontsize=10, 
                           ha='center', va='center', 
                           bbox=dict(facecolor='white', alpha=0.7))
        elif hasattr(self.network, 'arcs'):
            # Network
            for (from_node, to_node), arc_data in self.network.arcs.items():
                if from_node in node_positions and to_node in node_positions:
                    from_pos = node_positions[from_node]['position']
                    to_pos = node_positions[to_node]['position']
                    
                    # Dessiner une flèche
                    arrow = FancyArrowPatch(
                        from_pos, to_pos,
                        arrowstyle='-|>',
                        mutation_scale=15,
                        linewidth=1.5,
                        color='gray',
                        alpha=0.6,
                        zorder=1
                    )
                    ax.add_patch(arrow)
                    
                    # Ajouter le temps de voyage
                    mid_x = (from_pos[0] + to_pos[0]) / 2
                    mid_y = (from_pos[1] + to_pos[1]) / 2
                    ax.text(mid_x, mid_y, f"{arc_data.get('travel_time', 0)}", fontsize=10, 
                           ha='center', va='center', 
                           bbox=dict(facecolor='white', alpha=0.7))
            
        # Configurer les limites et les étiquettes des axes
        all_positions = [data['position'] for data in node_positions.values()]
        all_x = [pos[0] for pos in all_positions]
        all_y = [pos[1] for pos in all_positions]
        
        # Ajouter une marge
        margin = 5
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
        
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Titre
        ax.set_title('Réseau de transport de barges', fontsize=15)
        
    def create_timeline(self, output_file='barge_timeline.png'):
        """
        Crée une visualisation en chronogramme des mouvements des barges.
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        # Créer la figure et les axes
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # Obtenir les temps triés
        times = sorted(self.movement_data.keys())
        max_time = max(times)
        
        # Palettes de couleurs pour les terminaux
        terminal_ids = []
        if hasattr(self.network, 'nodes'):
            terminal_ids = list(self.network.nodes.keys())
        elif hasattr(self.network, 'terminals'):
            terminal_ids = list(self.network.terminals.keys())
            
        cmap = plt.cm.Paired
        terminal_colors = {tid: cmap(i/len(terminal_ids)) for i, tid in enumerate(terminal_ids)}
        
        # Hauteur de chaque barre de barge
        barge_height = 0.8
        
        # Dessiner le chronogramme pour chaque barge
        for i, (barge_id, barge) in enumerate(self.barges.items()):
            y_pos = i * 1.2
            
            # Position initiale
            current_terminal = barge.position
            start_time = 0
            
            # Pour chaque point temporel, vérifier si la barge a changé de position
            for time_idx in range(len(times) - 1):
                time = times[time_idx]
                next_time = times[time_idx + 1]
                
                # Position actuelle
                positions = self.movement_data[time]
                next_positions = self.movement_data[next_time]
                
                if barge_id in positions and barge_id in next_positions:
                    current_pos = positions[barge_id]
                    next_pos = next_positions[barge_id]
                    
                    # Trouver les terminaux correspondant aux positions
                    current_terminal = None
                    next_terminal = None
                    
                    # Créer un dictionnaire de positions de nœuds pour recherche
                    node_positions = {}
                    if hasattr(self.network, 'nodes'):
                        for node_id, node_data in self.network.nodes.items():
                            node_positions[tuple(node_data['position'])] = node_id
                    elif hasattr(self.network, 'terminals'):
                        # Générer des positions fictives pour les terminaux
                        terminals = list(self.network.terminals.keys())
                        for i, terminal in enumerate(terminals):
                            angle = (i / len(terminals)) * 2 * np.pi
                            x = np.cos(angle) * 10
                            y = np.sin(angle) * 10
                            node_positions[(x, y)] = terminal
                    
                    # Trouver le terminal le plus proche pour chaque position
                    current_terminal = self._find_closest_terminal(current_pos, node_positions)
                    next_terminal = self._find_closest_terminal(next_pos, node_positions)
                    
                    # Si le terminal a changé, dessiner un rectangle pour le segment
                    if current_terminal:
                        color = terminal_colors.get(current_terminal, 'gray')
                        duration = next_time - start_time
                        rect = Rectangle((start_time, y_pos - barge_height/2), 
                                       duration, barge_height, 
                                       color=color, alpha=0.7,
                                       label=current_terminal if i == 0 and time_idx == 0 else "")
                        ax.add_patch(rect)
                        
                        # Ajouter une étiquette si la durée est suffisamment longue
                        if duration > 1:
                            ax.text(start_time + duration/2, y_pos, 
                                   current_terminal, 
                                   ha='center', va='center', 
                                   fontsize=8, color='black')
                    
                    # Si le terminal a changé, mettre à jour le temps de début
                    if current_terminal != next_terminal:
                        start_time = next_time
                        current_terminal = next_terminal
            
            # Dernier segment jusqu'à la fin
            if current_terminal:
                color = terminal_colors.get(current_terminal, 'gray')
                duration = max_time - start_time
                rect = Rectangle((start_time, y_pos - barge_height/2), 
                               duration, barge_height, 
                               color=color, alpha=0.7)
                ax.add_patch(rect)
                
                # Ajouter une étiquette si la durée est suffisamment longue
                if duration > 1:
                    ax.text(start_time + duration/2, y_pos, 
                           current_terminal, 
                           ha='center', va='center', 
                           fontsize=8, color='black')
        
        # Configurer les axes
        ax.set_yticks([i * 1.2 for i in range(len(self.barges))])
        ax.set_yticklabels(list(self.barges.keys()))
        ax.set_xlabel('Temps', fontsize=12)
        ax.set_ylabel('Barge', fontsize=12)
        ax.set_xlim(0, max_time)
        ax.set_ylim(-0.5, len(self.barges) * 1.2)
        
        # Légende
        handles = [Patch(color=terminal_colors[tid], alpha=0.7) for tid in terminal_ids]
        ax.legend(handles, terminal_ids, title='Terminaux', loc='upper right')
        
        # Titre
        ax.set_title('Chronogramme des mouvements des barges', fontsize=15)
        
        # Grille
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)
        
        # Enregistrer l'image
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        
    def _find_closest_terminal(self, position, node_positions):
        """
        Trouve le terminal le plus proche d'une position donnée.
        
        Args:
            position: Position (x, y)
            node_positions: Dictionnaire des positions des nœuds {(x, y): node_id}
            
        Returns:
            ID du terminal le plus proche
        """
        if not node_positions:
            return None
            
        position = tuple(position)
        if position in node_positions:
            return node_positions[position]
            
        # Trouver le terminal le plus proche
        min_dist = float('inf')
        closest_terminal = None
        
        for pos, terminal_id in node_positions.items():
            dist = ((pos[0] - position[0]) ** 2 + (pos[1] - position[1]) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_terminal = terminal_id
                
        return closest_terminal

# Fonction pour enregistrer les événements de la simulation dans un fichier
def save_events(simulator, filename):
    """
    Enregistre les événements traités dans un fichier JSON pour analyse ultérieure.
    
    Args:
        simulator: Le simulateur avec les événements
        filename: Le nom du fichier de sortie
    """
    events_data = []
    
    for event in simulator.processed_events:
        # Préparer les données pour la sérialisation
        event_dict = {
            "id": getattr(event, "id", 0),
            "time": event.time,
            "type": getattr(event, "event_type", "unknown"),
            "data": {}
        }
        
        # Convertir les données spécifiques aux événements
        for key, value in event.data.items():
            if hasattr(value, "__dict__"):
                # C'est un objet, extraire ses attributs
                event_dict["data"][key] = {k: v for k, v in value.__dict__.items() 
                                          if not k.startswith("_") and not callable(v)}
            else:
                # C'est un type simple
                event_dict["data"][key] = value
                
        events_data.append(event_dict)
    
    # Enregistrer au format JSON
    with open(filename, 'w') as f:
        json.dump(events_data, f, indent=2)
    
    print(f"Événements enregistrés dans {filename}")
