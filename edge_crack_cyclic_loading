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

# Geometry
s = model.ConstrainedSketch(name='sketch', sheetSize=200.0)
s.rectangle(point1=(0.0, 0.0), point2=(width, height))

part = model.Part(name='Plate', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
part.BaseShell(sketch=s)

# PRECISE RECTANGULAR PARTITION

# Partition parameters
partition_x_start = 9.93    
partition_y_start = 0.0     
partition_width = 0.28     
partition_height = 0.07     

partition_x_end = partition_x_start + partition_width 
partition_y_end = partition_y_start + partition_height


# TRANSITION partition parameters (intermediate zone)
transition_margin = 0.15   
transition_x_start = partition_x_start - transition_margin
transition_y_start = 0.0  
transition_width = partition_width + 2 * transition_margin 
transition_height = partition_height + transition_margin    

transition_x_end = transition_x_start + transition_width
transition_y_end = transition_y_start + transition_height

# Create sketch for partitions
s_partition = model.ConstrainedSketch(name='partitionSketch', sheetSize=200.0)

# Draw fine partition rectangle

# Left vertical line transition
s_partition.Line(point1=(transition_x_start, transition_y_start), 
                 point2=(transition_x_start, transition_y_end))

# Top horizontal line transition
s_partition.Line(point1=(transition_x_start, transition_y_end), 
                 point2=(transition_x_end, transition_y_end))

# Right vertical line transition
s_partition.Line(point1=(transition_x_end, transition_y_end), 
                 point2=(transition_x_end, transition_y_start))


# Draw fine partition rectangle

# Left vertical line (x = 8mm)
s_partition.Line(point1=(partition_x_start, partition_y_start), 
                 point2=(partition_x_start, partition_y_end))

# Top horizontal line (y = 2mm)
s_partition.Line(point1=(partition_x_start, partition_y_end), 
                 point2=(partition_x_end, partition_y_end))

# Right vertical line (x = 18mm)
s_partition.Line(point1=(partition_x_end, partition_y_end), 
                 point2=(partition_x_end, partition_y_start))



# Apply partition
face_to_partition = part.faces[0]
part.PartitionFaceBySketch(faces=face_to_partition, sketch=s_partition)


# Identify created zones
zone_fine = None
zone_transition = None
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
        elif (transition_x_start <= x_center <= transition_x_end and 
              transition_y_start <= y_center <= transition_y_end):
            zone_transition = face
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

# 1. Identify horizontal and vertical edges of the rectangle
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

# 2. Apply mesh by number of elements
part.seedEdgeByNumber(edges=edges_horizontal, number=10)
part.seedEdgeByNumber(edges=edges_vertical, number=40)

# 2. TRANSITION ZONE MESH (outer rectangle) - PROGRESSIVE MESH
print("=== TRANSITION ZONE MESHING ===")
transition_horizontal_edges = []
transition_vertical_edges = []

for edge in part.edges:
    point1 = edge.pointOn[0]
    x, y = point1[0], point1[1]
    
    # Edges of TRANSITION rectangle (but NOT fine rectangle)
    in_transition = (transition_x_start - 0.001 <= x <= transition_x_end + 0.001 and
                    transition_y_start - 0.001 <= y <= transition_y_end + 0.001)
    in_fine = (partition_x_start - 0.001 <= x <= partition_x_end + 0.001 and
              partition_y_start - 0.001 <= y <= partition_y_end + 0.001)
    
    if in_transition and not in_fine:
        # Check if edge is on transition rectangle contour
        if (abs(y - transition_y_start) < 1e-3 or abs(y - transition_y_end) < 1e-3):
            transition_horizontal_edges.append(edge)
        elif (abs(x - transition_x_start) < 1e-3 or abs(x - transition_x_end) < 1e-3):
            transition_vertical_edges.append(edge)

# Calculate progressive transition mesh
transition_width_total = transition_width  
transition_height_total = transition_height 

# Transition mesh: finer than global, less fine than fine zone
num_elements_transition_h = 17 
num_elements_transition_v = 7  

# Apply transition mesh
if transition_horizontal_edges:
    part.seedEdgeByNumber(edges=transition_horizontal_edges, number=num_elements_transition_h)
    print("Transition horizontal edges: " + str(len(transition_horizontal_edges)) + " with " + str(num_elements_transition_h) + " elements")

if transition_vertical_edges:
    part.seedEdgeByNumber(edges=transition_vertical_edges, number=num_elements_transition_v)
    print("Transition vertical edges: " + str(len(transition_vertical_edges)) + " with " + str(num_elements_transition_v) + " elements")

# Mesh control and generation
part.setMeshControls(regions=part.faces, elemShape=QUAD, technique=FREE)
elemType = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD)
part.setElementType(regions=(part.faces,), elemTypes=(elemType,))
part.generateMesh()
part.SectionAssignment(region=(part.faces,), sectionName='Section')

# Assembly
assembly = model.rootAssembly
instance = assembly.Instance(name='PlateInst', part=part, dependent=ON)

# Node sets
bottom_nodes = [n for n in instance.nodes if abs(n.coordinates[1]) < 0.1]
top_nodes = [n for n in instance.nodes if abs(n.coordinates[1] - height) < 0.1]

assembly.SetFromNodeLabels(name='Bottom', nodeLabels=((instance.name, [n.label for n in bottom_nodes]),))
assembly.SetFromNodeLabels(name='Top', nodeLabels=((instance.name, [n.label for n in top_nodes]),))

# INITIAL CRACK ALREADY RELEASED AT START


# Separate nodes: initial crack vs zone to fix
initial_crack_nodes = [n for n in bottom_nodes if n.coordinates[0] <= crack_length]
initially_fixed_nodes = [n for n in bottom_nodes if n.coordinates[0] > crack_length]

# Create set for initially fixed nodes ONLY
if initially_fixed_nodes:
    assembly.SetFromNodeLabels(name='InitiallyFixed', 
                              nodeLabels=((instance.name, [n.label for n in initially_fixed_nodes]),))
    
    # Initial condition: ONLY nodes after crack are fixed
    model.DisplacementBC(name='FixedBottom', createStepName='Initial', 
                         region=assembly.sets['InitiallyFixed'], u1=0.0, u2=0.0)
    
else:
    print("ERROR: No nodes to fix initially!")

# PROGRESSIVE RELEASE WITH MULTIPLE SUB-STEPS
num_cycles = 10
max_load = 1250
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
                                  nodeLabels=((instance.name, [n.label for n in fixed_nodes]),))
    
    # ====== PHASE 1: MOUNT (5 steps) - VERY SMOOTH PROGRESSION ======
    charge_levels = [0.20, 0.40, 0.60, 0.80, 1.0]  # 20%, 40%, 60%, 80%, 100%

    for substep in range(5):
        step_name = 'Cycle-' + str(cycle+1) + '-Mount-' + str(substep+1)
        
        # Determine previous step
        if cycle == 0 and substep == 0:
            prev_step = 'Initial'
        elif substep == 0:
            prev_step = 'Cycle-' + str(cycle) + '-Descent-19'  # Last step of previous cycle
        else:
            prev_step = 'Cycle-' + str(cycle+1) + '-Mount-' + str(substep)
        
        #PARAMETERS
        model.StaticStep(name=step_name, previous=prev_step,
                         description='Cycle ' + str(cycle+1) + ' - Mount ' + str(substep+1),
                         nlgeom=ON,
                         timePeriod=6.0,         
                         initialInc=0.02,      
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
    
    # ====== PHASE 2: PLATEAU (3 steps) ======
    for substep in range(3):
        step_name = 'Cycle-' + str(cycle+1) + '-Plateau-' + str(substep+1)
        
        if substep == 0:
            prev_step = 'Cycle-' + str(cycle+1) + '-Mount-5'
        else:
            prev_step = 'Cycle-' + str(cycle+1) + '-Plateau-' + str(substep)
        
        model.StaticStep(name=step_name, previous=prev_step,
                         description='Cycle ' + str(cycle+1) + ' - Plateau ' + str(substep+1),
                         nlgeom=ON,
                         timePeriod=3.0,         
                         initialInc=0.1,      
                         maxInc=0.3,            
                         minInc=1e-10,            
                         maxNumInc=2000,
                         adaptiveDampingRatio=0.05)
        
        # Constant load at maximum
        force_per_node = max_load / len(top_nodes)
        model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                                  cf2=force_per_node)
        
        print("  Plateau " + str(substep+1) + ": " + str(max_load) + "N (100%)")
    
    # ====== PHASE 3: DESCENT (10 steps) - VERY SMOOTH PROGRESSION ======
    decharge_levels = [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05]
    
    for substep in range(19):  
        step_name = 'Cycle-' + str(cycle+1) + '-Descent-' + str(substep+1)
        
        if substep == 0:
            prev_step = 'Cycle-' + str(cycle+1) + '-Plateau-3'
        else:
            prev_step = 'Cycle-' + str(cycle+1) + '-Descent-' + str(substep)
        
        # adusted parameters for the last steps
        if substep >= 7: 
            # Paramètres ultra-conservateurs pour les derniers steps critiques
            model.StaticStep(name=step_name, previous=prev_step,
                             description='Cycle ' + str(cycle+1) + ' - Descent ' + str(substep+1),
                             nlgeom=ON,
                             timePeriod=6.0,        
                             initialInc=0.005,    
                             maxInc=0.3,              
                             minInc=1e-10,
                             maxNumInc=2000,
                             adaptiveDampingRatio=0.05,
                             stabilizationMethod=DAMPING_FACTOR,
                            stabilizationMagnitude=0.005)  
        else:
            # parameters for the first steps
            model.StaticStep(name=step_name, previous=prev_step,
                             description='Cycle ' + str(cycle+1) + ' - Descent ' + str(substep+1),
                             nlgeom=ON,
                             timePeriod=6.0,        
                             initialInc=0.02,   
                             maxInc=0.3,              
                             minInc=1e-10,
                             maxNumInc=2000,
                             adaptiveDampingRatio=0.05) 
        
        # Load reduction
        current_load = max_load * decharge_levels[substep]
        force_per_node = current_load / len(top_nodes)
        
        model.loads['CyclicLoad'].setValuesInStep(stepName=step_name,
                                                  cf2=force_per_node)
        
        print("  Descent " + str(substep+1) + ": " + str(int(current_load)) + "N (" + str(int(decharge_levels[substep]*100)) + "%)")
    
    # RELEASE AT END OF CYCLE 
    liberation_length = 0.007 
    xc = xc + liberation_length  # Advance crack
    
    print(" END CYCLE " + str(cycle+1) + ": RELEASE!")
    print("    Release: " + str(liberation_length) + "mm")
    
    # Calculate new free nodes after this cycle
    liberated_nodes = [n for n in bottom_nodes if (xc - liberation_length) < n.coordinates[0] <= xc]
    remaining_fixed = [n for n in bottom_nodes if n.coordinates[0] > xc]
    
    print("    Nodes released THIS CYCLE: " + str(len(liberated_nodes)))
    print("    Nodes remaining fixed: " + str(len(remaining_fixed)))

# Job creation
job = mdb.Job(name='SimpleCrack', model='CrackModel')
job.writeInput()

print("Model created successfully")
