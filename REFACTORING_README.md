# PICC Common Module

This module provides a refactored, modular structure for Plasticity Induced Crack Closure (PICC) studies using Abaqus. The code has been reorganized to eliminate duplication and improve maintainability.

## Structure

The `picc_common` module contains the following components:

### Core Modules

- **`geometry.py`** - `GeometryBuilder`: Creates geometric parts, partitions, and sketches
- **`materials.py`** - `MaterialBuilder`: Handles materials and sections
- **`mesh.py`** - `MeshBuilder`: Manages mesh generation and refinement
- **`boundary_conditions.py`** - `BoundaryConditionBuilder`: Creates boundary conditions and node sets
- **`cyclic_loading.py`** - `CyclicLoadingBuilder`: Handles cyclic loading patterns and steps
- **`contact.py`** - `ContactBuilder`: Sets up contact surfaces and interactions
- **`outputs.py`** - `OutputBuilder`: Creates history and field output requests
- **`model_builder.py`** - `PICCModelBuilder`: Main orchestrator for complete models

## Usage Examples

### Simple Complete Model

```python
from picc_common import PICCModelBuilder

# Create model with default settings
builder = PICCModelBuilder('MyModel')
model_info = builder.build_complete_model()
job = builder.create_job("MyJob")
```

### Custom Configuration

```python
from picc_common import PICCModelBuilder

builder = PICCModelBuilder('CustomModel')

config = {
    'geometry_params': {
        'width': 60.0,
        'height': 40.0,
        'crack_length': 12.0,
        'partition_params': {
            'x_start': 10.0,
            'y_start': 0.0,
            'width': 0.5,
            'height': 0.1,
            'include_transition': True,
            'transition_margin': 0.2
        }
    },
    'num_cycles': 15,
    'max_load': 4000,
    'contact_stiffness_scale': 25.0,
    'monitor_nodes': [50, 51, 52]
}

model_info = builder.build_complete_model(config)
```

### Using Individual Components

```python
from picc_common import GeometryBuilder, MaterialBuilder, MeshBuilder

# Initialize model
model = mdb.Model(name='ComponentExample')

# Use individual builders
geo_builder = GeometryBuilder(model)
plate = geo_builder.create_plate_part()
zones = geo_builder.create_partition(plate)

mat_builder = MaterialBuilder(model)
steel = mat_builder.create_steel_material()
section = mat_builder.create_solid_section()
```

## Configuration Parameters

### Geometry Parameters
```python
geometry_params = {
    'width': 50.0,              # Plate width
    'height': 50.0,             # Plate height  
    'crack_length': 10.0,       # Initial crack length
    'partition_params': {
        'x_start': 9.93,        # Partition X start
        'y_start': 0.0,         # Partition Y start
        'width': 0.28,          # Partition width
        'height': 0.07,         # Partition height
        'include_transition': True,      # Include transition zone
        'transition_margin': 0.15        # Transition margin
    }
}
```

### Mesh Parameters
```python
mesh_params = {
    'global_size': 0.6,                    # Global mesh size
    'fine_horizontal_elements': 10,        # Fine zone horizontal elements
    'fine_vertical_elements': 40,          # Fine zone vertical elements
    'transition_size': 0.3                 # Transition zone size
}
```

### Loading Parameters
```python
loading_params = {
    'charge_levels': [0.20, 0.40, 0.60, 0.80, 1.00],  # Loading levels
    'decharge_levels': [0.95, 0.90, ..., 0.05],       # Unloading levels
    'num_plateau_steps': 3,                            # Plateau steps
    'step_params': {
        'time_period': 6.0,
        'initial_inc': 0.01,
        'max_inc': 0.3,
        'min_inc': 1e-10,
        'max_num_inc': 2000,
        'adaptive_damping_ratio': 0.15
    }
}
```

## Migration from Old Scripts

The new modular structure replaces the following original scripts:

- `picc-automate.py` → Use `PICCModelBuilder` with custom config
- `picc_ready.py` → Use `PICCModelBuilder.build_complete_model()`
- `picc-v2.py` → Use `picc_v3_refactored.py` as template
- `picc-plane-stress.py` → Use individual components as needed
- `edge_crack_cyclic_loading.py` → Use `CyclicLoadingBuilder`

## Benefits of Refactored Structure

1. **Eliminates Code Duplication**: Common functionality extracted into reusable modules
2. **Improved Maintainability**: Changes only need to be made in one place
3. **Flexibility**: Mix and match components for different use cases
4. **Consistency**: Standardized interfaces and parameters
5. **Extensibility**: Easy to add new features or variations
6. **Documentation**: Clear separation of concerns and better documentation

## File Organization

```
picc_common/
├── __init__.py                 # Package initialization
├── geometry.py                 # Geometry creation
├── materials.py                # Materials and sections  
├── mesh.py                     # Mesh generation
├── boundary_conditions.py      # Boundary conditions
├── cyclic_loading.py           # Loading patterns
├── contact.py                  # Contact setup
├── outputs.py                  # Output requests
└── model_builder.py            # Main orchestrator
```

## Legacy Scripts

The original scripts are preserved for reference:
- `picc-automate.py`
- `picc_ready.py` 
- `picc-v2.py`
- `picc-plane-stress.py`
- `edge_crack_cyclic_loading.py`

New development should use the refactored `picc_common` module structure.