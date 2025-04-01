import os
import pytest
from dp_graph import DependencyGraph

# Get the path to the test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
SAMPLE_PROJECT = os.path.join(TEST_DATA_DIR, 'sample_project')

def test_graph_initialization():
    """Test that the graph is properly initialized"""
    graph = DependencyGraph()
    assert graph.nodes == {}
    assert graph.edge_count == 0

def test_parse_project():
    """Test parsing a simple Python project"""
    graph = DependencyGraph()
    graph.parse_project(SAMPLE_PROJECT)
    
    # Check that nodes were created
    assert len(graph.nodes) > 0
    
    # Check specific functions were found
    main_process_data = f"{os.path.join(SAMPLE_PROJECT, 'main.py')}::process_data"
    assert main_process_data in graph.nodes
    
    # Check function metadata
    node_data = graph.nodes[main_process_data]
    assert node_data['name'] == 'process_data'
    assert 'Process input data and return results' in node_data['doc']

def test_get_dependencies():
    """Test getting dependencies for a function"""
    graph = DependencyGraph()
    graph.parse_project(SAMPLE_PROJECT)
    
    # Get dependencies for process_data function
    main_process_data = f"{os.path.join(SAMPLE_PROJECT, 'main.py')}::process_data"
    deps = graph.get_dependencies(main_process_data)
    
    # Should have dependencies on validate_input and transform_data
    assert main_process_data in deps
    assert len(deps[main_process_data]) == 2
    assert 'validate_input' in deps[main_process_data]
    assert 'transform_data' in deps[main_process_data]

def test_to_dict():
    """Test converting graph to dictionary format"""
    graph = DependencyGraph()
    graph.parse_project(SAMPLE_PROJECT)
    
    graph_dict = graph.to_dict()
    assert 'nodes' in graph_dict
    assert 'edges' in graph_dict
    assert 'imports' in graph_dict
    
    # Check imports
    main_py = os.path.join(SAMPLE_PROJECT, 'main.py')
    assert main_py in graph_dict['imports']
    assert 'utils' in graph_dict['imports'][main_py]

def test_invalid_project():
    """Test handling of invalid project path"""
    graph = DependencyGraph()
    with pytest.raises(FileNotFoundError):
        graph.parse_project('/path/that/does/not/exist') 