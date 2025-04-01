#!/usr/bin/env python3
"""
Script pour exécuter tous les scénarios de test de la simulation de barges.
"""
import os
import subprocess
import time
from datetime import datetime

def create_output_directory(scenario_name):
    """Crée un répertoire de sortie pour le scénario."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output_{scenario_name}_{timestamp}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def run_scenario(script_name, scenario_name):
    """Exécute un scénario de test et capture les résultats."""
    print(f"\n=== Exécution du scénario: {scenario_name} ===")
    print(f"Script: {script_name}")
    
    # Créer un répertoire de sortie unique pour ce scénario
    output_dir = create_output_directory(scenario_name)
    
    # Exécuter le script
    try:
        start_time = time.time()
        result = subprocess.run(
            ["python", script_name],
            capture_output=True,
            text=True,
            check=True
        )
        duration = time.time() - start_time
        
        # Sauvegarder la sortie
        with open(os.path.join(output_dir, "output.txt"), "w") as f:
            f.write(f"=== Sortie du scénario {scenario_name} ===\n")
            f.write(f"Durée: {duration:.2f} secondes\n\n")
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n=== STDERR ===\n")
            f.write(result.stderr)
        
        # Déplacer les fichiers de sortie générés
        if os.path.exists("output"):
            for file in os.listdir("output"):
                src = os.path.join("output", file)
                dst = os.path.join(output_dir, file)
                os.rename(src, file)
        
        print(f"✓ Scénario terminé avec succès")
        print(f"  Durée: {duration:.2f} secondes")
        print(f"  Résultats sauvegardés dans: {output_dir}")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Erreur lors de l'exécution du scénario")
        print(f"  Code de sortie: {e.returncode}")
        print(f"  Erreur: {e.stderr}")
        
        # Sauvegarder l'erreur
        with open(os.path.join(output_dir, "error.txt"), "w") as f:
            f.write(f"=== Erreur du scénario {scenario_name} ===\n")
            f.write(f"Code de sortie: {e.returncode}\n\n")
            f.write("=== STDOUT ===\n")
            f.write(e.stdout)
            f.write("\n=== STDERR ===\n")
            f.write(e.stderr)

def main():
    """Exécute tous les scénarios de test."""
    print("=== Démarrage des tests de simulation ===\n")
    
    # Liste des scénarios à exécuter
    scenarios = [
        ("src/main.py", "simulation_simple"),
        ("run_simulation.py", "simulation_reelle"),
        ("analyze_simulation.py", "analyse_complete")
    ]
    
    # Exécuter chaque scénario
    for script, name in scenarios:
        run_scenario(script, name)
    
    print("\n=== Tous les tests sont terminés ===")

if __name__ == "__main__":
    main()
