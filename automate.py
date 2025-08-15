import os
import time

# List of parameters for each job
'''
charge_levels0 = [0.01, 0.11, 0.22, 0.33, 0.44, 0.56, 0.67, 0.78, 0.89, 1.0] #r ratio = 0.0
    
charge_levels1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] #r ratio = 0.1    
    
charge_levels2 = [0.2, 0.29, 0.38, 0.47, 0.56, 0.64, 0.73, 0.82, 0.91, 1.0] #r ratio = 0.2

charge_levels3 = [0.3, 0.38, 0.47, 0.55, 0.63, 0.72, 0.8, 0.88, 0.97, 1.0] #r ratio = 0.3

charge_levels5 = [0.5, 0.56, 0.61, 0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0] #r ratio = 0.5



# Ratio R = 0.0 (décharge complète jusqu'à 0%)
decharge_levels0 = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50,
                    0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.00] #r ratio = 0.0

# Ratio R = 0.1 (décharge jusqu'à 10%)
decharge_levels1 = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50,
                    0.45, 0.40, 0.35, 0.30, 0.25, 0.22, 0.19, 0.16, 0.13, 0.10] #r ratio = 0.1

# Ratio R = 0.2 (décharge jusqu'à 20%)
decharge_levels2 = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50,
                    0.45, 0.42, 0.39, 0.36, 0.33, 0.30, 0.27, 0.24, 0.22, 0.20] #r ratio = 0.2

# Ratio R = 0.3 (décharge jusqu'à 30%)
decharge_levels3 = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.52,
                    0.49, 0.46, 0.43, 0.40, 0.38, 0.36, 0.34, 0.32, 0.31, 0.30] #r ratio = 0.3

# Ratio R = 0.5 (décharge jusqu'à 50%)
decharge_levels5 = [0.95, 0.90, 0.85, 0.80, 0.78, 0.76, 0.74, 0.72, 0.70, 0.68,
                    0.66, 0.64, 0.62, 0.60, 0.58, 0.56, 0.54, 0.52, 0.51, 0.50] #r ratio = 0.5


stress_ratios = [0.1, 0.2, 0.3]  # Corresponds to the charge levels

charge = [charge_levels0, charge_levels1, charge_levels2, charge_levels3, charge_levels5]

decharge = [decharge_levels0, decharge_levels1, decharge_levels2, decharge_levels3, decharge_levels5]

r_ratios = [0.0, 0.1, 0.2, 0.3, 0.5]  # Corresponds to the decharge levels
'''



'''
charge_levels0 = [0.3, 0.38, 0.46, 0.54, 0.62, 0.70, 0.78, 0.86, 0.94, 1.0] #r ratio = 0.3
    
charge_levels1 = [0.5, 0.56, 0.61, 0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0] #r ratio = 0.5

# Ratio R = 0.3
decharge_levels0 = [1.0, 0.98, 0.95, 0.93, 0.90, 0.88, 0.85, 0.83, 0.80, 0.78,
                    0.75, 0.73, 0.70, 0.68, 0.65, 0.63, 0.60, 0.58, 0.55, 0.53,
                    0.50, 0.48, 0.45, 0.43, 0.40, 0.38, 0.35, 0.33, 0.31, 0.30] #r ratio = 0.3

# Ratio R = 0.5
decharge_levels1 = [1.0, 0.98, 0.97, 0.95, 0.93, 0.92, 0.90, 0.88, 0.87, 0.85,
                    0.83, 0.82, 0.80, 0.78, 0.77, 0.75, 0.73, 0.72, 0.70, 0.68,
                    0.67, 0.65, 0.63, 0.62, 0.60, 0.58, 0.57, 0.55, 0.53, 0.50] #r ratio = 0.5

stress_ratios = [0.3]  # Corresponds to the charge levels

charge = [charge_levels0, charge_levels1]

decharge = [decharge_levels0, decharge_levels1]

r_ratios = [0.3, 0.5]  # Corresponds to the decharge levels
'''

charge_levels1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] #r ratio = 0.1

decharge_levels1 = [1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82, 0.79, 0.76, 0.73,
                    0.70, 0.67, 0.64, 0.61, 0.58, 0.55, 0.52, 0.49, 0.46, 0.43,
                    0.40, 0.37, 0.34, 0.31, 0.28, 0.25, 0.22, 0.19, 0.16, 0.10] #r ratio = 0.1


stress_ratios = [0.3]  # Corresponds to the charge levels

charge = [charge_levels1]

decharge = [decharge_levels1]

r_ratios = [0.1]  # Corresponds to the decharge levels



job_counter = 0
total_jobs = len(stress_ratios) * len(r_ratios)





for stress_ratio in stress_ratios:
    for i, r_ratio in enumerate(r_ratios):
        job_counter += 1
        job_name = f"Job_S{str(stress_ratio).replace('.', '')}_R{str(r_ratio).replace('.', '')}"
        script_name = f"model_script_S{str(stress_ratio).replace('.', '')}_R{str(r_ratio).replace('.', '')}.py"

        # Creation of the script file
        with open("picc-automate.py", "r", encoding="utf-8") as template:
            content = template.read()

        content = content.replace("{{CHARGE}}", str(charge[i]))
        content = content.replace("{{DECHARGE}}", str(decharge[i]))
        content = content.replace("{{JOBNAME}}", job_name)
        content = content.replace("{{STRESS_RATIO}}", str(stress_ratio))

        with open(script_name, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" Script generated : {script_name}")

        # Execution of the script
        exit_code = os.system(f"abaqus cae noGUI={script_name}")
        if exit_code != 0:
            print(f" Error while creating inp {job_name}.")
            continue

        exit_code_job = os.system(f"abaqus job={job_name}")
        if exit_code_job != 0:
            print(f" Error while executing {job_name}.")
            continue
        
        # Wait for the .lck file to be removed
        time.sleep(60)  
        while os.path.exists(f"{job_name}.lck"):
            print(f"Wait for the end of {job_name}...")
            time.sleep(30)

        print(f" {job_name} finished")

print(" All jobs have finished")
