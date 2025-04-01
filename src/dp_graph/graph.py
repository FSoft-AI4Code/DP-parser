from typing import List, Union
from abc import ABC, abstractmethod

@abstractmethod
class Node(ABC):
    @abstractmethod
    def __repr__(self):
        pass

class FunctionNode(Node):
    def __init__(self,
        signature: str,
        code: str,
        source: str = None,
        parameters: List[str] = None,
        dependencies: Union[List[Node], str] = None):
        """
        Represents a function object in the dependency graph.

        :param signature: A unique function signature (e.g., "module.func").
        :param parameters: A list of parameters of the function.
        :param dependencies: A list of function signatures or FunctionNode 
        objects that this function depends on.
        """
        self.code = code
        self.signature = signature
        self.source = source
        self.parameters = parameters if parameters is not None else []
        self.dependencies = dependencies if dependencies is not None else []

    def __repr__(self):
        return (
            f"FunctionNode(signature={self.signature!r}, "
            f"code={self.code!r}, "
            f"source={self.source!r}, "
            f"parameters={self.parameters!r}, "
            f"dependencies={self.dependencies!r})"
        )


class DPGraph:
    def __init__(self):
        """
        Initializes an empty dependency graph.
        """
        self.nodes = {}  # key: function signature, value: FunctionNode

    def add_function(self, signature: str, code: str,
                     source: str = None,
                     parameters: List[str] = None,
                     dependencies: List[str] = None):
        """
        Adds or updates a function node in the dependency graph.

        :param signature: A unique function signature.
        :param parameters: A list of function parameters.
        :param dependencies: A list of function signatures 
        that this function depends on.
        """
        # Register dependency nodes if they do not exist already.
        new_dependencies = []
        if dependencies:
            for dep in dependencies:
                dep_signature = dep

                if dep_signature not in self.nodes:
                    self.nodes[dep_signature] = FunctionNode(dep_signature, dep)
                new_dependencies.append(self.nodes[dep_signature])

        if signature in self.nodes:
            # Update existing node's source, parameters and dependencies if provided.
            # if source is None:
            node = self.nodes[signature]
            node.code = code
            node.source = source
            if parameters is not None:
                node.parameters = parameters
            if dependencies is not None:
                node.dependencies = new_dependencies
        else:
            self.nodes[signature] = FunctionNode(signature, code, source,
                                                 parameters, new_dependencies)


    def get_function(self, signature):
        """
        Retrieve a function node by its signature.

        :param signature: The function signature.
        :return: The corresponding FunctionNode, or None if not found.
        """
        return self.nodes.get(signature)

    def get_dependencies(self, signature):
        """
        Get the list of dependencies for a given function.

        :param signature: The function signature.
        :return: A list of FunctionNode objects that the function depends on.
        """
        node = self.get_function(signature)
        if node:
            return [self.get_function(dep) for dep in node.dependencies if self.get_function(dep)]
        return []

    def __repr__(self):
        return f"Graph(nodes={list(self.nodes.values())})"


# Example usage:
if __name__ == "__main__":
    dep_graph = Graph()
    
    code_A = '''\
def funcA(x, y):
    return funcB(x) + funcC(y, x)
'''
    code_B = '''\
def funcB(a):
    return a + 1
'''

    code_C = '''\
def funcC(b, c):
    return b + c
'''
    
    # Add functions with their signatures, parameters, and dependencies.
    dep_graph.add_function("module.funcA", code=code_A, parameters=["x", "y"], dependencies=["module.funcB", "module.funcC"])
    dep_graph.add_function("module.funcB", code=code_B, parameters=["a"])
    dep_graph.add_function("module.funcC", code=code_C, parameters=["b", "c"], dependencies=["module.funcB"])
    
    # Retrieve and print a function node.
    funcA = dep_graph.get_function("module.funcA")
    print("Function A:", funcA)
    
    # List dependencies of funcA
    deps = dep_graph.get_dependencies("module.funcA")    
    print("Dependencies of module.funcA:", deps)
    
    # Print entire graph
    print("Dependency Graph:", dep_graph)