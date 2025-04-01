import os
import json
import pickle
from glob import glob
from tqdm import tqdm
import concurrent.futures
import click

from dp_graph.python_parser import PythonParser

def save_dependency_graph(repo_path: str, output_dir: str) -> dict:
    """Build and save dependency graph for a repository."""
    # Build the dependency graph
    parser = PythonParser()
    graph = parser.parse(repo_path)
    
    repo_name = os.path.basename(repo_path).replace(' ', '-')

    # Save the dependency graph to a file
    graph_filename = os.path.join(output_dir, f"{repo_name}_dependency_graph.pkl")
    with open(graph_filename, 'wb') as f:
        pickle.dump(graph, f)

    # Save the metadata to a file
    metadata = {
        "repository": repo_path,
        "dependency_graph_file": graph_filename,
        "number_of_files": len(glob(os.path.join(repo_path, "**/*.py"), recursive=True)),
        "functions_count": len(graph.nodes),
        "connections_count": graph.edge_count,
    }

    json_filename = os.path.join(output_dir, f"{repo_name}_metadata.json")
    with open(json_filename, 'w', encoding="utf-8") as jsonfile:
        json.dump(metadata, jsonfile, indent=4)
    
    return metadata

def process_repositories(repo_list: list, output_dir: str):
    """Process multiple repositories in parallel."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with tqdm(total=len(repo_list), desc="Processing repositories") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(save_dependency_graph, repo_path, output_dir) 
                      for repo_path in repo_list]
            for future in concurrent.futures.as_completed(futures):
                future.result()
                pbar.update(1)

@click.group()
def cli():
    """DG-Parser - A tool for analyzing code dependency graphs."""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', default='output', help='Output directory for the analysis')
@click.option('--format', '-f', type=click.Choice(['pkl', 'json', 'dot']), default='pkl',
              help='Output format for the dependency graph')
def analyze(path: str, output: str, format: str):
    """Analyze a Python project and generate its dependency graph."""
    click.echo(f"Analyzing project: {path}")
    
    parser = PythonParser()
    graph = parser.parse(path)
    
    # simple visualize in terminal
    for node in graph.nodes.values():
        print("\tFunction Signature:", node.signature)
        print("\tDependencies:")
        for dep in node.dependencies:
            print(f"\t\t{dep.signature}")
        print("\tCalls:", node.code.split("\n")[0])
        print("\tParameters:", node.parameters)
        print("-" * 100)

    if not os.path.exists(output):
        os.makedirs(output)
        
    project_name = os.path.basename(path).replace(' ', '-')
    output_file = os.path.join(output, f"{project_name}_graph.{format}")
    
    if format == 'pkl':
        with open(output_file, 'wb') as f:
            pickle.dump(graph, f)
    elif format == 'json':
        with open(output_file, 'w') as f:
            json.dump(graph.to_dict(), f, indent=2)
    elif format == 'dot':
        graph.to_dot(output_file)
    
    click.echo(f"Dependency graph saved to: {output_file}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', default='output', help='Output directory')
def batch(path: str, output: str):
    """Process multiple Python projects in a directory."""
    repo_list = glob(os.path.join(path, "*"))
    click.echo(f"Found {len(repo_list)} projects to process")
    process_repositories(repo_list, output)

def main():
    cli()
