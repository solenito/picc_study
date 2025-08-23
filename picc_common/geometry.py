# -*- coding: utf-8 -*-
"""
Geometry Builder Module for PICC Study
Handles creation of geometric parts, partitions and sketches
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *


class GeometryBuilder:
    """Builder class for creating geometry components in PICC models"""
    
    def __init__(self, model):
        """
        Initialize geometry builder
        
        Args:
            model: Abaqus model object
        """
        self.model = model
        self.width = 50.0
        self.height = 50.0
        self.crack_length = 10.0
        
    def create_plate_part(self, name='Plate', width=None, height=None):
        """
        Create main plate part
        
        Args:
            name: Name of the part
            width: Plate width (defaults to self.width)
            height: Plate height (defaults to self.height)
            
        Returns:
            Created part object
        """
        if width is None:
            width = self.width
        if height is None:
            height = self.height
            
        # Create sketch
        s = self.model.ConstrainedSketch(name='sketch', sheetSize=200.0)
        s.rectangle(point1=(0.0, 0.0), point2=(width, height))
        
        # Create part
        part = self.model.Part(name=name, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        part.BaseShell(sketch=s)
        
        print(f"Created plate part '{name}' with dimensions {width}x{height}")
        return part
        
    def create_master_line_part(self, name='MasterLine', width=None):
        """
        Create master line part for contact
        
        Args:
            name: Name of the part
            width: Line width (defaults to self.width)
            
        Returns:
            Created part object
        """
        if width is None:
            width = self.width
            
        # Create sketch
        s_master = self.model.ConstrainedSketch(name='masterLineSketch', sheetSize=200.0)
        s_master.Line(point1=(0.0, 0.0), point2=(width, 0.0))
        
        # Create part
        part_master = self.model.Part(name=name, dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        part_master.BaseWire(sketch=s_master)
        
        print(f"Created master line part '{name}' with width {width}")
        return part_master
        
    def create_partition(self, part, partition_params=None):
        """
        Create partitions in the plate for mesh refinement
        
        Args:
            part: Part object to partition
            partition_params: Dictionary with partition parameters
                - x_start: X coordinate start
                - y_start: Y coordinate start  
                - width: Partition width
                - height: Partition height
                - include_transition: Whether to include transition zone
                - transition_margin: Margin for transition zone
                
        Returns:
            Dictionary with zone information
        """
        if partition_params is None:
            # Default parameters for fine partition around crack tip
            partition_params = {
                'x_start': 9.93,
                'y_start': 0.0,
                'width': 0.28,
                'height': 0.07,
                'include_transition': True,
                'transition_margin': 0.15
            }
            
        x_start = partition_params['x_start']
        y_start = partition_params['y_start']
        width = partition_params['width']
        height = partition_params['height']
        
        x_end = x_start + width
        y_end = y_start + height
        
        # Create partition sketch
        s_partition = self.model.ConstrainedSketch(name='partitionSketch', sheetSize=200.0)
        
        # Add transition zone if requested
        if partition_params.get('include_transition', False):
            margin = partition_params.get('transition_margin', 0.15)
            trans_x_start = x_start - margin
            trans_y_start = y_start
            trans_width = width + 2 * margin
            trans_height = height + margin
            trans_x_end = trans_x_start + trans_width
            trans_y_end = trans_y_start + trans_height
            
            # Draw transition rectangle
            s_partition.Line(point1=(trans_x_start, trans_y_start), 
                           point2=(trans_x_start, trans_y_end))
            s_partition.Line(point1=(trans_x_start, trans_y_end), 
                           point2=(trans_x_end, trans_y_end))
            s_partition.Line(point1=(trans_x_end, trans_y_end), 
                           point2=(trans_x_end, trans_y_start))
        
        # Draw fine partition rectangle
        s_partition.Line(point1=(x_start, y_start), point2=(x_start, y_end))
        s_partition.Line(point1=(x_start, y_end), point2=(x_end, y_end))
        s_partition.Line(point1=(x_end, y_end), point2=(x_end, y_start))
        
        # Apply partition
        face_to_partition = part.faces[0]
        part.PartitionFaceBySketch(faces=face_to_partition, sketch=s_partition)
        
        # Identify zones
        zones = self._identify_partition_zones(part, partition_params)
        
        print(f"Created partitions: {len(zones['fine'])} fine zone(s), "
              f"{len(zones.get('transition', []))} transition zone(s), "
              f"{len(zones['normal'])} normal zone(s)")
              
        return zones
        
    def _identify_partition_zones(self, part, partition_params):
        """
        Identify different zones after partitioning
        
        Args:
            part: Partitioned part
            partition_params: Partition parameters
            
        Returns:
            Dictionary with zone lists
        """
        x_start = partition_params['x_start']
        y_start = partition_params['y_start']
        width = partition_params['width']
        height = partition_params['height']
        x_end = x_start + width
        y_end = y_start + height
        
        zones = {
            'fine': [],
            'transition': [],
            'normal': []
        }
        
        if partition_params.get('include_transition', False):
            margin = partition_params.get('transition_margin', 0.15)
            trans_x_start = x_start - margin
            trans_y_start = y_start
            trans_width = width + 2 * margin
            trans_height = height + margin
            trans_x_end = trans_x_start + trans_width
            trans_y_end = trans_y_start + trans_height
        
        for i, face in enumerate(part.faces):
            try:
                center = face.pointOn[0]
                x_center = center[0]
                y_center = center[1]
                
                # Check if in fine zone
                if (x_start <= x_center <= x_end and 
                    y_start <= y_center <= y_end):
                    zones['fine'].append(face)
                # Check if in transition zone (if enabled)
                elif (partition_params.get('include_transition', False) and
                      trans_x_start <= x_center <= trans_x_end and 
                      trans_y_start <= y_center <= trans_y_end):
                    zones['transition'].append(face)
                else:
                    zones['normal'].append(face)
                    
            except Exception as e:
                print(f"Zone {i+1}: identification error - {e}")
                zones['normal'].append(face)
                
        return zones