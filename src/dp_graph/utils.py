import networkx as nx
import plotly.graph_objects as go

def visualize_graph(graph):
    """
    Visualizes the dependency graph using Plotly and NetworkX.

    :param graph: The dependency graph to visualize.
    """
    G = nx.DiGraph()

    for node in graph.nodes.values():
        G.add_node(node.signature)
        for dep in node.dependencies:
            G.add_edge(node.signature, dep.signature)

    pos = nx.spring_layout(G, k=0.1, iterations=15)  # Adjust the layout to spread out the nodes more
    print(pos)

    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=1, color='#888'),  # Increase the line width
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            size=20,  # Increase the node size
            colorbar=dict(
                thickness=15,
                title=dict(
                    text='Node Connections',
                    side='right'
                ),
                xanchor='left',
            ),
            line_width=1
        )
    )

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['text'] += (node,)  # Ensure node text is added correctly
        
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f"{adjacencies[0]} ({len(adjacencies[1])} edges)")

    node_trace.marker.color = node_adjacencies
    node_trace.textposition = 'top center'
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Dependency Graph',
                        font=dict(size=20),
                        font_color='black',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper"
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    fig.show()

if __name__ == '__main__':
    from extract_meta import build_dependency_graph

    repo_path = 'GitHub_Crawler/raw_data/521xueweihan#GitHub520'
    dependency_graph = build_dependency_graph(repo_path)
    print(dependency_graph)
    visualize_graph(dependency_graph)
