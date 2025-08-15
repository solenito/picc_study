import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ====== CONFIGURATION ======
excel_file = "S_0-1/contact_s01_r00.xlsx"  # Nom de votre fichier Excel
sheet_name = "Sheet1"              # Nom de la feuille (ou 0 pour la première)

# Colonnes à lire
time_column = "time"
node_columns = ["node47", "node46", "node45"]

# ====== LECTURE DU FICHIER EXCEL ======
try:
    # Vérifier si le fichier existe
    if not os.path.exists(excel_file):
        print("Fichier non trouvé:", excel_file)
        print("Fichiers disponibles dans le répertoire:")
        for file in os.listdir("."):
            if file.endswith(('.xlsx', '.xls', '.csv')):
                print("  -", file)
        exit()
    
    # Lire le fichier Excel
    print("Lecture du fichier:", excel_file)
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print("Fichier lu avec succès")
    print("Dimensions:", df.shape)
    print("Colonnes disponibles:", list(df.columns))
    
except Exception as e:
    print("Erreur lors de la lecture du fichier Excel:", str(e))
    exit()

# ====== VÉRIFICATION DES COLONNES ======
required_columns = [time_column] + node_columns
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"Colonnes manquantes: {missing_columns}")
    print("Colonnes disponibles:", list(df.columns))
    exit()

# ====== EXTRACTION DES DONNÉES ======
time_data = df[time_column].values

# Nettoyer les données (supprimer les valeurs NaN)
mask = ~np.isnan(time_data)
time_clean = time_data[mask]

node_data = {}
for node in node_columns:
    data = df[node].values[mask]
    # Supprimer les NaN pour chaque nœud
    node_mask = ~np.isnan(data)
    if len(data[node_mask]) > 0:
        node_data[node] = data
    else:
        print(f"Attention: Pas de données valides pour {node}")

print(f"Données nettoyées - {len(time_clean)} points temporels")

# ====== CRÉATION DU GRAPHIQUE ======
plt.figure(figsize=(12, 8))

# Couleurs pour chaque nœud
colors = ['red', 'blue', 'green', 'orange', 'purple']

# Tracer chaque nœud
for i, (node, data) in enumerate(node_data.items()):
    color = colors[i % len(colors)]
    plt.plot(time_clean, data, color=color, linewidth=2, label=node, marker='o', markersize=3)

# Configuration du graphique
plt.xlabel('Time', fontsize=12, fontweight='bold')
plt.ylabel('Node Values', fontsize=12, fontweight='bold')
plt.title('Evolution of Node Values Over Time', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()

# Améliorer l'affichage
plt.tight_layout()

# Afficher les statistiques
print("\n====== STATISTIQUES ======")
for node, data in node_data.items():
    print(f"{node}:")
    print(f"  Min: {np.min(data):.3f}")
    print(f"  Max: {np.max(data):.3f}")
    print(f"  Moyenne: {np.mean(data):.3f}")
    print(f"  Écart-type: {np.std(data):.3f}")

plt.show()