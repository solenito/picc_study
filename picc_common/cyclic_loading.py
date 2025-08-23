# -*- coding: utf-8 -*-
"""
Cyclic Loading Builder Module for PICC Study
Handles creation of cyclic loading patterns and steps
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *


class CyclicLoadingBuilder:
    """Builder class for creating cyclic loading in PICC models"""
    
    def __init__(self, model, assembly):
        """
        Initialize cyclic loading builder
        
        Args:
            model: Abaqus model object
            assembly: Assembly object
        """
        self.model = model
        self.assembly = assembly
        
    def get_standard_charge_levels(self):
        """
        Get standard charge levels for loading phase
        
        Returns:
            List of charge level multipliers (0.0 to 1.0)
        """
        return [0.20, 0.40, 0.60, 0.80, 1.00]
        
    def get_standard_decharge_levels(self):
        """
        Get standard discharge levels for unloading phase
        
        Returns:
            List of discharge level multipliers (1.0 to 0.05)
        """
        return [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50, 
                0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05]
                
    def create_loading_steps(self, cycle, max_load, top_nodes, 
                           charge_levels=None, step_params=None):
        """
        Create loading steps for a cycle
        
        Args:
            cycle: Cycle number (0-based)
            max_load: Maximum load value
            top_nodes: List of top nodes for load application
            charge_levels: List of charge level multipliers
            step_params: Dictionary with step parameters
            
        Returns:
            List of created step names
        """
        if charge_levels is None:
            charge_levels = self.get_standard_charge_levels()
            
        if step_params is None:
            step_params = {
                'time_period': 6.0,
                'initial_inc': 0.01,
                'max_inc': 0.3,
                'min_inc': 1e-10,
                'max_num_inc': 2000,
                'adaptive_damping_ratio': 0.15
            }
            
        step_names = []
        
        for substep in range(len(charge_levels)):
            step_name = f'Cycle-{cycle+1}-Mount-{substep+1}'
            
            # Determine previous step
            if cycle == 0 and substep == 0:
                prev_step = 'Initial'
            elif substep == 0:
                prev_step = f'Cycle-{cycle}-Descent-{len(self.get_standard_decharge_levels())}'
            else:
                prev_step = f'Cycle-{cycle+1}-Mount-{substep}'
                
            # Create step
            self.model.StaticStep(
                name=step_name, 
                previous=prev_step,
                description=f'Cycle {cycle+1} - Mount {substep+1}',
                nlgeom=ON,
                timePeriod=step_params['time_period'],
                initialInc=step_params['initial_inc'],
                maxInc=step_params['max_inc'],
                minInc=step_params['min_inc'],
                maxNumInc=step_params['max_num_inc'],
                adaptiveDampingRatio=step_params['adaptive_damping_ratio']
            )
            
            # Calculate load
            current_load = max_load * charge_levels[substep]
            force_per_node = current_load / len(top_nodes)
            
            # Apply load
            if cycle == 0 and substep == 0:
                # First step: create load
                self.model.ConcentratedForce(
                    name='CyclicLoad',
                    createStepName=step_name,
                    region=self.assembly.sets['Top'],
                    cf2=force_per_node
                )
            else:
                # Update existing load
                self.model.loads['CyclicLoad'].setValuesInStep(
                    stepName=step_name,
                    cf2=force_per_node
                )
                
            step_names.append(step_name)
            print(f"  Mount {substep+1}: {int(current_load)}N "
                  f"({int(charge_levels[substep]*100)}%)")
                  
        return step_names
        
    def create_plateau_steps(self, cycle, max_load, top_nodes, 
                           num_steps=3, step_params=None):
        """
        Create plateau steps for a cycle
        
        Args:
            cycle: Cycle number (0-based)
            max_load: Maximum load value
            top_nodes: List of top nodes
            num_steps: Number of plateau steps
            step_params: Dictionary with step parameters
            
        Returns:
            List of created step names
        """
        if step_params is None:
            step_params = {
                'time_period': 6.0,
                'initial_inc': 0.01,
                'max_inc': 0.3,
                'min_inc': 1e-10,
                'max_num_inc': 2000,
                'adaptive_damping_ratio': 0.15
            }
            
        step_names = []
        force_per_node = max_load / len(top_nodes)
        
        for substep in range(num_steps):
            step_name = f'Cycle-{cycle+1}-Plateau-{substep+1}'
            
            # Determine previous step
            if substep == 0:
                prev_step = f'Cycle-{cycle+1}-Mount-{len(self.get_standard_charge_levels())}'
            else:
                prev_step = f'Cycle-{cycle+1}-Plateau-{substep}'
                
            # Create step
            self.model.StaticStep(
                name=step_name,
                previous=prev_step,
                description=f'Cycle {cycle+1} - Plateau {substep+1}',
                nlgeom=ON,
                timePeriod=step_params['time_period'],
                initialInc=step_params['initial_inc'],
                maxInc=step_params['max_inc'],
                minInc=step_params['min_inc'],
                maxNumInc=step_params['max_num_inc'],
                adaptiveDampingRatio=step_params['adaptive_damping_ratio']
            )
            
            # Maintain maximum load
            self.model.loads['CyclicLoad'].setValuesInStep(
                stepName=step_name,
                cf2=force_per_node
            )
            
            step_names.append(step_name)
            
        print(f"  Plateau: {num_steps} steps at {int(max_load)}N")
        return step_names
        
    def create_unloading_steps(self, cycle, max_load, top_nodes,
                             decharge_levels=None, step_params=None):
        """
        Create unloading steps for a cycle
        
        Args:
            cycle: Cycle number (0-based)
            max_load: Maximum load value
            top_nodes: List of top nodes
            decharge_levels: List of discharge level multipliers
            step_params: Dictionary with step parameters
            
        Returns:
            List of created step names
        """
        if decharge_levels is None:
            decharge_levels = self.get_standard_decharge_levels()
            
        if step_params is None:
            step_params = {
                'time_period': 6.0,
                'initial_inc': 0.01,
                'max_inc': 0.3,
                'min_inc': 1e-10,
                'max_num_inc': 2000,
                'adaptive_damping_ratio': 0.15
            }
            
        step_names = []
        
        for substep in range(len(decharge_levels)):
            step_name = f'Cycle-{cycle+1}-Descent-{substep+1}'
            
            # Determine previous step
            if substep == 0:
                prev_step = f'Cycle-{cycle+1}-Plateau-3'  # Assuming 3 plateau steps
            else:
                prev_step = f'Cycle-{cycle+1}-Descent-{substep}'
                
            # Adjusted parameters for critical final steps
            current_step_params = step_params.copy()
            if substep >= 7:  # Last steps are more critical
                current_step_params.update({
                    'initial_inc': 0.005,
                    'max_inc': 0.1,
                    'adaptive_damping_ratio': 0.25
                })
                
            # Create step
            self.model.StaticStep(
                name=step_name,
                previous=prev_step,
                description=f'Cycle {cycle+1} - Descent {substep+1}',
                nlgeom=ON,
                timePeriod=current_step_params['time_period'],
                initialInc=current_step_params['initial_inc'],
                maxInc=current_step_params['max_inc'],
                minInc=current_step_params['min_inc'],
                maxNumInc=current_step_params['max_num_inc'],
                adaptiveDampingRatio=current_step_params['adaptive_damping_ratio']
            )
            
            # Calculate load
            current_load = max_load * decharge_levels[substep]
            force_per_node = current_load / len(top_nodes)
            
            # Update load
            self.model.loads['CyclicLoad'].setValuesInStep(
                stepName=step_name,
                cf2=force_per_node
            )
            
            step_names.append(step_name)
            
        print(f"  Descent: {len(decharge_levels)} steps to "
              f"{int(max_load * decharge_levels[-1])}N")
        return step_names
        
    def create_complete_cycle(self, cycle, max_load, top_nodes, 
                            charge_levels=None, decharge_levels=None,
                            num_plateau_steps=3, step_params=None):
        """
        Create complete cycle with mount, plateau, and descent phases
        
        Args:
            cycle: Cycle number (0-based)
            max_load: Maximum load value
            top_nodes: List of top nodes
            charge_levels: List of charge level multipliers
            decharge_levels: List of discharge level multipliers
            num_plateau_steps: Number of plateau steps
            step_params: Dictionary with step parameters
            
        Returns:
            Dictionary with step names for each phase
        """
        print(f"=== CYCLE {cycle+1} ===")
        
        # Create loading steps
        mount_steps = self.create_loading_steps(
            cycle, max_load, top_nodes, charge_levels, step_params
        )
        
        # Create plateau steps
        plateau_steps = self.create_plateau_steps(
            cycle, max_load, top_nodes, num_plateau_steps, step_params
        )
        
        # Create unloading steps
        descent_steps = self.create_unloading_steps(
            cycle, max_load, top_nodes, decharge_levels, step_params
        )
        
        return {
            'mount': mount_steps,
            'plateau': plateau_steps,
            'descent': descent_steps
        }