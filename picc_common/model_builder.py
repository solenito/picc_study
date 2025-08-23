# -*- coding: utf-8 -*-
"""
Model Builder Module for PICC Study
Main orchestrator for building complete PICC models
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

from .geometry import GeometryBuilder
from .materials import MaterialBuilder
from .mesh import MeshBuilder
from .boundary_conditions import BoundaryConditionBuilder
from .cyclic_loading import CyclicLoadingBuilder
from .contact import ContactBuilder
from .outputs import OutputBuilder


class PICCModelBuilder:
    """Main builder class for creating complete PICC models"""
    
    def __init__(self, model_name='CrackModel'):
        """
        Initialize PICC model builder
        
        Args:
            model_name: Name for the Abaqus model
        """
        # Initialize Abaqus model
        Mdb()
        self.model = mdb.Model(name=model_name)
        self.assembly = None
        
        # Initialize builders
        self.geometry_builder = GeometryBuilder(self.model)
        self.materials_builder = MaterialBuilder(self.model)
        self.mesh_builder = MeshBuilder(self.model)
        
        # These will be initialized after assembly creation
        self.bc_builder = None
        self.loading_builder = None
        self.contact_builder = None
        self.output_builder = None
        
        # Store created components
        self.parts = {}
        self.instances = {}
        self.zones = {}
        self.node_sets = {}
        
        print(f"Initialized PICC model builder for model '{model_name}'")
        
    def create_geometry(self, geometry_params=None):
        """
        Create geometry components
        
        Args:
            geometry_params: Dictionary with geometry parameters
                - width: Plate width
                - height: Plate height
                - crack_length: Initial crack length
                - partition_params: Partition parameters
                
        Returns:
            Dictionary with created parts
        """
        if geometry_params is None:
            geometry_params = {
                'width': 50.0,
                'height': 50.0,
                'crack_length': 10.0
            }
            
        print("=== CREATING GEOMETRY ===")
        
        # Update builder parameters
        self.geometry_builder.width = geometry_params.get('width', 50.0)
        self.geometry_builder.height = geometry_params.get('height', 50.0)
        self.geometry_builder.crack_length = geometry_params.get('crack_length', 10.0)
        
        # Create parts
        self.parts['plate'] = self.geometry_builder.create_plate_part()
        self.parts['master_line'] = self.geometry_builder.create_master_line_part()
        
        # Create partitions if requested
        partition_params = geometry_params.get('partition_params')
        if partition_params:
            self.zones = self.geometry_builder.create_partition(
                self.parts['plate'], partition_params
            )
            
        return self.parts
        
    def create_materials(self):
        """
        Create materials and sections
        
        Returns:
            Dictionary with created materials and sections
        """
        print("=== CREATING MATERIALS ===")
        
        materials_sections = self.materials_builder.create_standard_materials()
        
        # Assign sections to parts
        self.materials_builder.assign_section_to_part(
            self.parts['plate'], 'Section', 'faces'
        )
        self.materials_builder.assign_section_to_part(
            self.parts['master_line'], 'MasterSection', 'edges'
        )
        
        return materials_sections
        
    def create_assembly(self):
        """
        Create assembly with instances
        
        Returns:
            Assembly object
        """
        print("=== CREATING ASSEMBLY ===")
        
        self.assembly = self.model.rootAssembly
        
        # Create instances
        self.instances['main'] = self.assembly.Instance(
            name='PlateInst', 
            part=self.parts['plate'], 
            dependent=ON
        )
        self.instances['master'] = self.assembly.Instance(
            name='MasterInst', 
            part=self.parts['master_line'], 
            dependent=ON
        )
        
        self.assembly.regenerate()
        
        print("Instances created - master line positioned at bottom of rectangle")
        
        # Initialize remaining builders now that assembly exists
        self.bc_builder = BoundaryConditionBuilder(self.model, self.assembly)
        self.loading_builder = CyclicLoadingBuilder(self.model, self.assembly)
        self.contact_builder = ContactBuilder(self.model, self.assembly)
        self.output_builder = OutputBuilder(self.model, self.assembly)
        
        return self.assembly
        
    def create_mesh(self, mesh_params=None):
        """
        Create mesh for all parts
        
        Args:
            mesh_params: Dictionary with mesh parameters
            
        Returns:
            None
        """
        print("=== CREATING MESH ===")
        
        # Apply mesh to parts
        self.mesh_builder.apply_mesh_to_parts(
            self.parts['plate'], 
            self.parts['master_line'],
            self.zones,
            mesh_params
        )
        
    def setup_boundary_conditions(self, crack_length=None):
        """
        Set up boundary conditions
        
        Args:
            crack_length: Initial crack length
            
        Returns:
            Dictionary with node sets and boundary conditions
        """
        if crack_length is None:
            crack_length = self.geometry_builder.crack_length
            
        print("=== SETTING UP BOUNDARY CONDITIONS ===")
        
        # Create node sets
        self.node_sets = self.bc_builder.create_node_sets(
            self.instances['main'], 
            self.instances['master']
        )
        
        # Fix master line
        self.bc_builder.fix_master_line()
        
        # Create initial crack boundary condition
        self.bc_builder.create_initial_crack_bc(
            self.instances['main'], 
            crack_length
        )
        
        return self.node_sets
        
    def setup_contact(self, contact_stiffness_scale=30.0):
        """
        Set up contact between crack faces
        
        Args:
            contact_stiffness_scale: Contact stiffness scale factor
            
        Returns:
            Dictionary with contact setup information
        """
        print("=== SETTING UP CONTACT ===")
        
        contact_info = self.contact_builder.setup_complete_contact(
            self.instances['main'],
            self.instances['master'],
            contact_stiffness_scale
        )
        
        return contact_info
        
    def create_cyclic_loading(self, num_cycles, max_load, loading_params=None):
        """
        Create cyclic loading for specified number of cycles
        
        Args:
            num_cycles: Number of cycles to create
            max_load: Maximum load value
            loading_params: Dictionary with loading parameters
            
        Returns:
            Dictionary with step information for all cycles
        """
        print(f"=== CREATING CYCLIC LOADING ({num_cycles} CYCLES) ===")
        
        all_cycles = {}
        
        for cycle in range(num_cycles):
            cycle_steps = self.loading_builder.create_complete_cycle(
                cycle,
                max_load,
                self.node_sets['top_nodes'],
                **loading_params if loading_params else {}
            )
            all_cycles[f'cycle_{cycle+1}'] = cycle_steps
            
        return all_cycles
        
    def setup_outputs(self, monitor_nodes=None, last_cycle_steps=None):
        """
        Set up output requests
        
        Args:
            monitor_nodes: List of node labels to monitor
            last_cycle_steps: List of last cycle step names
            
        Returns:
            Dictionary with output information
        """
        print("=== SETTING UP OUTPUTS ===")
        
        outputs_info = self.output_builder.create_standard_outputs(
            monitor_nodes,
            last_cycle_steps
        )
        
        return outputs_info
        
    def build_complete_model(self, config=None):
        """
        Build complete PICC model with all components
        
        Args:
            config: Dictionary with complete model configuration
                - geometry_params: Geometry parameters
                - mesh_params: Mesh parameters  
                - num_cycles: Number of cycles
                - max_load: Maximum load
                - loading_params: Loading parameters
                - contact_stiffness_scale: Contact stiffness scale
                - monitor_nodes: Nodes to monitor
                
        Returns:
            Dictionary with complete model information
        """
        if config is None:
            config = {
                'geometry_params': {
                    'width': 50.0,
                    'height': 50.0,
                    'crack_length': 10.0,
                    'partition_params': {
                        'x_start': 9.93,
                        'y_start': 0.0,
                        'width': 0.28,
                        'height': 0.07,
                        'include_transition': True,
                        'transition_margin': 0.15
                    }
                },
                'num_cycles': 20,
                'max_load': 5000,
                'contact_stiffness_scale': 30.0,
                'monitor_nodes': [44, 45, 46, 47]
            }
            
        print("=== BUILDING COMPLETE PICC MODEL ===")
        
        # Build model step by step
        parts = self.create_geometry(config.get('geometry_params'))
        materials = self.create_materials()
        assembly = self.create_assembly()
        self.create_mesh(config.get('mesh_params'))
        node_sets = self.setup_boundary_conditions(
            config.get('geometry_params', {}).get('crack_length')
        )
        contact_info = self.setup_contact(config.get('contact_stiffness_scale', 30.0))
        
        # Create loading cycles
        cycles = self.create_cyclic_loading(
            config.get('num_cycles', 20),
            config.get('max_load', 5000),
            config.get('loading_params')
        )
        
        # Set up outputs
        outputs = self.setup_outputs(
            config.get('monitor_nodes'),
            config.get('last_cycle_steps')
        )
        
        model_info = {
            'parts': parts,
            'materials': materials,
            'assembly': assembly,
            'node_sets': node_sets,
            'contact': contact_info,
            'cycles': cycles,
            'outputs': outputs
        }
        
        print("=== PICC MODEL BUILD COMPLETED ===")
        return model_info
        
    def create_job(self, job_name="PICC_Job"):
        """
        Create job for the model
        
        Args:
            job_name: Name for the job
            
        Returns:
            Created job object
        """
        job = mdb.Job(name=job_name, model=self.model.name)
        job.writeInput()
        
        print(f"Job '{job_name}' created and input file written")
        return job