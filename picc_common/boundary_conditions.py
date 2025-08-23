# -*- coding: utf-8 -*-
"""
Boundary Conditions Builder Module for PICC Study
Handles creation of boundary conditions and node sets
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *


class BoundaryConditionBuilder:
    """Builder class for creating boundary conditions in PICC models"""
    
    def __init__(self, model, assembly):
        """
        Initialize boundary conditions builder
        
        Args:
            model: Abaqus model object
            assembly: Assembly object
        """
        self.model = model
        self.assembly = assembly
        
    def create_node_sets(self, instance_main, instance_master, height=50.0):
        """
        Create node sets for boundary conditions
        
        Args:
            instance_main: Main plate instance
            instance_master: Master line instance  
            height: Plate height for identifying top nodes
            
        Returns:
            Dictionary with node sets information
        """
        # Identify nodes
        bottom_nodes = [n for n in instance_main.nodes if abs(n.coordinates[1]) < 0.1]
        top_nodes = [n for n in instance_main.nodes if abs(n.coordinates[1] - height) < 0.1]
        master_nodes = [n for n in instance_master.nodes]
        
        # Create node sets
        self.assembly.SetFromNodeLabels(
            name='Bottom', 
            nodeLabels=((instance_main.name, [n.label for n in bottom_nodes]),)
        )
        
        self.assembly.SetFromNodeLabels(
            name='Top', 
            nodeLabels=((instance_main.name, [n.label for n in top_nodes]),)
        )
        
        self.assembly.SetFromNodeLabels(
            name='Master', 
            nodeLabels=((instance_master.name, [n.label for n in master_nodes]),)
        )
        
        print(f"Created node sets:")
        print(f"  Bottom: {len(bottom_nodes)} nodes")
        print(f"  Top: {len(top_nodes)} nodes") 
        print(f"  Master: {len(master_nodes)} nodes")
        
        return {
            'bottom_nodes': bottom_nodes,
            'top_nodes': top_nodes,
            'master_nodes': master_nodes
        }
        
    def fix_master_line(self, step_name='Initial'):
        """
        Fix master line nodes (both U1 and U2)
        
        Args:
            step_name: Step name for boundary condition
            
        Returns:
            Created boundary condition
        """
        bc = self.model.DisplacementBC(
            'MasterFixed', 
            step_name, 
            region=self.assembly.sets['Master'], 
            u1=0.0, 
            u2=0.0
        )
        
        print("Master line fixed (U1=U2=0)")
        return bc
        
    def create_initial_crack_bc(self, instance_main, crack_length=10.0, 
                              step_name='Initial'):
        """
        Create boundary conditions for initial crack
        
        Args:
            instance_main: Main plate instance
            crack_length: Length of initial crack
            step_name: Step name for boundary condition
            
        Returns:
            Created boundary condition or None
        """
        # Find crack nodes (bottom nodes beyond crack length)
        crack_nodes = [n for n in instance_main.nodes if abs(n.coordinates[1]) < 1e-6]
        initially_fixed_nodes = [n for n in crack_nodes if n.coordinates[0] > crack_length]
        
        if initially_fixed_nodes:
            # Create node set
            self.assembly.SetFromNodeLabels(
                'InitiallyFixed',
                nodeLabels=((instance_main.name, [n.label for n in initially_fixed_nodes]),)
            )
            
            # Create boundary condition
            bc = self.model.DisplacementBC(
                'FixedBottom', 
                step_name,
                region=self.assembly.sets['InitiallyFixed'], 
                u1=0.0, 
                u2=0.0
            )
            
            print(f"Initial crack BC created: {len(initially_fixed_nodes)} nodes fixed")
            return bc
            
        else:
            print("No nodes found for initial crack BC")
            return None
            
    def create_crack_release_bc(self, instance_main, fixed_nodes, cycle, 
                              step_name, set_name_prefix='Fixed'):
        """
        Create boundary condition for crack release
        
        Args:
            instance_main: Main plate instance
            fixed_nodes: List of nodes to fix
            cycle: Cycle number
            step_name: Step name for boundary condition
            set_name_prefix: Prefix for set name
            
        Returns:
            Created boundary condition or None
        """
        if not fixed_nodes:
            return None
            
        set_name = f'{set_name_prefix}-Cycle-{cycle}'
        
        # Create node set
        self.assembly.SetFromNodeLabels(
            name=set_name,
            nodeLabels=((instance_main.name, [n.label for n in fixed_nodes]),)
        )
        
        # Create boundary condition
        bc_name = f'BC-Cycle-{cycle}'
        bc = self.model.DisplacementBC(
            bc_name, 
            step_name,
            region=self.assembly.sets[set_name], 
            u1=0.0, 
            u2=0.0
        )
        
        print(f"Crack release BC '{bc_name}' created: {len(fixed_nodes)} nodes fixed")
        return bc
        
    def deactivate_boundary_condition(self, bc_name, step_name):
        """
        Deactivate boundary condition in a step
        
        Args:
            bc_name: Name of boundary condition to deactivate
            step_name: Step name where to deactivate
            
        Returns:
            Success status
        """
        try:
            if bc_name in self.model.boundaryConditions.keys():
                self.model.boundaryConditions[bc_name].deactivate(step_name)
                print(f"Boundary condition '{bc_name}' deactivated in step '{step_name}'")
                return True
            else:
                print(f"Boundary condition '{bc_name}' not found")
                return False
        except Exception as e:
            print(f"Error deactivating BC '{bc_name}': {e}")
            return False
            
    def create_node_monitoring_sets(self, instance_main, node_labels):
        """
        Create node sets for monitoring specific nodes
        
        Args:
            instance_main: Main plate instance
            node_labels: List of node labels to monitor
            
        Returns:
            List of created set names
        """
        set_names = []
        
        for label in node_labels:
            set_name = f'Node{label}'
            self.assembly.SetFromNodeLabels(
                name=set_name, 
                nodeLabels=((instance_main.name, [label]),)
            )
            set_names.append(set_name)
            
        print(f"Created monitoring sets for nodes: {node_labels}")
        return set_names