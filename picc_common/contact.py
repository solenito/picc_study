# -*- coding: utf-8 -*-
"""
Contact Builder Module for PICC Study
Handles creation of contact surfaces and interactions
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *


class ContactBuilder:
    """Builder class for creating contact interactions in PICC models"""
    
    def __init__(self, model, assembly):
        """
        Initialize contact builder
        
        Args:
            model: Abaqus model object
            assembly: Assembly object
        """
        self.model = model
        self.assembly = assembly
        
    def create_contact_surfaces(self, instance_main, instance_master):
        """
        Create contact surfaces between crack faces
        
        Args:
            instance_main: Main plate instance (slave surface)
            instance_master: Master line instance (master surface)
            
        Returns:
            Dictionary with surface information
        """
        print("=== CREATING CONTACT SURFACES ===")
        
        # Get edges for main plate
        edges_plate = self.assembly.instances[instance_main.name].edges
        
        # Find bottom edges for slave surface
        bottom_edge_indices = []
        for idx, edge in enumerate(edges_plate, start=1):
            x, y, _ = edge.pointOn[0]
            if abs(y) < 1e-6:  # Bottom edge (y ≈ 0)
                bottom_edge_indices.append(idx)
                
        print(f"Found {len(bottom_edge_indices)} bottom edges for slave surface")
        
        # Create mask for bottom edges
        mask_val = 0
        for idx in bottom_edge_indices:
            mask_val |= 1 << (idx - 1)
            
        mask_hex = format(mask_val, 'X')
        mask_str = f'[#{mask_hex} ]'
        
        print(f"Using mask: {mask_str} for edges {bottom_edge_indices}")
        
        # Create slave surface
        slave_seq = edges_plate.getSequenceFromMask(mask=(mask_str,))
        self.assembly.Surface(name='SlaveSurface', side1Edges=slave_seq)
        print(f"SlaveSurface created with {len(slave_seq)} edges")
        
        # Create master surface from master line
        edges_master = self.assembly.instances[instance_master.name].edges
        master_edge_seq = edges_master.getSequenceFromMask(mask=('[#1 ]',))
        self.assembly.Surface(name='MasterSurface', side1Edges=master_edge_seq)
        print(f"MasterSurface created with {len(master_edge_seq)} edges")
        
        return {
            'slave_surface': self.assembly.surfaces['SlaveSurface'],
            'master_surface': self.assembly.surfaces['MasterSurface'],
            'slave_edges': len(slave_seq),
            'master_edges': len(master_edge_seq)
        }
        
    def create_contact_property(self, name='CrackContact', 
                              contact_stiffness_scale=30.0):
        """
        Create contact property for crack interaction
        
        Args:
            name: Contact property name
            contact_stiffness_scale: Scale factor for contact stiffness
            
        Returns:
            Created contact property
        """
        # Create contact property
        contact_prop = self.model.ContactProperty(name=name)
        
        # Define normal behavior
        contact_prop.NormalBehavior(
            pressureOverclosure=HARD,
            constraintEnforcementMethod=PENALTY,
            contactStiffnessScaleFactor=contact_stiffness_scale,
            allowSeparation=ON,
            stiffnessBehavior=LINEAR
        )
        
        print(f"Created contact property '{name}' with stiffness scale {contact_stiffness_scale}")
        return contact_prop
        
    def create_surface_to_surface_contact(self, contact_property_name='CrackContact',
                                        interaction_name='CrackInteraction',
                                        step_name='Initial'):
        """
        Create surface-to-surface contact interaction
        
        Args:
            contact_property_name: Name of contact property to use
            interaction_name: Name for the interaction
            step_name: Step name where interaction is created
            
        Returns:
            Created interaction
        """
        master_region = self.assembly.surfaces['MasterSurface']
        slave_region = self.assembly.surfaces['SlaveSurface']
        
        # Create interaction
        interaction = self.model.SurfaceToSurfaceContactStd(
            name=interaction_name,
            createStepName=step_name,
            master=master_region,
            slave=slave_region,
            sliding=FINITE,
            interactionProperty=contact_property_name
        )
        
        print(f"Created surface-to-surface contact interaction '{interaction_name}'")
        return interaction
        
    def setup_complete_contact(self, instance_main, instance_master,
                             contact_stiffness_scale=30.0,
                             step_name='Initial'):
        """
        Set up complete contact definition
        
        Args:
            instance_main: Main plate instance
            instance_master: Master line instance
            contact_stiffness_scale: Contact stiffness scale factor
            step_name: Step name for interaction creation
            
        Returns:
            Dictionary with contact setup information
        """
        print("=== SETTING UP COMPLETE CONTACT ===")
        
        # Create contact surfaces
        surfaces = self.create_contact_surfaces(instance_main, instance_master)
        
        # Create contact property
        contact_prop = self.create_contact_property(
            contact_stiffness_scale=contact_stiffness_scale
        )
        
        # Create interaction
        interaction = self.create_surface_to_surface_contact(step_name=step_name)
        
        print("Contact setup completed successfully")
        
        return {
            'surfaces': surfaces,
            'contact_property': contact_prop,
            'interaction': interaction
        }