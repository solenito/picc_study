import os
import time

# Liste des valeurs de ton paramètre (ex: charge)

charge_levels0 = [0.0, 0.11, 0.22, 0.33, 0.44, 0.56, 0.67, 0.78, 0.89, 1.0] #r ratio = 0.0
    
charge_levels1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] #r ratio = 0.1    
    
charge_levels2 = [0.2, 0.29, 0.38, 0.47, 0.56, 0.64, 0.73, 0.82, 0.91, 1.0] #r ratio = 0.2

charge_levels3 = [0.3, 0.38, 0.47, 0.55, 0.63, 0.72, 0.8, 0.88, 0.97, 1.0] #r ratio = 0.3

charge_levels4 = [0.4, 0.47, 0.53, 0.6, 0.67, 0.73, 0.8, 0.87, 0.93, 1.0] #r ratio = 0.4

charge_levels5 = [0.5, 0.56, 0.61, 0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0] #r ratio = 0.5



decharge_levels0 = [0.97, 0.93, 0.90, 0.87, 0.83, 0.80, 0.77, 0.73, 0.70, 0.67,  
                       0.63, 0.60, 0.57, 0.53, 0.50, 0.47, 0.43, 0.40, 0.37, 0.33,  
                       0.30, 0.27, 0.23, 0.20, 0.17, 0.13, 0.10, 0.07, 0.03, 0.00] #r ratio = 0.

decharge_levels1 = [1.0, 0.97, 0.93, 0.9, 0.86, 0.83, 0.79, 0.76, 0.72, 0.69,
                        0.66, 0.62, 0.59, 0.55, 0.52, 0.48, 0.45, 0.41, 0.38, 0.34,
                        0.31, 0.28, 0.24, 0.21, 0.19, 0.17, 0.15, 0.13, 0.11, 0.1] #r ratio = 0.1 


decharge_levels2 = [1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82, 0.79, 0.76, 0.73,
                     0.7, 0.67, 0.64, 0.61, 0.58, 0.55, 0.52, 0.49, 0.46, 0.43,
                     0.4, 0.37, 0.34, 0.31, 0.28, 0.25, 0.22, 0.19, 0.16, 0.2] #r ratio = 0.2


decharge_levels3 = [1.0, 0.97, 0.95, 0.93, 0.9, 0.88, 0.86, 0.83, 0.81, 0.79,
                       0.76, 0.74, 0.72, 0.69, 0.67, 0.65, 0.62, 0.6, 0.58, 0.55,
                       0.53, 0.51, 0.48, 0.46, 0.44, 0.41, 0.39, 0.37, 0.34, 0.32] #r ratio = 0.3''' 
    
     
decharge_levels4 = [1.0, 0.98, 0.96, 0.94, 0.92, 0.9, 0.88, 0.86, 0.84, 0.82,
                        0.8, 0.78, 0.76, 0.74, 0.72, 0.7, 0.68, 0.66, 0.64, 0.62,
                        0.6, 0.58, 0.56, 0.54, 0.52, 0.5, 0.48, 0.46, 0.44, 0.4] #r ratio = 0.4

decharge_levels5 = [1.0, 0.98, 0.97, 0.95, 0.93, 0.91, 0.9, 0.88, 0.86, 0.84,
                        0.83, 0.81, 0.79, 0.78, 0.76, 0.74, 0.72, 0.71, 0.69, 0.67,
                        0.66, 0.64, 0.62, 0.6, 0.59, 0.57, 0.55, 0.53, 0.52, 0.5] #r ratio = 0.5

charge = [charge_levels0, charge_levels1, charge_levels2, charge_levels3, charge_levels4, charge_levels5]

decharge = [decharge_levels0, decharge_levels1, decharge_levels2, decharge_levels3, decharge_levels4, decharge_levels5]

for i, load in enumerate(charge):
    job_name = f"Job_R{i*0.1:.1f}"  
    script_name = f"model_script_R{i*0.1:.1f}.py"

    # Crée un nouveau script avec le bon paramètre
    with open("picc-v2.py", "r") as template:
        content = template.read()

    content = content.replace("{{CHARGE}}", str(charge[i]))
    content = content.replace("{{DECHARGE}}", str(decharge[i]))
    content = content.replace("{{JOBNAME}}", job_name)

    with open(script_name, "w") as f:
        f.write(content)
    
        print(f" Lancement de {job_name}...")

    # Lancer le job Abaqus
    os.system(f"abaqus cae noGUI={script_name}")

    # Attendre que le fichier .lck disparaisse (le job est fini)
    while os.path.exists(f"{job_name}.lck"):
        print(f"Attente de fin pour {job_name}...")
        time.sleep(30)

    print(f"✅ {job_name} terminé.")

print(" Tous les jobs sont terminés.")
