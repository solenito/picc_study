# -*- coding: utf-8 -*-
"""
Materials Builder Module for PICC Study
Handles creation of materials and sections
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *


class MaterialBuilder:
    """Builder class for creating materials and sections in PICC models"""
    
    def __init__(self, model):
        """
        Initialize materials builder
        
        Args:
            model: Abaqus model object
        """
        self.model = model
        
    def create_steel_material(self, name='Steel', 
                            elastic_modulus=210000.0, 
                            poisson_ratio=0.3,
                            yield_stress=250.0,
                            plastic_strain=0.01):
        """
        Create elastic-plastic steel material
        
        Args:
            name: Material name
            elastic_modulus: Elastic modulus (MPa)
            poisson_ratio: Poisson's ratio
            yield_stress: Yield stress (MPa)
            plastic_strain: Plastic strain for hardening
            
        Returns:
            Created material object
        """
        # Create material
        material = self.model.Material(name=name)
        
        # Add elastic properties
        material.Elastic(table=((elastic_modulus, poisson_ratio),))
        
        # Add plastic properties (slight hardening for convergence)
        material.Plastic(table=((yield_stress, 0.0), 
                               (yield_stress, plastic_strain)))
        
        print(f"Created steel material '{name}' with E={elastic_modulus} MPa, "
              f"fy={yield_stress} MPa")
        
        return material
        
    def create_rigid_master_material(self, name='RigidMaster',
                                   elastic_modulus=2100000.0,
                                   poisson_ratio=0.3):
        """
        Create rigid material for master line
        
        Args:
            name: Material name
            elastic_modulus: Elastic modulus (MPa)
            poisson_ratio: Poisson's ratio
            
        Returns:
            Created material object
        """
        # Create material
        material = self.model.Material(name=name)
        
        # Add elastic properties (high stiffness for rigid behavior)
        material.Elastic(table=((elastic_modulus, poisson_ratio),))
        
        print(f"Created rigid master material '{name}' with E={elastic_modulus} MPa")
        
        return material
        
    def create_solid_section(self, name='Section', 
                           material_name='Steel', 
                           thickness=1.0):
        """
        Create homogeneous solid section for plate
        
        Args:
            name: Section name
            material_name: Name of associated material
            thickness: Section thickness
            
        Returns:
            Created section object
        """
        section = self.model.HomogeneousSolidSection(
            name=name, 
            material=material_name, 
            thickness=thickness
        )
        
        print(f"Created solid section '{name}' with material '{material_name}', "
              f"thickness={thickness}")
        
        return section
        
    def create_truss_section(self, name='MasterSection',
                           material_name='RigidMaster',
                           area=1.0):
        """
        Create truss section for master line
        
        Args:
            name: Section name
            material_name: Name of associated material
            area: Cross-sectional area
            
        Returns:
            Created section object
        """
        section = self.model.TrussSection(
            name=name,
            material=material_name,
            area=area
        )
        
        print(f"Created truss section '{name}' with material '{material_name}', "
              f"area={area}")
        
        return section
        
    def assign_section_to_part(self, part, section_name, region_type='faces'):
        """
        Assign section to part regions
        
        Args:
            part: Part object
            section_name: Name of section to assign
            region_type: Type of region ('faces' for solid, 'edges' for truss)
            
        Returns:
            None
        """
        if region_type == 'faces':
            # For solid sections (plate)
            part.SectionAssignment(region=(part.faces,), sectionName=section_name)
            print(f"Assigned section '{section_name}' to part faces")
            
        elif region_type == 'edges':
            # For truss sections (master line)
            edges_set = part.Set(name='AllEdges', edges=part.edges)
            part.SectionAssignment(region=edges_set, sectionName=section_name)
            print(f"Assigned section '{section_name}' to part edges")
            
        else:
            raise ValueError(f"Invalid region_type: {region_type}. "
                           "Must be 'faces' or 'edges'")
                           
    def create_standard_materials(self):
        """
        Create standard materials and sections for PICC study
        
        Returns:
            Dictionary with created materials and sections
        """
        # Create materials
        steel = self.create_steel_material()
        rigid_master = self.create_rigid_master_material()
        
        # Create sections
        solid_section = self.create_solid_section()
        truss_section = self.create_truss_section()
        
        return {
            'materials': {
                'steel': steel,
                'rigid_master': rigid_master
            },
            'sections': {
                'solid': solid_section,
                'truss': truss_section
            }
        }