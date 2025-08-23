# -*- coding: utf-8 -*-
"""
PICC Component Example
Example showing how to use individual components from the refactored structure
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

from picc_common import (
    GeometryBuilder, MaterialBuilder, MeshBuilder, 
    BoundaryConditionBuilder, CyclicLoadingBuilder,
    ContactBuilder, OutputBuilder
)

def create_simple_model():
    """Example of creating a simple model using individual components"""
    
    # Initialize Abaqus model
    Mdb()
    model = mdb.Model(name='SimpleModel')
    
    # Create geometry
    geo_builder = GeometryBuilder(model)
    plate_part = geo_builder.create_plate_part()
    master_part = geo_builder.create_master_line_part()
    
    # Create partitions for mesh refinement
    partition_params = {
        'x_start': 9.93,
        'y_start': 0.0,
        'width': 0.28,
        'height': 0.07,
        'include_transition': False  # Simple partition only
    }
    zones = geo_builder.create_partition(plate_part, partition_params)
    
    # Create materials
    mat_builder = MaterialBuilder(model)
    steel = mat_builder.create_steel_material()
    rigid_master = mat_builder.create_rigid_master_material()
    solid_section = mat_builder.create_solid_section()
    truss_section = mat_builder.create_truss_section()
    
    # Assign sections
    mat_builder.assign_section_to_part(plate_part, 'Section', 'faces')
    mat_builder.assign_section_to_part(master_part, 'MasterSection', 'edges')
    
    # Create assembly
    assembly = model.rootAssembly
    instance_main = assembly.Instance(name='PlateInst', part=plate_part, dependent=ON)
    instance_master = assembly.Instance(name='MasterInst', part=master_part, dependent=ON)
    assembly.regenerate()
    
    # Create mesh
    mesh_builder = MeshBuilder(model)
    mesh_params = {
        'global_size': 0.6,
        'fine_horizontal_elements': 5,
        'fine_vertical_elements': 20
    }
    mesh_builder.apply_mesh_to_parts(plate_part, master_part, zones, mesh_params)
    
    # Set up boundary conditions
    bc_builder = BoundaryConditionBuilder(model, assembly)
    node_sets = bc_builder.create_node_sets(instance_main, instance_master)
    bc_builder.fix_master_line()
    bc_builder.create_initial_crack_bc(instance_main, crack_length=10.0)
    
    # Set up contact
    contact_builder = ContactBuilder(model, assembly)
    contact_info = contact_builder.setup_complete_contact(instance_main, instance_master)
    
    # Create a few loading steps
    loading_builder = CyclicLoadingBuilder(model, assembly)
    max_load = 3000
    top_nodes = node_sets['top_nodes']
    
    # Create first cycle
    cycle_steps = loading_builder.create_complete_cycle(0, max_load, top_nodes)
    
    # Set up outputs
    output_builder = OutputBuilder(model, assembly)
    outputs = output_builder.create_standard_outputs(monitor_nodes=[45, 46])
    
    # Create job
    job = mdb.Job(name="SimpleModel_Job", model='SimpleModel')
    job.writeInput()
    
    print("Simple model created successfully")
    return model, job

def create_custom_loading_pattern():
    """Example of creating custom loading patterns"""
    
    # Initialize basic model (abbreviated for example)
    Mdb()
    model = mdb.Model(name='CustomLoading')
    
    # ... (geometry, materials, assembly setup - abbreviated)
    
    # Custom loading pattern
    loading_builder = CyclicLoadingBuilder(model, None)  # Assembly would be set
    
    # Custom charge/discharge levels
    custom_charge = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    custom_decharge = [0.8, 0.6, 0.4, 0.2, 0.1]
    
    # Custom step parameters for more conservative analysis
    conservative_params = {
        'time_period': 10.0,
        'initial_inc': 0.005,
        'max_inc': 0.1,
        'min_inc': 1e-12,
        'max_num_inc': 5000,
        'adaptive_damping_ratio': 0.25
    }
    
    print("Custom loading pattern example created")

if __name__ == "__main__":
    # Run the simple model example
    model, job = create_simple_model()
    
    # Show custom loading example
    create_custom_loading_pattern()