# -*- coding: utf-8 -*-
"""
Test Module for PICC Common
Tests the refactored structure without requiring Abaqus
"""

import sys
import os

def test_module_structure():
    """Test that all modules are properly structured"""
    
    print("Testing PICC Common Module Structure...")
    
    # Test that package directory exists
    package_dir = os.path.join(os.path.dirname(__file__), 'picc_common')
    if not os.path.exists(package_dir):
        print("✗ Package directory 'picc_common' not found")
        return False
    print("✓ Package directory exists")
    
    # Test that all expected modules exist
    expected_modules = [
        '__init__.py',
        'geometry.py',
        'materials.py', 
        'mesh.py',
        'boundary_conditions.py',
        'cyclic_loading.py',
        'contact.py',
        'outputs.py',
        'model_builder.py'
    ]
    
    for module in expected_modules:
        module_path = os.path.join(package_dir, module)
        if not os.path.exists(module_path):
            print(f"✗ Module {module} not found")
            return False
        print(f"✓ Module {module} exists")
    
    # Test syntax by compiling modules
    try:
        import py_compile
        for module in expected_modules:
            if module.endswith('.py'):
                module_path = os.path.join(package_dir, module)
                py_compile.compile(module_path, doraise=True)
        print("✓ All modules compile successfully")
    except py_compile.PyCompileError as e:
        print(f"✗ Compilation error: {e}")
        return False
    
    print("✓ All module structure tests passed")
    return True

def test_class_definitions():
    """Test class definitions without importing Abaqus-dependent code"""
    
    print("\nTesting class definitions...")
    
    # Read and check for class definitions
    package_dir = os.path.join(os.path.dirname(__file__), 'picc_common')
    
    expected_classes = {
        'geometry.py': ['GeometryBuilder'],
        'materials.py': ['MaterialBuilder'],
        'mesh.py': ['MeshBuilder'],
        'boundary_conditions.py': ['BoundaryConditionBuilder'],
        'cyclic_loading.py': ['CyclicLoadingBuilder'],
        'contact.py': ['ContactBuilder'],
        'outputs.py': ['OutputBuilder'],
        'model_builder.py': ['PICCModelBuilder']
    }
    
    for module_file, classes in expected_classes.items():
        module_path = os.path.join(package_dir, module_file)
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for class_name in classes:
                if f'class {class_name}:' in content or f'class {class_name}(' in content:
                    print(f"✓ Class {class_name} found in {module_file}")
                else:
                    print(f"✗ Class {class_name} not found in {module_file}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error reading {module_file}: {e}")
            return False
    
    print("✓ All class definitions found")
    return True

def test_documentation():
    """Test that documentation files exist"""
    
    print("\nTesting documentation...")
    
    doc_files = [
        'REFACTORING_README.md',
        'picc_v3_refactored.py',
        'picc_component_example.py'
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            print(f"✓ Documentation file {doc_file} exists")
        else:
            print(f"✗ Documentation file {doc_file} not found")
            return False
    
    print("✓ All documentation files found")
    return True

def test_refactoring_benefits():
    """Calculate and report refactoring benefits"""
    
    print("\nCalculating refactoring benefits...")
    
    # Count lines in original files
    original_files = [
        'picc-automate.py',
        'picc_ready.py', 
        'picc-v2.py',
        'picc-plane-stress.py',
        'edge_crack_cyclic_loading.py'
    ]
    
    original_total = 0
    for file in original_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                original_total += lines
                print(f"  {file}: {lines} lines")
    
    # Count lines in refactored modules
    package_dir = 'picc_common'
    refactored_total = 0
    
    if os.path.exists(package_dir):
        for file in os.listdir(package_dir):
            if file.endswith('.py'):
                file_path = os.path.join(package_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    refactored_total += lines
                    print(f"  {file}: {lines} lines")
    
    # Count new example files
    example_files = ['picc_v3_refactored.py', 'picc_component_example.py']
    example_total = 0
    for file in example_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                example_total += lines
                print(f"  {file}: {lines} lines")
    
    total_new = refactored_total + example_total
    
    print(f"\nRefactoring Summary:")
    print(f"  Original scripts: {original_total} lines")
    print(f"  Refactored modules: {refactored_total} lines")
    print(f"  Example scripts: {example_total} lines")
    print(f"  Total new code: {total_new} lines")
    
    if original_total > 0:
        reduction_ratio = (original_total - refactored_total) / original_total
        print(f"  Code reduction: {reduction_ratio:.1%}")
        
    print("✓ Refactoring benefits calculated")
    return True

def main():
    """Run all tests"""
    
    print("=" * 50)
    print("PICC Common Module Test Suite")
    print("=" * 50)
    
    tests = [
        test_module_structure,
        test_class_definitions,
        test_documentation,
        test_refactoring_benefits
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)