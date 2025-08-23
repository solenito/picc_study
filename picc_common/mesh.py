# -*- coding: utf-8 -*-
"""
Mesh Builder Module for PICC Study
Handles mesh generation and refinement
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
import mesh


class MeshBuilder:
    """Builder class for creating and refining meshes in PICC models"""
    
    def __init__(self, model):
        """
        Initialize mesh builder
        
        Args:
            model: Abaqus model object
        """
        self.model = model
        
    def create_adaptive_mesh(self, part, zones, mesh_params=None):
        """
        Create adaptive mesh with different refinement levels
        
        Args:
            part: Part object to mesh
            zones: Dictionary with zone information from partitioning
            mesh_params: Dictionary with mesh parameters
                - global_size: Global mesh size
                - fine_horizontal_elements: Number of elements for fine zone horizontal edges
                - fine_vertical_elements: Number of elements for fine zone vertical edges
                - transition_size: Mesh size for transition zone
                
        Returns:
            None
        """
        if mesh_params is None:
            mesh_params = {
                'global_size': 0.6,
                'fine_horizontal_elements': 10,
                'fine_vertical_elements': 40,
                'transition_size': 0.3
            }
            
        print("=== ADAPTIVE MESHING ===")
        
        # Global mesh first
        part.seedPart(size=mesh_params['global_size'])
        
        # Apply fine mesh to partition edges if zones exist
        if zones.get('fine'):
            self._apply_fine_mesh_to_partition(part, zones, mesh_params)
            
        # Mesh control and generation
        part.setMeshControls(regions=part.faces, elemShape=QUAD, technique=FREE)
        
        # Set element type
        elem_type = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD)
        part.setElementType(regions=(part.faces,), elemTypes=(elem_type,))
        
        # Generate mesh
        part.generateMesh()
        
        print(f"Generated adaptive mesh for part '{part.name}'")
        
    def _apply_fine_mesh_to_partition(self, part, zones, mesh_params):
        """
        Apply fine mesh to partition edges
        
        Args:
            part: Part object
            zones: Zone information
            mesh_params: Mesh parameters
            
        Returns:
            None
        """
        # Get partition parameters from first fine zone
        if not zones['fine']:
            return
            
        # Find partition edges by analyzing all edges
        horizontal_edges = []
        vertical_edges = []
        
        # Get bounds of fine zone
        fine_face = zones['fine'][0]
        center = fine_face.pointOn[0]
        
        # Estimate partition bounds (this is approximate)
        partition_x_start = center[0] - 0.14  # Half width estimate
        partition_x_end = center[0] + 0.14
        partition_y_start = 0.0
        partition_y_end = center[1] + 0.035  # Half height estimate
        
        tolerance = 0.01
        
        for edge in part.edges:
            point = edge.pointOn[0]
            x, y = point[0], point[1]
            
            # Check if edge is on partition rectangle contour
            # Horizontal edges (top and bottom of partition)
            if (partition_x_start - tolerance <= x <= partition_x_end + tolerance):
                if (abs(y - partition_y_start) < 1e-3 or 
                    abs(y - partition_y_end) < 1e-3):
                    horizontal_edges.append(edge)
                    
            # Vertical edges (left and right of partition)  
            if (partition_y_start - tolerance <= y <= partition_y_end + tolerance):
                if (abs(x - partition_x_start) < 1e-3 or 
                    abs(x - partition_x_end) < 1e-3):
                    vertical_edges.append(edge)
        
        # Apply fine mesh
        if horizontal_edges:
            part.seedEdgeByNumber(edges=horizontal_edges, 
                                number=mesh_params['fine_horizontal_elements'])
                                
        if vertical_edges:
            part.seedEdgeByNumber(edges=vertical_edges, 
                                number=mesh_params['fine_vertical_elements'])
        
        print(f"Fine mesh applied:")
        print(f"  Horizontal edges: {len(horizontal_edges)} with "
              f"{mesh_params['fine_horizontal_elements']} elements")
        print(f"  Vertical edges: {len(vertical_edges)} with "
              f"{mesh_params['fine_vertical_elements']} elements")
              
    def create_master_line_mesh(self, part_master, mesh_size=0.02):
        """
        Create mesh for master line
        
        Args:
            part_master: Master line part
            mesh_size: Mesh size for master line
            
        Returns:
            None
        """
        print("=== Master line mesh ===")
        
        # Seed part
        part_master.seedPart(size=mesh_size)
        
        # Set element type
        elem_type = mesh.ElemType(elemCode=T2D2, elemLibrary=STANDARD)
        part_master.setElementType(regions=(part_master.edges,), 
                                 elemTypes=(elem_type,))
        
        # Generate mesh
        part_master.generateMesh()
        
        print(f"Generated master line mesh with size {mesh_size}")
        
    def apply_mesh_to_parts(self, part, part_master, zones=None, 
                          plate_mesh_params=None, master_mesh_size=0.02):
        """
        Apply appropriate mesh to both parts
        
        Args:
            part: Main plate part
            part_master: Master line part
            zones: Partition zones for adaptive meshing
            plate_mesh_params: Mesh parameters for plate
            master_mesh_size: Mesh size for master line
            
        Returns:
            None
        """
        # Mesh the main part
        if zones:
            self.create_adaptive_mesh(part, zones, plate_mesh_params)
        else:
            # Simple uniform mesh if no zones
            part.seedPart(size=plate_mesh_params.get('global_size', 0.6) 
                         if plate_mesh_params else 0.6)
            part.setMeshControls(regions=part.faces, elemShape=QUAD, technique=FREE)
            elem_type = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD)
            part.setElementType(regions=(part.faces,), elemTypes=(elem_type,))
            part.generateMesh()
            print(f"Generated uniform mesh for part '{part.name}'")
            
        # Mesh the master line
        self.create_master_line_mesh(part_master, master_mesh_size)