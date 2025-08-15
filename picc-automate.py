# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
from caeModules import *

# SIMPLE CRACK PROPAGATION MODEL
Mdb()
model = mdb.Model(name='CrackModel')

# Parameters
width = 50.0
height = 50.0
crack_length = 10.0

# Geometry of the first part - plate
s = model.ConstrainedSketch(name='sketch', sheetSize=200.0)
s.rectangle(point1=(0.0, 0.0), point2=(width, height))

part = model.Part(name='Plate', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
part.BaseShell(sketch=s)

# create the second part - master line

s_master = model.ConstrainedSketch(name='masterLineSketch', sheetSize=200.0)
s_master.Line(point1=(0.0, 0.0), point2=(width, 0.0)) # Horizontal line at the bottom of the rectangle

part_master = model.Part(name='MasterLine', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
part_master.BaseWire(sketch=s_master)

print(" Part master created")

# rigid material for the master line
model.Material(name='RigidMaster')
model.materials['RigidMaster'].Elastic(table=((2100000.0, 0.3),))
model.TrussSection(name='MasterSection', material='RigidMaster', area=1.0)


# PRECISE RECTANGULAR PARTITION - ZONE FINE UNIQUEMENT

# Partition parameters
partition_x_start = 9.44    
partition_y_start = 0.0     
partition_width = 2.24     
partition_height = 0.56     

partition_x_end = partition_x_start + partition_width 
partition_y_end = partition_y_start + partition_height

# Create sketch for partitions
s_partition = model.ConstrainedSketch(name='partitionSketch', sheetSize=200.0)

# Draw fine partition rectangle UNIQUEMENT

# Left vertical line (x = 9.44mm)
s_partition.Line(point1=(partition_x_start, partition_y_start), 
                 point2=(partition_x_start, partition_y_end))

# Top horizontal line (y = 0.56mm)
s_partition.Line(point1=(partition_x_start, partition_y_end), 
                 point2=(partition_x_end, partition_y_end))

# Right vertical line (x = 11.68mm)
s_partition.Line(point1=(partition_x_end, partition_y_end), 
                 point2=(partition_x_end, partition_y_start))

# Apply partition
face_to_partition = part.faces[0]
part.PartitionFaceBySketch(faces=face_to_partition, sketch=s_partition)

# Identify created zones
zone_fine = None
zones_normales = []

for i, face in enumerate(part.faces):
    try:
        center = face.pointOn[0]
        x_center = center[0]
        y_center = center[1]
        
        # Identify different zones
        if (partition_x_start <= x_center <= partition_x_end and 
            partition_y_start <= y_center <= partition_y_end):
            zone_fine = face
        else:
            zones_normales.append(face)
            
    except Exception as e:
        print("Zone " + str(i+1) + ": identification error")

# Material
model.Material(name='Steel')
model.materials['Steel'].Elastic(table=((210000.0, 0.3),))
model.materials['Steel'].Plastic(table=((250.0, 0.0), (250.0, 0.01)))
model.HomogeneousSolidSection(name='Section', material='Steel', thickness=1.0)


# ADAPTIVE MESH WITH ZONES
print("=== ADAPTIVE MESHING ===")

# Global mesh first
part.seedPart(size=0.6)  # Normal global mesh

# 1. Identify horizontal and vertical edges of the fine rectangle
edges_horizontal = []
edges_vertical = []

for edge in part.edges:
    point1 = edge.pointOn[0]
    x, y = point1[0], point1[1]
    
    # Check if edge is on partition rectangle contour
    if partition_y_start - 0.01 <= y <= partition_y_end + 0.01:
        if abs(y - partition_y_start) < 1e-3 or abs(y - partition_y_end) < 1e-3:
            edges_vertical.append(edge)

    if partition_x_start - 0.01 <= x <= partition_x_end + 0.01:
        if abs(x - partition_x_start) < 1e-3 or abs(x - partition_x_end) < 1e-3:
            edges_horizontal.append(edge)

# 2. Apply fine mesh to partition edges
part.seedEdgeByNumber(edges=edges_horizontal, number=10) 
part.seedEdgeByNumber(edges=edges_vertical, number=40) 

print("Fine mesh applied:")
print("  Horizontal edges: " + str(len(edges_horizontal)) + " with 10 elements")
print("  Vertical edges: " + str(len(edges_vertical)) + " with 40 elements")

# Mesh control and generation
part.setMeshControls(regions=part.faces, elemShape=QUAD, technique=FREE)
elemType = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD)
part.setElementType(regions=(part.faces,), elemTypes=(elemType,))
part.generateMesh()

print("=== Master line mesh ===")

part_master.seedPart(size=0.02)

elemType = mesh.ElemType(elemCode=T2D2, elemLibrary=STANDARD) 
part_master.setElementType(regions=(part_master.edges,), elemTypes=(elemType,))

part_master.generateMesh()
 
# ASSIGN SECTION TO PARTS
part.SectionAssignment(region=(part.faces,), sectionName='Section')
edgesSet = part_master.Set(name='AllEdges', edges=part_master.edges)
part_master.SectionAssignment(region=edgesSet, sectionName='MasterSection')

# ASSEMBLY 
assembly      = model.rootAssembly
instance_main = assembly.Instance(name='PlateInst',  part=part,        dependent=ON)
instance_master = assembly.Instance(name='MasterInst', part=part_master, dependent=ON)
print(" Instances créées - ligne master positionnée au bas du rectangle")

assembly.regenerate()

# CREATE CONTACT SURFACES with MASKS
edges_plate = assembly.instances['PlateInst'].edges

print("Indices et coords des edges de PlateInst :")
for idx, e in enumerate(edges_plate, start=1):
    x, y, _ = e.pointOn[0]
    print("  Edge #{:2d} → (x={:.3f}, y={:.3f})".format(idx, x, y))

bottom_idxs = [idx for idx, e in enumerate(edges_plate, start=1)
               if abs(e.pointOn[0][1]) < 1e-6]

mask_val = 0
for idx in bottom_idxs:
    mask_val |= 1 << (idx - 1)

mask_hex = format(mask_val, 'X')              
mask_str = '[#%s ]' % mask_hex

print("Utilisation du mask :", mask_str, "pour les edges", bottom_idxs)

slave_seq = edges_plate.getSequenceFromMask(mask=(mask_str,),)

# Create slave surface
assembly.Surface(name='SlaveSurface', side1Edges=slave_seq)
print("SlaveSurface edges count:", len(slave_seq))

# Create master surface from the master line
edges_master    = assembly.instances['MasterInst'].edges
master_edge_seq = edges_master.getSequenceFromMask(mask=('[#1 ]',),)
assembly.Surface(name='MasterSurface', side1Edges=master_edge_seq)
print("MasterSurface edges count:", len(master_edge_seq))

master_region = assembly.surfaces['MasterSurface']
slave_region  = assembly.surfaces['SlaveSurface']

# Contact properties
model.ContactProperty(name='CrackContact')
model.interactionProperties['CrackContact'].NormalBehavior(
    pressureOverclosure=HARD,
    constraintEnforcementMethod=PENALTY,
    contactStiffnessScaleFactor=30.0,          
    allowSeparation=ON,
    stiffnessBehavior=LINEAR
)


# Node sets
bottom_nodes = [n for n in instance_main.nodes if abs(n.coordinates[1]) < 0.1]
top_nodes = [n for n in instance_main.nodes if abs(n.coordinates[1] - height) < 0.1]
master_nodes = [n for n in instance_master.nodes]


assembly.SetFromNodeLabels(name='Bottom', nodeLabels=((instance_main.name, [n.label for n in bottom_nodes]),))
assembly.SetFromNodeLabels(name='Top', nodeLabels=((instance_main.name, [n.label for n in top_nodes]),))
assembly.SetFromNodeLabels(name='Master', nodeLabels=((instance_master.name, [n.label for n in master_nodes]),))

# Master line fixed 
model.DisplacementBC('MasterFixed', 'Initial', region=assembly.sets['Master'], u1=0.0, u2=0.0)
print("Ligne master fixée -", len(master_nodes), "nœuds")

# INITIAL CRACK ALREADY RELEASED AT START

crack_nodes          = [n for n in bottom_nodes if abs(n.coordinates[1]) < 1e-6]
initially_fixed_nodes = [n for n in crack_nodes if n.coordinates[0] > crack_length]
if initially_fixed_nodes:
    assembly.SetFromNodeLabels('InitiallyFixed',
        nodeLabels=((instance_main.name, [n.label for n in initially_fixed_nodes]),))
    model.DisplacementBC('FixedBottom', 'Initial',
                         region=assembly.sets['InitiallyFixed'], u1=0.0, u2=0.0)
else:
    print(" ERROR: No nodes to fix initially!")


# PROGRESSIVE RELEASE WITH MULTIPLE SUB-STEPS
area_force = width*1.0  # Area of the top surface (50mm x 1mm)
ratio_sigma = {{STRESS_RATIO}}
max_stress = ratio_sigma * 250.0  # Maximum stress for the load
num_cycles = 20
max_load = max_stress * area_force  # Maximum load to apply
xc = crack_length


for cycle in range(num_cycles):
    print("\n=== CYCLE " + str(cycle+1) + " ===")
    
    # Currently fixed nodes (before release of this cycle)
    fixed_nodes = [n for n in bottom_nodes if n.coordinates[0] > xc]
    
    print("Cycle " + str(cycle+1) + ": current position x = " + str(xc) + "mm")
    print("  - Nodes fixed DURING this cycle: " + str(len(fixed_nodes)))
    
    # Create set for fixed nodes of this cycle
    if fixed_nodes:
        set_name = 'Fixed-Cycle-' + str(cycle+1)
        assembly.SetFromNodeLabels(name=set_name, 
                                  nodeLabels=((instance_main.name, [n.label for n in fixed_nodes]),))
    
    # ====== PHASE 1: MOUNT (10 steps) - VERY SMOOTH PROGRESSION ======
    charge_levels = {{CHARGE}}

    for substep in range(10):  # ← Changé de 5 à 10
        step_name = 'Cycle-' + str(cycle+1) + '-Mount-' + str(substep+1)
        
        # Determine previous step
        if cycle == 0 and substep == 0:
            prev_step = 'Initial'
        elif substep == 0:
            prev_step = 'Cycle-' + str(cycle) + '-Descent-30'  
        else:
            prev_step = 'Cycle-' + str(cycle+1) + '-Mount-' + str(substep)
        
        #PARAMETERS
        model.StaticStep(name=step_name, previous=prev_step,
                         description='Cycle ' + str(cycle+1) + ' - Mount ' + str(substep+1),
                         nlgeom=ON,
                         timePeriod=6.0,         
                         initialInc=0.01,      
                         maxInc=0.3,             
                         minInc=1e-10,          
                         maxNumInc=2000,         
                         adaptiveDampingRatio=0.15)
        
        # Smoother progressive load
        current_load = max_load * charge_levels[substep]
        force_per_node = current_load / len(top_nodes)

        if substep == 0 and cycle == 0:
            # first step: create load
            model.ConcentratedForce(name='CyclicLoad', 
                               createStepName=step_name,
                               region=assembly.sets['Top'], 
                               cf2=force_per_node)
            model.SurfaceToSurfaceContactStd(
                                name='CrackClosure',
                                createStepName=step_name,
                                master=master_region,   
                                slave=slave_region,        
                                sliding=FINITE,
                                thickness=ON,
                                interactionProperty='CrackContact',
                                adjustMethod=NONE,
                                initialClearance=OMIT,
                                datumAxis=None)
        else:
            #  subsequent steps: update existing load
            model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                                  cf2=force_per_node)
        
        
        # Handle BCs at first mount substep
        if substep == 0:
            if cycle == 0:
                model.boundaryConditions['FixedBottom'].deactivate(step_name)
                print("    Initial condition deactivated")
            else:
                prev_bc_name = 'BC-Cycle-' + str(cycle)
                if prev_bc_name in model.boundaryConditions.keys():
                    model.boundaryConditions[prev_bc_name].deactivate(step_name)
                    print("    Previous cycle BC deactivated")
            
            # Create new BC FOR ENTIRE CYCLE
            if fixed_nodes:
                bc_name = 'BC-Cycle-' + str(cycle+1)
                model.DisplacementBC(name=bc_name, createStepName=step_name,
                                   region=assembly.sets[set_name], u1=0.0, u2=0.0)
                print("    New BC created: " + str(len(fixed_nodes)) + " fixed nodes")
        
        print("  Mount " + str(substep+1) + ": " + str(int(current_load)) + "N (" + str(int(charge_levels[substep]*100)) + "%)")
    
    # ====== PHASE 2: PLATEAU (1 step) ======
    step_name = 'Cycle-' + str(cycle+1) + '-Plateau-1'
    prev_step = 'Cycle-' + str(cycle+1) + '-Mount-10'

    model.StaticStep(name=step_name, previous=prev_step,
                     description='Cycle ' + str(cycle+1) + ' - Plateau',
                     nlgeom=ON,
                     timePeriod=3.0,         
                     initialInc=0.05,      
                     maxInc=0.3,            
                     minInc=1e-10,            
                     maxNumInc=2000,
                     adaptiveDampingRatio=0.05)

    # Constant load at maximum
    force_per_node = max_load / len(top_nodes)
    model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                              cf2=force_per_node)

    print("  Plateau: " + str(max_load) + "N (100%)")
    
    # ====== PHASE 3: DESCENT (30 steps) ======
    decharge_levels = {{DECHARGE}}


    for substep in range(30):
        step_name = 'Cycle-' + str(cycle+1) + '-Descent-' + str(substep+1)
        
        if substep == 0:
            prev_step = 'Cycle-' + str(cycle+1) + '-Plateau-1'  
        else:
            prev_step = 'Cycle-' + str(cycle+1) + '-Descent-' + str(substep)
        
        if substep >= 20:  
            model.StaticStep(name=step_name, previous=prev_step,
                             description='Cycle ' + str(cycle+1) + ' - Descent ' + str(substep+1),
                             nlgeom=ON,
                             timePeriod=6.0,        
                             initialInc=0.001,    
                             maxInc=0.2,              
                             minInc=1e-10,
                             maxNumInc=5000,
                             adaptiveDampingRatio=0.05,
                             stabilizationMethod=DAMPING_FACTOR,
                            stabilizationMagnitude=0.01)  
        else:
            # parameters for the first steps
            model.StaticStep(name=step_name, previous=prev_step,
                             description='Cycle ' + str(cycle+1) + ' - Descent ' + str(substep+1),
                             nlgeom=ON,
                             timePeriod=6.0,        
                             initialInc=0.02,   
                             maxInc=0.2,              
                             minInc=1e-10,
                             maxNumInc=5000,
                             adaptiveDampingRatio=0.05) 
        
        # Load reduction
        current_load = max_load * decharge_levels[substep]
        force_per_node = current_load / len(top_nodes)
        
        model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                                  cf2=force_per_node)
        
        print("  Descent " + str(substep+1) + ": " + str(int(current_load)) + "N (" + str(int(decharge_levels[substep]*100)) + "%)")
    
    # RELEASE AT END OF CYCLE 
    liberation_length = 0.056
    xc = xc + liberation_length  # Advance crack
    
    print(" END CYCLE " + str(cycle+1) + ": RELEASE!")
    print("    Release: " + str(liberation_length) + "mm")
    
    # Calculate new free nodes after this cycle
    liberated_nodes = [n for n in bottom_nodes if (xc - liberation_length) < n.coordinates[0] <= xc]
    remaining_fixed = [n for n in bottom_nodes if n.coordinates[0] > xc]
    
    print("    Nodes released THIS CYCLE: " + str(len(liberated_nodes)))
    print("    Nodes remaining fixed: " + str(len(remaining_fixed)))

#LAST CYCLE WITHOUT RELEASE
print("\n=== LAST CYCLE WITHOUT RELEASE ===")

# Redéfinir les variables nécessaires
area_force = width * 1.0
ratio_sigma = {{STRESS_RATIO}}
max_stress = ratio_sigma * 250.0
max_load = max_stress * area_force

# Définir les nœuds fixes pour le dernier cycle
fixed_nodes = [n for n in bottom_nodes if n.coordinates[0] > xc]
print("Last Cycle: current position x = " + str(xc) + "mm")
print("  - Nodes fixed DURING last cycle: " + str(len(fixed_nodes)))

# Créer l'ensemble pour les nœuds fixes du dernier cycle
if fixed_nodes:
    set_name = 'Fixed-LastCycle'
    assembly.SetFromNodeLabels(name=set_name, 
                              nodeLabels=((instance_main.name, [n.label for n in fixed_nodes]),))

# Redéfinir les niveaux de charge pour le dernier cycle
charge_levels = {{CHARGE}}
decharge_levels = {{DECHARGE}}


# ====== PHASE 1: MOUNT (10 steps) ======
for substep in range(10):
    step_name = 'LastCycle-Mount-' + str(substep+1)
    
    # Determine previous step
    if substep == 0:
        prev_step = 'Cycle-20-Descent-30'  
    else:
        prev_step = 'LastCycle-Mount-' + str(substep)
    
    # PARAMETERS
    model.StaticStep(name=step_name, previous=prev_step,
                    description='Last Cycle - Mount ' + str(substep+1),
                    nlgeom=ON,
                    timePeriod=6.0,         
                    initialInc=0.01,      
                    maxInc=0.3,             
                    minInc=1e-10,          
                    maxNumInc=2000,         
                    adaptiveDampingRatio=0.15)
    
    # Smoother progressive load
    current_load = max_load * charge_levels[substep]
    force_per_node = current_load / len(top_nodes)

    # Update existing load (pas de création, juste update)
    model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                            cf2=force_per_node)
    
    # Handle BCs at first mount substep
    if substep == 0:
        # Désactiver la BC du cycle précédent
        prev_bc_name = 'BC-Cycle-20'  # Nom explicite du dernier cycle
        if prev_bc_name in model.boundaryConditions.keys():
            model.boundaryConditions[prev_bc_name].deactivate(step_name)
            print("    Previous cycle BC deactivated")
        
        # Create new BC FOR ENTIRE LAST CYCLE
        if fixed_nodes:
            bc_name = 'BC-LastCycle'
            model.DisplacementBC(name=bc_name, createStepName=step_name,
                               region=assembly.sets[set_name], u1=0.0, u2=0.0)
            print("    New BC created: " + str(len(fixed_nodes)) + " fixed nodes")
    
    print("  Mount " + str(substep+1) + ": " + str(int(current_load)) + "N (" + str(int(charge_levels[substep]*100)) + "%)")

# ====== PHASE 2: PLATEAU (1 step) ======
step_name = 'LastCycle-Plateau-1'
prev_step = 'LastCycle-Mount-10'

model.StaticStep(name=step_name, previous=prev_step,
                description='Last Cycle - Plateau',
                nlgeom=ON,
                timePeriod=3.0,         
                initialInc=0.05,      
                maxInc=0.3,            
                minInc=1e-10,            
                maxNumInc=2000,
                adaptiveDampingRatio=0.05)

# Constant load at maximum
force_per_node = max_load / len(top_nodes)
model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                        cf2=force_per_node)

print("  Plateau: " + str(max_load) + "N (100%)")

# ====== PHASE 3: DESCENT (30 steps) ======
decharge_levels = {{DECHARGE}}


for substep in range(30):
    step_name = 'LastCycle-Descent-' + str(substep+1)
    
    if substep == 0:
        prev_step = 'LastCycle-Plateau-1'  
    else:
        prev_step = 'LastCycle-Descent-' + str(substep)
    
    if substep >= 20:  
        model.StaticStep(name=step_name, previous=prev_step,
                        description='Last Cycle - Descent ' + str(substep+1),
                        nlgeom=ON,
                        timePeriod=6.0,        
                        initialInc=0.001,    
                        maxInc=0.2,              
                        minInc=1e-10,
                        maxNumInc=5000,
                        adaptiveDampingRatio=0.05,
                        stabilizationMethod=DAMPING_FACTOR,
                        stabilizationMagnitude=0.01)  
    else:
        model.StaticStep(name=step_name, previous=prev_step,
                        description='Last Cycle - Descent ' + str(substep+1),
                        nlgeom=ON,
                        timePeriod=6.0,        
                        initialInc=0.02,   
                        maxInc=0.2,              
                        minInc=1e-10,
                        maxNumInc=5000,
                        adaptiveDampingRatio=0.05) 
    
    # Load reduction
    current_load = max_load * decharge_levels[substep]
    force_per_node = current_load / len(top_nodes)
    
    model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                            cf2=force_per_node)
    
    print("  Descent " + str(substep+1) + ": " + str(int(current_load)) + "N (" + str(int(decharge_levels[substep]*100)) + "%)")

# PAS DE RELEASE À LA FIN !
print("Last cycle completed - NO NODE RELEASE")

# History output 

# FIND THE BOTTOM-LEFT NODE
bottom_left_node = None
min_distance = float('inf')

for node in instance_main.nodes:
    x, y = node.coordinates[0], node.coordinates[1]
    # Calculate distance from origin (0,0)
    distance = (x**2 + y**2)**0.5
    if distance < min_distance:
        min_distance = distance
        bottom_left_node = node

if bottom_left_node:    
    assembly.SetFromNodeLabels('BottomLeftNode', 
                              nodeLabels=((instance_main.name, [bottom_left_node.label]),))
else:
    print(" ERROR: No bottom-left node found")


# History output for the bottom-left node displacement
regionDef = model.rootAssembly.sets['BottomLeftNode']
model.HistoryOutputRequest(name='H-Output-Displacement', 
                          createStepName='Cycle-1-Mount-1',
                          variables=('U2',),  # vertical displacement
                          region=regionDef,
                          sectionPoints=DEFAULT,
                          rebar=EXCLUDE)

#  History output for the top surface force
regionDef_top = model.rootAssembly.sets['Top']
model.HistoryOutputRequest(name='H-Output-Force', 
                          createStepName='Cycle-1-Mount-1',
                          variables=('CF2',),  # vertical force
                          region=regionDef_top,
                          sectionPoints=DEFAULT,
                          rebar=EXCLUDE)

# Créer des ensembles pour les nœuds 45, 46, 47
assembly.SetFromNodeLabels(name='Node47', nodeLabels=((instance_main.name, [47]),))
assembly.SetFromNodeLabels(name='Node46', nodeLabels=((instance_main.name, [46]),))
assembly.SetFromNodeLabels(name='Node45', nodeLabels=((instance_main.name, [45]),))

# Ajouter des requêtes de History Output pour U2 (déplacement vertical) de chaque nœud
regionDef_node47 = model.rootAssembly.sets['Node47']
model.HistoryOutputRequest(name='H-Output-Node47', 
                          createStepName='Cycle-1-Mount-1',
                          variables=('U2',),  # Déplacement vertical
                          region=regionDef_node47,
                          sectionPoints=DEFAULT,
                          rebar=EXCLUDE)

regionDef_node46 = model.rootAssembly.sets['Node46']
model.HistoryOutputRequest(name='H-Output-Node46', 
                          createStepName='Cycle-1-Mount-1',
                          variables=('U2',),  # Déplacement vertical
                          region=regionDef_node46,
                          sectionPoints=DEFAULT,
                          rebar=EXCLUDE)

regionDef_node45 = model.rootAssembly.sets['Node45']
model.HistoryOutputRequest(name='H-Output-Node45', 
                          createStepName='Cycle-1-Mount-1',
                          variables=('U2',),  # Déplacement vertical
                          region=regionDef_node45,
                          sectionPoints=DEFAULT,
                          rebar=EXCLUDE)



# History output pour déplacements des nœuds du haut
model.HistoryOutputRequest(name='H-Output-TopDisplacement', 
                          createStepName='Cycle-1-Mount-1',
                          variables=('U2',),
                          region=assembly.sets['Top'],
                          sectionPoints=DEFAULT,
                          rebar=EXCLUDE)

# Field outputs optimaux pour crack-closure
model.FieldOutputRequest(name='F-Output-Complete', 
                        createStepName='Cycle-1-Mount-1',
                        variables=('CSTATUS', 'PEEQ', 'U', 'S'))



# Field outputs pour TOUS les steps du dernier cycle
last_cycle_steps = [
    'LastCycle-Mount-1', 'LastCycle-Mount-5', 'LastCycle-Mount-10',
    'LastCycle-Plateau-1',
    'LastCycle-Descent-1', 'LastCycle-Descent-10', 'LastCycle-Descent-20', 'LastCycle-Descent-30'
]

for step_name in last_cycle_steps:
    try:
        model.fieldOutputRequests['F-Output-Complete'].setValuesInStep(
            stepName=step_name, variables=('CSTATUS', 'PEEQ', 'U', 'S'))
    except:
        print("⚠️  Step non trouvé: " + step_name)

print("History outputs created")
print("Maximal stress:" + str(max_stress) + "MPa")
print("Model created successfully")

# Job creation
job = mdb.Job(name="{{JOBNAME}}", model='CrackModel')
job.writeInput()
