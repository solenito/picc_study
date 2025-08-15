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
excel_file = "S_0-3/picc_s03_r00.xlsx"  # Name of your Excel file
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

# ====== MAIN PLOT ======
plt.figure(figsize=(12, 8))
plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')

# Plot force-displacement curve
plt.plot(displacements_clean, forces_clean, 'b-', linewidth=1.5, label='Force vs Displacement')

# Mark peaks (cycles)
if len(peaks) > 0:
    plt.plot(displacements_clean[peaks], forces_clean[peaks], 'ro', 
             markersize=6, label=f'Cycle peaks ({len(peaks)})')

# ====== FORMATTING ======
plt.xlabel('Displacement (mm)', fontsize=12, fontweight='bold')
plt.ylabel('Load (N)', fontsize=12, fontweight='bold')
plt.title('Force-Displacement Curve\nCyclic Fatigue Analysis', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend(fontsize=10)

# Statistics on the plot
stats_text = f"""Statistics:
• Points: {len(forces_clean)}
• Cycles: {cycles_detected}
• Max force: {np.max(forces_clean):.0f} N
• Max disp.: {np.max(displacements_clean):.3f} mm
• Amplitude: {np.max(forces_clean) - np.min(forces_clean):.0f} N"""

plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
         fontsize=9)

# ====== SECONDARY PLOT - ZOOM ONE CYCLE ======

cycle = 21
force_min = 0

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

plt.figure(figsize=(10, 6))
plt.style.use('default')
plt.plot(disps_cycle, forces_cycle, 'g-', linewidth=2, label='Last cycle ' + f' {cycle}')
plt.xlabel('Displacement (mm)', fontsize=12, fontweight='bold')
plt.ylabel('Force (N)', fontsize=12, fontweight='bold')
plt.title('Last cycle '+f'{cycle}', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()

plt.show()