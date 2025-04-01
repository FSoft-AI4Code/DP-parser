# Dependency graph parser (DP-parser)

A Python package for parsing and analyzing code dependency graphs.

## Features

- Parse Python code to generate dependency graphs
- Analyze module dependencies and relationships
- Command-line interface for quick analysis
- Export dependency graphs (i.e. Pickle)
<!-- - Built on `networkx` and `astroid` -->

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. From PyPI (not yet published):
```bash
pip install dg-parser
```

2. From source:
```bash
git clone https://github.com/nmd2k/DG-parser.git
cd DG-parser
pip install -e .
```

### Basic Usage

#### 1. Command Line Interface

The package provides a convenient CLI for quick analysis:

```bash
dp-parser analyze tests/test_data/sample_project             

>>> Analyzing project: tests/test_data/sample_project
        Function Signature: validate_input
        Dependencies:
        Calls: from utils import validate_input, transform_data
        Parameters: ['data']
----------------------------------------------------------------------------------------------------
        Function Signature: transform_data
        Dependencies:
        Calls: from utils import validate_input, transform_data
        Parameters: ['data']
----------------------------------------------------------------------------------------------------
        Function Signature: ValueError
        Dependencies:
        Calls: ValueError
        Parameters: []
----------------------------------------------------------------------------------------------------
        Function Signature: process_data
        Dependencies:
                transform_data
                ValueError
                validate_input
        Calls: def process_data(data):
        Parameters: ['data']
----------------------------------------------------------------------------------------------------
Dependency graph saved to: output/sample_project_graph.pkl
```

#### 2. Python API

```python
from dp_graph import PythonParser

# Create a dependency graph instance
parser = PythonParser()

# Parse a Python project
graph = parser.parse("/path/to/project")

# Get all dependencies
for node in graph.nodes.values():
    print("\tFunction Signature:", node.signature)
    print("\tDependencies:")
    for dep in node.dependencies:
        print(f"\t\t{dep.signature}")
    print("\tCalls:", node.code.split("\n")[0])
    print("\tParameters:", node.parameters)
    print("-" * 100)

# Export the graph
# Comming soon
```

## License

MIT License
