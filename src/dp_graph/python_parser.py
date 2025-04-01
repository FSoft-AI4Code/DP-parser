import os
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

from dp_graph.graph import DPGraph


class PythonParser:
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        
        self.IGNORE_FILES = [
            "__init__.py",
            "setup.py",
            "test_*.py",
            "_test.py",
            "conftest.py",
            "config.py",
        ]

        self.BUILT_IN_FUNCTIONS = [
            "abs",
            "aiter",
            "all",
            "anext",
            "any",
            "ascii",
            "bin",
            "bool",
            "breakpoint",
            "bytearray",
            "bytes",
            "callable",
            "chr",
            "classmethod",
            "compile",
            "complex",
            "delattr",
            "dict",
            "dir",
            "divmod",
            "enumerate",
            "eval",
            "exec",
            "filter",
            "float",
            "format",
            "frozenset",
            "getattr",
            "globals",
            "hasattr",
            "hash",
            "help",
            "hex",
            "id",
            "input",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "locals",
            "map",
            "max",
            "memoryview",
            "min",
            "next",
            "object",
            "oct",
            "open",
            "ord",
            "pow",
            "print",
            "property",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "setattr",
            "slice",
            "sorted",
            "staticmethod",
            "str",
            "sum",
            "super",
            "tuple",
            "type",
            "vars",
            "zip",
        ]

    def _extract_function_name_and_params(self, node):
        func_query = self.language.query(
            """\
            (function_definition
                name: (identifier) @function.def
                parameters: (parameters) @function.params)
            """
        )
        captures = func_query.captures(node)
        if not captures:
            return None, []

        function_name = captures["function.def"][0].text.decode("utf8")
        params = (
            captures["function.params"][0]
            .text.decode("utf8")
            .replace("(", "")
            .replace(")", "")
            .split(",")
        )

        return function_name, params


    def _extract_function_calls(self, node):
        call_query = self.language.query(
            """\
            (call
                function: (identifier) @function.call
                arguments: (argument_list) @function.args)
            (call
                function: (attribute) @function.call
                arguments: (argument_list) @function.args)
            """
        )
        captures = call_query.captures(node)
        if not captures:
            return []

        calls = []
        for child in captures["function.call"]:
            if child.text.decode("utf8") in self.BUILT_IN_FUNCTIONS:
                continue
            if "." in child.text.decode("utf8"):
                calls.append(child.text.decode("utf8").split(".")[0])
            else:
                calls.append(child.text.decode("utf8"))

        # remove duplicates
        calls = list(set(calls))

        return calls


    def _extract_all_variables(self, node):
        var_query = self.language.query(
            """\
        (assignment
            left: (identifier) @variable)
            """
        )
        captures = var_query.captures(node)
        if not captures:
            return []

        variables = []
        for child in captures["variable"]:
            variables.append(child.text.decode("utf8"))

        return variables


    def extract_metadata_from_file(self, file_path):
        query = self.language.query(
            """
            (import_statement) @import.statement
            (import_from_statement) @import.statement
            (aliased_import) @import.as


        (function_definition) @function
        """
        )
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = self.parser.parse(bytes(code, "utf8"))
        captures = query.captures(tree.root_node)
        return captures


    def parse(self, repo_path: str) -> DPGraph:
        dependency_graph = DPGraph()

        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    source_path = file_path.replace(repo_path, "")
                    # print(f"Processing {file_path}...")

                    captures = self.extract_metadata_from_file(file_path)

                    for key, values in captures.items():
                        if key == "import.statement":
                            for item in values:
                                if not item.child_by_field_name("name"):
                                    # this case is `from abc import *`
                                    continue
                                if item.child_by_field_name("name").child_by_field_name(
                                    "alias"
                                ):
                                    continue  # skip aliased imports

                                import_libs = [
                                    child.text.decode("utf8")
                                    for child in item.children_by_field_name("name")
                                ]
                                for lib in import_libs:
                                    dependency_graph.add_function(
                                        signature=lib, code=item.text.decode("utf8")
                                    )

                        if key == "import.as":
                            for item in values:
                                alias = item.child_by_field_name("alias").text.decode(
                                    "utf8"
                                )
                                dependency_graph.add_function(
                                    signature=alias, code=item.text.decode("utf8")
                                )

                        if key == "function":
                            for item in values:
                                # if item = function
                                # extract signature and params
                                # extract calls and args inside the function
                                # add function to the graph
                                signature, params = self._extract_function_name_and_params(item)
                                variables = self._extract_all_variables(item)

                                if signature == "main":
                                    continue

                                calls = self._extract_function_calls(item)
                                for call in calls[:]:
                                    for var in params:
                                        if var.startswith(call):
                                            calls.remove(call)
                                    if call in calls and call in variables:
                                        calls.remove(call)

                                dependency_graph.add_function(
                                    signature,
                                    item.text.decode("utf8"),
                                    source_path,
                                    params,
                                    calls,
                                )

        return dependency_graph
