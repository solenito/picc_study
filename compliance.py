import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import scipy
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import scipy.stats as stats

print("=== FORCE-DISPLACEMENT POST-PROCESSING SCRIPT ===")

# ====== CONFIGURATION ======
excel_file = "force-displacement-20-cycles-0-3_0-2.xlsx"  # Name of your Excel file
#excel_file = "force-displacement-0-2-perfectly-plastic.xlsx"  # Name of your Excel file
sheet_name = "Sheet1"        # Sheet name (or 0 for first sheet)

# Column names in Excel file
force_column = "force"       # Force column (N)
displacement_column = "displacement"  # Displacement column (mm)

# ====== EXCEL FILE READING ======
try:
    # Check if file exists
    if not os.path.exists(excel_file):
        print("File not found:", excel_file)
        print("Available files in directory:")
        for file in os.listdir("."):
            if file.endswith(('.xlsx', '.xls', '.csv')):
                print("  -", file)
        exit()
    
    # Read Excel file
    print("Reading file:", excel_file)
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print("File read successfully")
    print("Dimensions:", df.shape)
    print("Available columns:", list(df.columns))
    
except Exception as e:
    print(" Excel reading error:", str(e))
    exit()

# ====== DATA EXTRACTION ======
forces = df[force_column].values
displacements = df[displacement_column].values

# MULTIPLY DISPLACEMENTS BY 2
displacements = displacements * 2.0 # for the total displacement

# ====== DATA CLEANING ======
# Remove NaN values
mask = ~(np.isnan(forces) | np.isnan(displacements))
forces_clean = forces[mask]
displacements_clean = displacements[mask]

if len(forces_clean) < len(forces):
    print(f"  {len(forces) - len(forces_clean)} NaN values removed")

# ====== CYCLE ANALYSIS ======
# Detect cycles (force peaks)
from scipy.signal import find_peaks

peaks, _ = find_peaks(forces_clean, height=np.max(forces_clean)*0.8)
cycles_detected = len(peaks)
print(f" Cycles detected: {cycles_detected}")


# ====== SECONDARY PLOT - ZOOM ONE CYCLE ======

cycle = 20
force_min = 750

if cycle == 1:
    start = 0  # first cycle starts at the beginning
else:
    start = peaks[cycle - 2]  # end of the previous cycle (previous peak)
    
    for i in range(start, peaks[cycle - 1]):
        if forces_clean[i] <= force_min:  # tolerance to consider "force ≈ 0"
            start = i
            break

end = peaks[cycle - 1]  #   peak of the current cycle

# search for return to 0 after the peak
for i in range(end, len(forces_clean)):
    if forces_clean[i] <= force_min:  
        end = i
        break


forces_cycle = forces_clean[start:end]
disps_cycle = displacements_clean[start:end]



# ====== OTHERS PLOTS ======
# Plot the loading phase of one cycle

if cycle == 1:
    load_start = 0  # 
else:
    load_start = peaks[cycle - 2]  
    
    for i in range(load_start, peaks[cycle - 1]):
        if forces_clean[i] <= force_min +1:  
            load_start = i
            break

load_end = peaks[cycle - 1] 


loading_forces = forces_clean[load_start:load_end]
loading_disps = displacements_clean[load_start:load_end]

       
# Plot the unloading phase of the cycle

if cycle == 1:
    release_start = peaks[0]  
else:
    release_start = peaks[cycle - 1]  # end of the previous cycle (previous peak)

release_end = peaks[cycle - 1]  # peak of the current cycle

#print(release_start, release_end )

# search for return to 0 after the peak
for i in range(release_end, len(forces_clean)):
    if forces_clean[i] <= force_min+1:  
        release_end = i
        break

unloading_forces = forces_clean[release_start:release_end]
unloading_disps = displacements_clean[release_start:release_end]

plt.figure(figsize=(8, 6))
plt.plot(unloading_forces, unloading_disps, 'g-', linewidth=2, label='Déchargement : déplacement(force)')
plt.xlabel('Force (N)', fontsize=12, fontweight='bold')
plt.ylabel('Déplacement (mm)', fontsize=12, fontweight='bold')
plt.title('Déplacement en fonction de la force (phase de déchargement)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()


# Calcul de la dérivée dU/dF (compliance locale)
compliance_locale = np.gradient(unloading_disps, unloading_forces)




plt.figure(figsize=(8, 6))
plt.plot(unloading_forces, compliance_locale, 'b-', linewidth=2, label='dU/dF (compliance instantanée)')
plt.xlabel('Force (N)', fontsize=12, fontweight='bold')
plt.ylabel('dU/dF (mm/N)', fontsize=12, fontweight='bold')
plt.title('Compliance instantanée (dérivée déplacement/force)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()

# Sélection des 25% premiers points du déchargement
n_points = len(unloading_forces)
n_reg = int(0.25 * n_points)
forces_reg = unloading_forces[:n_reg]
disps_reg = unloading_disps[:n_reg]

# Régression linéaire : déplacement = a * force + b
X = forces_reg.reshape(-1, 1)
y = disps_reg
model = LinearRegression()
model.fit(X, y)
fully_open_compliance = model.coef_[0]
intercept = model.intercept_

print(f"Régression sur les 25% premiers points du déchargement : déplacement = {fully_open_compliance:.6e} * force + {intercept:.6e}")


sigma_on_sigma_max = unloading_forces / np.max(unloading_forces)


print("fully open compliance = ", fully_open_compliance)

# Calcul de l'écart relatif en %
C_off = (compliance_locale - fully_open_compliance) / fully_open_compliance * 100

plt.figure(figsize=(8, 6))
plt.plot(C_off, sigma_on_sigma_max, 'm-', linewidth=2, label='C_off (%)')
plt.show()