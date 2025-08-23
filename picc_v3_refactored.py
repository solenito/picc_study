# -*- coding: utf-8 -*-
"""
PICC V3 - Refactored Script
Using the new modular structure for PICC study
"""

from picc_common import PICCModelBuilder

# Build complete PICC model with custom configuration
def main():
    """Main function to build PICC model"""
    
    # Initialize model builder
    builder = PICCModelBuilder('CrackModel')
    
    # Configuration for the model
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
        'mesh_params': {
            'global_size': 0.6,
            'fine_horizontal_elements': 10,
            'fine_vertical_elements': 40
        },
        'num_cycles': 20,
        'max_load': 5000,
        'loading_params': {
            'charge_levels': [0.20, 0.40, 0.60, 0.80, 1.00],
            'decharge_levels': [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 
                              0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 
                              0.15, 0.10, 0.05],
            'num_plateau_steps': 3,
            'step_params': {
                'time_period': 6.0,
                'initial_inc': 0.01,
                'max_inc': 0.3,
                'min_inc': 1e-10,
                'max_num_inc': 2000,
                'adaptive_damping_ratio': 0.15
            }
        },
        'contact_stiffness_scale': 30.0,
        'monitor_nodes': [44, 45, 46, 47],
        'last_cycle_steps': [
            'LastCycle-Mount-1', 'LastCycle-Mount-5', 'LastCycle-Mount-10',
            'LastCycle-Plateau-1',
            'LastCycle-Descent-1', 'LastCycle-Descent-10', 
            'LastCycle-Descent-20', 'LastCycle-Descent-30'
        ]
    }
    
    # Build complete model
    model_info = builder.build_complete_model(config)
    
    # Create job
    job = builder.create_job("{{JOBNAME}}")
    
    print("Model created successfully")
    print("Job ready to submit")
    
    return model_info, job

if __name__ == "__main__":
    main()