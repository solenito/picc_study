import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import scipy
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import scipy.stats as stats


excel_file = "load-unload-cycle20.xlsx"  # Name of your Excel file
#excel_file = "force-displacement-0-2-perfectly-plastic.xlsx"  # Name of your Excel file
sheet_name = "Sheet1"        # Sheet name (or 0 for first sheet)

# Column names in Excel file
force_load = "force_load"       # Force column (N)
displacement_load = "displacement_load"  # Displacement column (mm)

force_unload = "force_unload"       # Force column (N)
displacement_unload = "displacement_unload"  # Displacement column (mm)

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
forces_l = df[force_load].values
displacements_l = df[displacement_load].values

forces_ul = df[force_unload].values
displacements_ul = df[displacement_unload].values

# MULTIPLY DISPLACEMENTS BY 2
displacements_l = displacements_l * 2.0 # for the total displacement
displacements_ul = displacements_ul * 2.0 # for the total displacement

# ====== DATA CLEANING ======
# Remove NaN values
mask = ~(np.isnan(forces_l) | np.isnan(displacements_l))
forces_l_clean = forces_l[mask]
displacements_l_clean = displacements_l[mask]

if len(forces_l_clean) < len(forces_l):
    print(f"  {len(forces_l) - len(forces_l_clean)} NaN values removed")
    
mask2 = ~(np.isnan(forces_ul) | np.isnan(displacements_ul))
forces_ul_clean = forces_ul[mask2]
displacements_ul_clean = displacements_ul[mask2]

if len(forces_ul_clean) < len(forces_ul):
    print(f"  {len(forces_ul) - len(forces_ul_clean)} NaN values removed")
    
    
'''plt.figure(figsize=(10, 6))
plt.plot(forces_l_clean, displacements_l_clean, 'r-', linewidth=2, label='Loading Phase')
plt.plot(forces_ul_clean, displacements_ul_clean, 'b-', linewidth=2, label='Unloading Phase')
plt.xlabel('Force (N)', fontsize=12, fontweight='bold')     
plt.ylabel('Displacement (mm)', fontsize=12, fontweight='bold')
plt.title('Force-Displacement Curve', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()'''


def compliance_offset(Xl, Yl, Xul, Yul, Xl_min, X_max, Xul_min, params, opt):
    """
    Python version of complianceOffset.m (ASTM method)
    Parameters:
        Xl, Yl: loading curve (force, disp)
        Xul, Yul: unloading curve (force, disp)
        Xl_min, X_max, Xul_min: min/max for loading/unloading
        params: [span, shift, shift1, HL, F]
        opt: 1 (loading only) or 2 (loading and unloading)
    Returns:
        Xseg_l, Coffset_l, Xseg_ul, Coffset_ul
    """
    span, shift, shift1, HL, F = params
    LL = HL - F

    # --- Open crack compliance calculation (unloading) ---
    idx_ul = np.where((Xul >= (Xul_min + LL * (X_max - Xul_min))) &
                      (Xul <= (Xul_min + HL * (X_max - Xul_min))))[0]
    coeffs = np.polyfit(Xul[idx_ul], Yul[idx_ul], 1)
    C0 = coeffs[0]

    # --- Instantaenous compliance of overlapping segments ---
    Xseg_l = Coffset_l = Xseg_ul = Coffset_ul = None
    for i in range(1, opt+1):
        if i == 1:
            X, Y, X_min = Xl, Yl, Xl_min
            if X[0] > X_min:
                istart = np.argmin(np.abs(X - X_min))
                X = X[istart:]
                Y = Y[istart:]
        else:
            X, Y, X_min = Xul, Yul, Xul_min

        N_segments = 2 + int(np.floor((1 - span) / shift))
        if span % shift == 0:
            N_segments -= 1
        Range = X_max - X_min
        Width = Range * span
        X_mid = X_min + Range * np.concatenate((
            [0.5 * span],
            0.5 * span + np.arange(shift, (N_segments - 2 + 1) * shift, shift),
            [1 - 0.5 * span]
        ))

        # Segment compliances
        C1 = np.zeros(N_segments)
        for j in range(N_segments):
            idx_seg = np.where((X >= X_mid[j] - 0.5 * Width) & (X <= X_mid[j] + 0.5 * Width))[0]
            coeffs_seg = np.polyfit(X[idx_seg], Y[idx_seg], 1)
            C1[j] = coeffs_seg[0]
        Coffset1 = (C0 - C1) * 100 / C0

        # Improved ASTM method (Chung, Song, 2009)
        X_mid_fine = np.arange(X_mid[0], X_mid[1] + Range * shift1 / 2, Range * shift1)
        C2 = np.zeros(len(X_mid_fine))
        for k in range(len(X_mid_fine)):
            idx_seg_fine = np.where((X >= X_mid_fine[k] - 0.5 * Width) & (X <= X_mid_fine[k] + 0.5 * Width))[0]
            coeffs_seg_fine = np.polyfit(X[idx_seg_fine], Y[idx_seg_fine], 1)
            C2[k] = coeffs_seg_fine[0]
        Coffset2 = (C0 - C2) * 100 / C0

        # Extrapolate compliance offset C2 to Xmin
        coeff_extrap = np.polyfit(Coffset2, X_mid_fine, 1)
        Coffset_Xmin = (X_min - coeff_extrap[1]) / coeff_extrap[0]

        # Combine all compliance offset results
        Coffset = np.concatenate(([Coffset_Xmin], Coffset2, Coffset1[2:]))
        Xseg = np.concatenate(([X_min], X_mid_fine, X_mid[2:]))

        if i == 1:
            Xseg_l, Coffset_l = Xseg, Coffset
        else:
            Xseg_ul, Coffset_ul = Xseg, Coffset

    if opt == 1:
        Xseg_ul, Coffset_ul = np.nan, np.nan

    return Xseg_l, Coffset_l, Xseg_ul, Coffset_ul




Xl = forces_l_clean
Yl = displacements_l_clean  
Xul = forces_ul_clean
Yul = displacements_ul_clean
Xl_min = np.min(Xl)
X_max = np.max(Xl)
Xul_min = np.min(Xul)

params = [0.1, 0.05, 0.01, 1, 0.25]  # span, shift, shift1, HL, F
opt = 2  # 1 for loading only, 2 for loading and unloading  


Xseg_l, Coffset_l, Xseg_ul, Coffset_ul = compliance_offset(Xl, Yl, Xul, Yul, Xl_min, X_max, Xul_min, params, opt)

sig_normalized_l = Xseg_l / X_max
sig_normalized_ul = Xseg_ul / X_max
# ====== PLOT LOADING AND UNLOADING COMPLIANCE ======

plt.figure(figsize=(10, 6))
plt.plot(Coffset_l, sig_normalized_l, 'r-', linewidth=2, label='Loading Compliance')
plt.plot(Coffset_ul, sig_normalized_ul, 'b-', linewidth=2, label='Unloading Compliance')
plt.axvline(x=0, color='k', linestyle='--', linewidth=1, label='C_off = 0%')
plt.xlabel('σ/σ_max', fontsize=12, fontweight='bold')           
plt.ylabel('C_off (%)', fontsize=12, fontweight='bold')
plt.title('Compliance Offset', fontsize=14, fontweight='bold')  
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()