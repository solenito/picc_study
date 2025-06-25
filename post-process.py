import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import scipy
from sklearn.linear_model import LinearRegression

print("=== FORCE-DISPLACEMENT POST-PROCESSING SCRIPT ===")

# ====== CONFIGURATION ======
excel_file = "force-displacement-20-cycles-0-3.xlsx"  # Name of your Excel file
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

cycle = 20
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
plt.plot(disps_cycle, forces_cycle, 'g-', linewidth=2, label='Loading Phase cycle' + f' {cycle}')
plt.xlabel('Displacement (mm)', fontsize=12, fontweight='bold')
plt.ylabel('Force (N)', fontsize=12, fontweight='bold')
plt.title('Loading Phase of Cycle'+f'{cycle}', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()
    

# ====== OTHERS PLOTS ======
# Plot the loading phase of one cycle

if cycle == 1:
    load_start = 0  # 
else:
    load_start = peaks[cycle - 2]  
    
    for i in range(load_start, peaks[cycle - 1]):
        if forces_clean[i] <= force_min:  
            load_start = i
            break

load_end = peaks[cycle - 1] 


loading_forces = forces_clean[load_start:load_end]
loading_disps = displacements_clean[load_start:load_end]

plt.figure(figsize=(10, 6))
plt.plot(loading_disps, loading_forces, 'g-', linewidth=2, label='Loading Phase cycle' + f' {cycle}')
plt.xlabel('Displacement (mm)', fontsize=12, fontweight='bold')
plt.ylabel('Force (N)', fontsize=12, fontweight='bold')
plt.title('Loading Phase of Cycle'+f'{cycle}', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()

       
# Plot the unloading phase of the cycle

if cycle == 1:
    release_start = peaks[0]  
else:
    release_start = peaks[cycle - 1]  # end of the previous cycle (previous peak)

release_end = peaks[cycle - 1]  # peak of the current cycle

# search for return to 0 after the peak
for i in range(release_end, len(forces_clean)):
    if forces_clean[i] <= force_min:  
        release_end = i
        break

unloading_forces = forces_clean[release_start:release_end]
unloading_disps = displacements_clean[release_start:release_end]

plt.figure(figsize=(10, 6))
plt.plot(unloading_disps, unloading_forces, 'm-', linewidth=2, label='Unloading Phase cycle'+ f' {cycle}')
plt.xlabel('Displacement (mm)', fontsize=12, fontweight='bold')
plt.ylabel('Force (N)', fontsize=12, fontweight='bold')
plt.title('Unloading Phase of Cycle'+f'{cycle}', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()

    

# ====== FINAL REPORT ======
print("\n" + "="*50)
print(" FINAL REPORT")
print("="*50)
print(f" Data points: {len(forces_clean)}")
print(f" Cycles detected: {cycles_detected}")
print(f" Maximum force: {np.max(forces_clean):.2f} N")
print(f" Minimum force: {np.min(forces_clean):.2f} N")
print(f" Maximum displacement: {np.max(displacements_clean):.4f} mm")






# ===== STIFFNESS DURING UNLOADING ======
# first part of the derivative
dF = np.gradient(unloading_forces)
dU = np.gradient(unloading_disps)
slopes = dF / dU

max_slopes1 = 150000
min_slopes1 = 0

max_disps1 = 0.020
min_disps1 = 0.005

mask = slopes <= max_slopes1
slopes_clean = slopes[mask]
unloading_disps_clean = unloading_disps[mask]

mask2 = slopes_clean >= min_slopes1
slopes_clean2 = slopes_clean[mask2]
unloading_disps_clean2 = unloading_disps_clean[mask2]

mask_first_part = unloading_disps_clean2 < max_disps1
unloading_disps_clean2 = unloading_disps_clean2[mask_first_part]
slopes_clean2 = slopes_clean2[mask_first_part]

mask_first_part2 = unloading_disps_clean2 > min_disps1
unloading_disps_clean2 = unloading_disps_clean2[mask_first_part2]
slopes_clean2 = slopes_clean2[mask_first_part2]

# Plot pente
plt.figure(figsize=(10, 5))
plt.plot(unloading_disps_clean2, slopes_clean2, 'orange', label='dF/dU')
plt.xlabel('Displacement (mm)')
plt.ylabel('Stiffness (dF/dU)')
plt.title('Evolution of Stiffness During Unloading')
plt.grid(True, alpha=0.3)
plt.legend()


# delete NaN and inf in slope
mask_valid = ~np.isnan(slopes_clean2) & ~np.isinf(slopes_clean2)
xreg = unloading_disps_clean2[mask_valid].reshape(-1, 1)
yreg = slopes_clean2[mask_valid].reshape(-1, 1)

# ccreation of the model
model = LinearRegression()
model.fit(xreg, yreg)

# Coefficients
slope1 = float(model.coef_[0])
intercept1 = float(model.intercept_)
print(f"y = {slope1:.2f} * x + {intercept1:.2f}")

y_pred = model.predict(xreg)

plt.scatter(xreg, yreg, label='Données')
plt.plot(xreg, y_pred, color='red', label='Régression linéaire')
plt.legend()


#second part of the derivative

dF = np.gradient(unloading_forces)
dU = np.gradient(unloading_disps)
slopes = dF / dU

#max_slopes2 = ...
min_slopes2 = 0

#max_disps2 = 0.021
min_disps2 = 0.020

mask2 = slopes_clean >= min_slopes2
slopes_clean2 = slopes_clean[mask2]
unloading_disps_clean2 = unloading_disps_clean[mask2]

mask_second_part = unloading_disps_clean2 > min_disps2
unloading_disps_clean2 = unloading_disps_clean2[mask_second_part]
slopes_clean2 = slopes_clean2[mask_second_part]

mask_second_part2 = slopes_clean2 > min_slopes2
unloading_disps_clean2 = unloading_disps_clean2[mask_second_part2]
slopes_clean2 = slopes_clean2[mask_second_part2]


plt.figure(figsize=(10, 5))
plt.plot(unloading_disps_clean2, slopes_clean2, 'orange', label='dF/dU')
plt.xlabel('Displacement (mm)')
plt.ylabel('Stiffness (dF/dU)')
plt.title('Evolution of Stiffness During Unloading')
plt.grid(True, alpha=0.3)
plt.legend()


# delete NaN and inf in slope
mask_valid = ~np.isnan(slopes_clean2) & ~np.isinf(slopes_clean2)
xreg2 = unloading_disps_clean2[mask_valid].reshape(-1, 1)
yreg2 = slopes_clean2[mask_valid].reshape(-1, 1)

# creation of the model
model = LinearRegression()
model.fit(xreg2, yreg2)

# Coefficients
slope2 = float(model.coef_[0])
intercept2 = float(model.intercept_)
print(f"y = {slope2:.2f} * x + {intercept2:.2f}")

y_pred2 = model.predict(xreg2)

plt.scatter(xreg2, yreg2, label='Données')
plt.plot(xreg2, y_pred2, color='red', label='Régression linéaire')
plt.legend()





# =====  INTERSECTION ======

# calculation of the intersection point of the two lines
if slope1 != slope2:
    x_intersect = (intercept2 - intercept1) / (slope1 - slope2)
    y_intersect = slope1 * x_intersect + intercept1
else:
    x_intersect = None  # Parallel lines do not intersect
    y_intersect = None

# prolongation of the two lines
xreg1_min = np.min(xreg)
xreg1_max = x_intersect if x_intersect is not None else np.max(xreg)
xreg1_ext = np.linspace(xreg1_min, xreg1_max, 100)
yreg1_ext = slope1 * xreg1_ext + intercept1


xreg2_min = x_intersect if x_intersect is not None else np.min(xreg2)
xreg2_max = np.max(xreg2)
xreg2_ext = np.linspace(xreg2_min, xreg2_max, 100)
yreg2_ext = slope2 * xreg2_ext + intercept2

plt.figure(figsize=(10, 5))
plt.plot(xreg1_ext, yreg1_ext, color='red', label='Régression linéaire 1 (prolongée)')
plt.plot(xreg2_ext, yreg2_ext, color='blue', label='Régression linéaire 2')
plt.scatter(xreg, yreg, color='orange', s=10, label='Données 1')
plt.scatter(xreg2, yreg2, color='green', s=10, label='Données 2')

# mark the intersection point
if x_intersect is not None and y_intersect is not None:
    plt.plot(x_intersect, y_intersect, 'ko', markersize=8, label='Intersection')
    print(f"Intersection: x = {x_intersect:.5f}, y = {y_intersect:.2f}")

plt.xlabel('Displacement (mm)')
plt.ylabel('Stiffness (dF/dU)')
plt.title('Evolution of Stiffness During Unloading\n(Prolongement et intersection)')
plt.grid(True, alpha=0.3)
plt.legend()




# ====== find the closure force ======

disp_target = x_intersect  # Target displacement for opening force (intersection point)

# Check if loading_disps and loading_forces are not empty
if len(unloading_disps) == 0 or len(unloading_forces) == 0:
    print(" Error: Loading data is empty. Ensure the loading phase is correctly extracted.")
else:
    # Find the minimum and maximum displacements in the loading phase
    disp_min = np.min(unloading_disps)
    disp_max = np.max(unloading_disps)

    print(f" Target displacement: {disp_target} mm")
    print(f" Loading displacement range: {disp_min:.4f} to {disp_max:.4f} mm")

    if disp_min <= disp_target <= disp_max:
        # find the closest displacement in the loading phase
        closest_idx = np.argmin(np.abs(unloading_disps - disp_target))
        closest_disp = unloading_disps[closest_idx]
        closest_force = unloading_forces[closest_idx]

        print(f" Force at displacement {disp_target} mm:")
        print(f"   Closest displacement: {closest_disp:.4f} mm")
        print(f"   Closure force force: {closest_force:.2f} N")
        print("sigma_cl/sigma_max =",closest_force/ np.max(unloading_forces))
    else:
        # if the target displacement is outside the loading range
        print(f" Target displacement {disp_target} mm is outside the loading range.")
        if disp_target < disp_min:
            print(f"   Closest available displacement: {disp_min:.4f} mm")
            print(f"   Closure force: {unloading_forces[0]:.2f} N")
            print(unloading_forces[0])
            ratio = unloading_forces[0] / np.max(unloading_forces)
            print(f"sigma_cl/sigma_max = {ratio:.2f}")
        else:
            print(f"   Closest available displacement: {disp_max:.4f} mm")
            print(f"   Closure force: {unloading_forces[-1]:.2f} N")     
            print(f"sigma_cl/sigma_max = {unloading_forces[-1]:.2f/ np.max(unloading_forces)}")






# ===== STIFFNESS DURING LOADING ======
# first part of the derivative
dF = np.gradient(loading_forces)
dU = np.gradient(loading_disps)
slopes = dF / dU

max_slopes1 = 150000
min_slopes1 = 0

max_disps1 = 0.010
min_disps1 = 0

mask = slopes <= max_slopes1
slopes_clean = slopes[mask]
loading_disps_clean = loading_disps[mask]

mask2 = slopes_clean >= min_slopes1
slopes_clean2 = slopes_clean[mask2]
loading_disps_clean2 = loading_disps_clean[mask2]

mask_first_part = loading_disps_clean2 < max_disps1
loading_disps_clean2 = loading_disps_clean2[mask_first_part]
slopes_clean2 = slopes_clean2[mask_first_part]

mask_first_part2 = loading_disps_clean2 > min_disps1
loading_disps_clean2 = loading_disps_clean2[mask_first_part2]
slopes_clean2 = slopes_clean2[mask_first_part2]

# Plot pente
plt.figure(figsize=(10, 5))
plt.plot(loading_disps_clean2, slopes_clean2, 'orange', label='dF/dU')
plt.xlabel('Displacement (mm)')
plt.ylabel('Stiffness (dF/dU)')
plt.title('Evolution of Stiffness During loading')
plt.grid(True, alpha=0.3)
plt.legend()


# delete NaN and inf in slope
mask_valid = ~np.isnan(slopes_clean2) & ~np.isinf(slopes_clean2)
xreg1l = loading_disps_clean2[mask_valid].reshape(-1, 1)
yreg1l = slopes_clean2[mask_valid].reshape(-1, 1)

# ccreation of the model
model = LinearRegression()
model.fit(xreg1l, yreg1l)

# Coefficients
slope1l = float(model.coef_[0])
intercept1l = float(model.intercept_)
print(f"y = {slope1l:.2f} * x + {intercept1l:.2f}")

y_pred1l = model.predict(xreg1l)

plt.scatter(xreg1l, yreg1l, label='Données')
plt.plot(xreg1l, y_pred1l, color='red', label='Régression linéaire')
plt.legend()


#second part of the derivative

dF = np.gradient(loading_forces)
dU = np.gradient(loading_disps)
slopes = dF / dU

#max_slopes2 = ...
min_slopes2 = 135580

#max_disps2 = 0.021
min_disps2 = 0.010

mask2 = slopes_clean >= min_slopes2
slopes_clean2 = slopes_clean[mask2]
loading_disps_clean2 = loading_disps_clean[mask2]

mask_second_part = loading_disps_clean2 > min_disps2
loading_disps_clean2 = loading_disps_clean2[mask_second_part]
slopes_clean2 = slopes_clean2[mask_second_part]

mask_second_part2 = slopes_clean2 > min_slopes2
loading_disps_clean2 = loading_disps_clean2[mask_second_part2]
slopes_clean2 = slopes_clean2[mask_second_part2]


plt.figure(figsize=(10, 5))
plt.plot(loading_disps_clean2, slopes_clean2, 'orange', label='dF/dU')
plt.xlabel('Displacement (mm)')
plt.ylabel('Stiffness (dF/dU)')
plt.title('Evolution of Stiffness During loading')
plt.grid(True, alpha=0.3)
plt.legend()


# delete NaN and inf in slope
mask_valid = ~np.isnan(slopes_clean2) & ~np.isinf(slopes_clean2)
xreg2l = loading_disps_clean2[mask_valid].reshape(-1, 1)
yreg2l = slopes_clean2[mask_valid].reshape(-1, 1)

# creation of the model
model = LinearRegression()
model.fit(xreg2l, yreg2l)

# Coefficients
slope2l = float(model.coef_[0])
intercept2l = float(model.intercept_)
print(f"y = {slope2l:.2f} * x + {intercept2l:.2f}")

y_pred2l = model.predict(xreg2l)

plt.scatter(xreg2l, yreg2l, label='Données')
plt.plot(xreg2l, y_pred2l, color='red', label='Régression linéaire')
plt.legend()





# =====  INTERSECTION ======

# calculation of the intersection point of the two lines
if slope1l != slope2l:
    x_intersectl = (intercept2l - intercept1l) / (slope1l - slope2l)
    y_intersectl = slope1l * x_intersectl + intercept1l
else:
    x_intersectl = None  # Parallel lines do not intersect
    y_intersectl = None

# prolongation of the two lines
xreg1_min = np.min(xreg1l)
xreg1_max = x_intersectl if x_intersectl is not None else np.max(xreg1l)
xreg1_ext = np.linspace(xreg1_min, xreg1_max, 100)
yreg1_ext = slope1l* xreg1_ext + intercept1l


xreg2_min = x_intersectl if x_intersectl is not None else np.min(xreg2l)
xreg2_max = np.max(xreg2l)
xreg2_ext = np.linspace(xreg2_min, xreg2_max, 100)
yreg2_ext = slope2l * xreg2_ext + intercept2l

plt.figure(figsize=(10, 5))
plt.plot(xreg1_ext, yreg1_ext, color='red', label='Régression linéaire 1 (prolongée)')
plt.plot(xreg2_ext, yreg2_ext, color='blue', label='Régression linéaire 2')
plt.scatter(xreg1l, yreg1l, color='orange', s=10, label='Données 1')
plt.scatter(xreg2l, yreg2l, color='green', s=10, label='Données 2')

# mark the intersection point
if x_intersectl is not None and y_intersectl is not None:
    plt.plot(x_intersectl, y_intersectl, 'ko', markersize=8, label='Intersection')
    print(f"Intersection: x = {x_intersectl:.5f}, y = {y_intersectl:.2f}")

plt.xlabel('Displacement (mm)')
plt.ylabel('Stiffness (dF/dU)')
plt.title('Evolution of Stiffness During loading\n(Prolongement et intersection)')
plt.grid(True, alpha=0.3)
plt.legend()


# ====== find the opening force ======

disp_target = x_intersectl  # Target displacement for opening force (intersection point)

# Check if loading_disps and loading_forces are not empty
if len(loading_disps) == 0 or len(loading_forces) == 0:
    print(" Error: Loading data is empty. Ensure the loading phase is correctly extracted.")
else:
    # Find the minimum and maximum displacements in the loading phase
    disp_min = np.min(loading_disps)
    disp_max = np.max(loading_disps)

    print(f" Target displacement: {disp_target} mm")
    print(f" Loading displacement range: {disp_min:.4f} to {disp_max:.4f} mm")

    if disp_min <= disp_target <= disp_max:
        # find the closest displacement in the loading phase
        closest_idx = np.argmin(np.abs(loading_disps - disp_target))
        closest_disp = loading_disps[closest_idx]
        closest_force = loading_forces[closest_idx]

        print(f" Force at displacement {disp_target} mm:")
        print(f"   Closest displacement: {closest_disp:.4f} mm")
        print(f"   Opening force force: {closest_force:.2f} N")
        print("sigma_op/sigma_max =",closest_force/ np.max(loading_forces))
    else:
        # if the target displacement is outside the loading range
        print(f" Target displacement {disp_target} mm is outside the loading range.")
        if disp_target < disp_min:
            print(f"   Closest available displacement: {disp_min:.4f} mm")
            print(f"   Opening force: {loading_forces[0]:.2f} N")
            print(loading_forces[0])
            ratio = loading_forces[0] / np.max(loading_forces)
            print(f"sigma_op/sigma_max = {ratio:.2f}")
        else:
            print(f"   Closest available displacement: {disp_max:.4f} mm")
            print(f"   Opening force: {loading_forces[-1]:.2f} N")     
            ratio = loading_forces[-1] / np.max(loading_forces)
            print(f"sigma_op/sigma_max = {ratio:.2f}")

# ====== SHOW PLOTS ======
plt.show()

print(" Post-processing completed successfully!")
