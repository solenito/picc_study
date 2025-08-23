# -*- coding: utf-8 -*-
"""
Output Builder Module for PICC Study
Handles creation of history and field output requests
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *


class OutputBuilder:
    """Builder class for creating output requests in PICC models"""
    
    def __init__(self, model, assembly):
        """
        Initialize output builder
        
        Args:
            model: Abaqus model object
            assembly: Assembly object
        """
        self.model = model
        self.assembly = assembly
        
    def create_displacement_history_output(self, region_name, output_name,
                                         create_step='Cycle-1-Mount-1'):
        """
        Create history output for displacements
        
        Args:
            region_name: Name of region/set for output
            output_name: Name for the output request
            create_step: Step where output is created
            
        Returns:
            Created history output request
        """
        region_def = self.assembly.sets[region_name]
        
        output_request = self.model.HistoryOutputRequest(
            name=output_name,
            createStepName=create_step,
            variables=('U2',),  # Vertical displacement
            region=region_def,
            sectionPoints=DEFAULT,
            rebar=EXCLUDE
        )
        
        print(f"Created displacement history output '{output_name}' for region '{region_name}'")
        return output_request
        
    def create_force_history_output(self, region_name, output_name,
                                   create_step='Cycle-1-Mount-1'):
        """
        Create history output for forces
        
        Args:
            region_name: Name of region/set for output
            output_name: Name for the output request
            create_step: Step where output is created
            
        Returns:
            Created history output request
        """
        region_def = self.assembly.sets[region_name]
        
        output_request = self.model.HistoryOutputRequest(
            name=output_name,
            createStepName=create_step,
            variables=('CF2',),  # Vertical force
            region=region_def,
            sectionPoints=DEFAULT,
            rebar=EXCLUDE
        )
        
        print(f"Created force history output '{output_name}' for region '{region_name}'")
        return output_request
        
    def create_node_monitoring_outputs(self, node_labels, instance_name,
                                     create_step='Cycle-1-Mount-1'):
        """
        Create history outputs for monitoring specific nodes
        
        Args:
            node_labels: List of node labels to monitor
            instance_name: Name of instance containing the nodes
            create_step: Step where outputs are created
            
        Returns:
            List of created output request names
        """
        output_names = []
        
        for label in node_labels:
            set_name = f'Node{label}'
            output_name = f'H-Output-Node{label}'
            
            # Create node set if it doesn't exist
            if set_name not in self.assembly.sets.keys():
                self.assembly.SetFromNodeLabels(
                    name=set_name,
                    nodeLabels=((instance_name, [label]),)
                )
                
            # Create history output
            self.create_displacement_history_output(set_name, output_name, create_step)
            output_names.append(output_name)
            
        print(f"Created node monitoring outputs for nodes: {node_labels}")
        return output_names
        
    def create_field_output(self, output_name='F-Output-Complete',
                          create_step='Cycle-1-Mount-1',
                          variables=None):
        """
        Create field output request
        
        Args:
            output_name: Name for the output request
            create_step: Step where output is created
            variables: Tuple of variables to output
            
        Returns:
            Created field output request
        """
        if variables is None:
            variables = ('CSTATUS', 'PEEQ', 'U', 'S')  # Standard variables for crack analysis
            
        output_request = self.model.FieldOutputRequest(
            name=output_name,
            createStepName=create_step,
            variables=variables
        )
        
        print(f"Created field output '{output_name}' with variables: {variables}")
        return output_request
        
    def create_step_specific_field_outputs(self, step_names, output_name_prefix='F-Output'):
        """
        Create field outputs for specific steps
        
        Args:
            step_names: List of step names for field output
            output_name_prefix: Prefix for output names
            
        Returns:
            List of created output request names
        """
        output_names = []
        
        for step_name in step_names:
            output_name = f'{output_name_prefix}-{step_name}'
            
            # Create field output for this step
            self.model.FieldOutputRequest(
                name=output_name,
                createStepName=step_name,
                variables=('CSTATUS', 'PEEQ', 'U', 'S')
            )
            
            output_names.append(output_name)
            
        print(f"Created {len(output_names)} step-specific field outputs")
        return output_names
        
    def create_standard_outputs(self, monitor_nodes=None, 
                              last_cycle_steps=None,
                              create_step='Cycle-1-Mount-1'):
        """
        Create standard set of outputs for PICC study
        
        Args:
            monitor_nodes: List of node labels to monitor (default: [44, 45, 46, 47])
            last_cycle_steps: List of last cycle step names for field output
            create_step: Step where outputs are created
            
        Returns:
            Dictionary with created outputs information
        """
        if monitor_nodes is None:
            monitor_nodes = [44, 45, 46, 47]
            
        print("=== CREATING STANDARD OUTPUTS ===")
        
        # History outputs for displacements and forces
        displacement_output = self.create_displacement_history_output(
            'Top', 'H-Output-TopDisplacement', create_step
        )
        
        force_output = self.create_force_history_output(
            'Top', 'H-Output-Force', create_step
        )
        
        # Node monitoring outputs
        node_outputs = []
        if monitor_nodes:
            # Get instance name (assuming 'PlateInst' for main instance)
            instance_name = 'PlateInst'
            node_outputs = self.create_node_monitoring_outputs(
                monitor_nodes, instance_name, create_step
            )
            
        # Field outputs
        field_output = self.create_field_output(create_step=create_step)
        
        # Last cycle field outputs
        last_cycle_outputs = []
        if last_cycle_steps:
            last_cycle_outputs = self.create_step_specific_field_outputs(
                last_cycle_steps, 'F-Output-LastCycle'
            )
            
        outputs_info = {
            'displacement': displacement_output,
            'force': force_output,
            'node_monitoring': node_outputs,
            'field': field_output,
            'last_cycle_fields': last_cycle_outputs
        }
        
        print("Standard outputs created successfully")
        return outputs_info