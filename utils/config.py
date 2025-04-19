import os

# Définition des chemins de base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Fichiers de données
DEMAND_FILE = os.path.join(DATA_DIR, "fichier_demande_4_1_12_52.txt")
DEMAND_PATH_FILE = os.path.join(DATA_DIR, "fichier_demandes_chemin_4_1_12_52.txt")

# Fichiers de sortie
PERFORMANCE_REPORT = os.path.join(OUTPUT_DIR, "performance_report.txt")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "results.txt")

# Créer les répertoires s'ils n'existent pas
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
