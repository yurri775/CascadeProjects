# fix_simulator.py
import sys
import os

def main():
    # Localiser le fichier barge_simulator.py
    file_path = 'src/simulation/barge_simulator.py'
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return
    
    # Lire le contenu
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Vérifier si la modification est nécessaire
    if 'self.statistics = self.stats' not in content:
        # Chercher où init se termine
        init_end = content.find('def ', content.find('def __init__'))
        if init_end == -1:
            print("Erreur: Structure de fichier inattendue.")
            return
        
        # Ajouter la ligne avant la fin de init
        modified_content = content[:init_end].rstrip() + "\n        # Alias pour compatibilité\n        self.statistics = self.stats\n\n" + content[init_end:]
        
        # Écrire le contenu modifié
        with open(file_path, 'w') as f:
            f.write(modified_content)
        
        print(f"Correction appliquée à {file_path}")
    else:
        print("Le fichier a déjà été corrigé.")

if __name__ == "__main__":
    main()