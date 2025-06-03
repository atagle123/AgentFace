from fastmcp import FastMCP
import graphviz
import base64
import tempfile
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

graphviz_mcp = FastMCP(name="graphviz_server")

# Create diagrams directory if it doesn't exist
DIAGRAMS_DIR = Path(__file__).parent.parent.parent.parent / "diagrams"
DIAGRAMS_DIR.mkdir(exist_ok=True)


@graphviz_mcp.tool()
def create_graphviz_diagram(
    dot_source: str,
    output_format: str = "png",
    engine: str = "dot",
    return_base64: bool = True,
    save_to_folder: bool = True,
    filename: Optional[str] = None
) -> str:
    """
    Creates a Graphviz diagram from DOT notation source code.

    Args:
        dot_source (str): The DOT notation source code for the graph.
        output_format (str): Output format (png, svg, pdf, ps, dot). Default is 'png'.
        engine (str): Layout engine (dot, neato, fdp, sfdp, circo, twopi). Default is 'dot'.
        return_base64 (bool): If True, returns base64 encoded image. If False, returns file path.
        save_to_folder (bool): If True, saves the diagram to the diagrams folder. Default is True.
        filename (Optional[str]): Custom filename for the saved diagram without extension.. If not provided, uses timestamp.

    Returns:
        str: Base64 encoded image data or file path to the generated diagram.
    """
    try:
        # Create graphviz object from source
        graph = graphviz.Source(dot_source, engine=engine, format=output_format)
        
        # Generate filename if not provided
        if save_to_folder and not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagram_{timestamp}"
        
        if save_to_folder:
            # Save to diagrams folder
            output_path = DIAGRAMS_DIR / filename
            # graph.render() automatically adds the extension and returns the full path
            saved_path = graph.render(str(output_path), cleanup=True)
        
        if return_base64:
            # Determine the path to read from
            if save_to_folder:
                file_to_read = saved_path
            else:
                # Render to temporary file
                with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as tmp_file:
                    output_path = tmp_file.name
                
                # Render the graph
                graph.render(output_path.replace(f'.{output_format}', ''), cleanup=True)
                file_to_read = output_path
            
            # Read and encode as base64
            with open(file_to_read, 'rb') as f:
                image_data = f.read()
            
            # Clean up temporary file if we used one
            if not save_to_folder:
                os.unlink(file_to_read)
            
            # Return base64 encoded data
            base64_data = base64.b64encode(image_data).decode('utf-8')
            result = f"data:image/{output_format};base64,{base64_data}"
            
            # Add saved path info if diagram was saved
            if save_to_folder:
                result += f"\n\nDiagram saved to: {saved_path}"
            
            return result
        else:
            if save_to_folder:
                return saved_path
            else:
                # Save to current directory
                output_path = graph.render(cleanup=True)
                return output_path
            
    except Exception as e:
        return f"Error creating diagram: {str(e)}"


@graphviz_mcp.tool()
def create_simple_graph(
    nodes: List[str],
    edges: List[Dict[str, Any]],
    graph_type: str = "digraph",
    title: Optional[str] = None,
    node_attrs: Optional[Dict[str, str]] = None,
    edge_attrs: Optional[Dict[str, str]] = None,
    output_format: str = "png",
    engine: str = "dot",
    save_to_folder: bool = True,
    filename: Optional[str] = None
) -> str:
    """
    Creates a simple graph from nodes and edges without requiring DOT notation knowledge.

    Args:
        nodes (List[str]): List of node names.
        edges (List[Dict[str, Any]]): List of edge dictionaries with 'from', 'to', and optional 'label' keys.
        graph_type (str): Type of graph ('graph' for undirected, 'digraph' for directed). Default is 'digraph'.
        title (Optional[str]): Optional title for the graph.
        node_attrs (Optional[Dict[str, str]]): Default attributes for all nodes (e.g., {'shape': 'box', 'color': 'blue'}).
        edge_attrs (Optional[Dict[str, str]]): Default attributes for all edges (e.g., {'color': 'red', 'style': 'dashed'}).
        output_format (str): Output format (png, svg, pdf, ps, dot). Default is 'png'.
        engine (str): Layout engine (dot, neato, fdp, sfdp, circo, twopi). Default is 'dot'.
        save_to_folder (bool): If True, saves the diagram to the diagrams folder. Default is True.
        filename (Optional[str]): Custom filename for the saved diagram without extension. If not provided, uses timestamp.

    Returns:
        str: Base64 encoded image data of the generated diagram.
    """
    try:
        # Start building DOT source
        dot_lines = [f"{graph_type} G {{"]
        
        # Add title if provided
        if title:
            dot_lines.append(f'    label="{title}";')
            dot_lines.append('    labelloc="t";')
        
        # Add default node attributes
        if node_attrs:
            attrs_str = ', '.join([f'{k}="{v}"' for k, v in node_attrs.items()])
            dot_lines.append(f'    node [{attrs_str}];')
        
        # Add default edge attributes
        if edge_attrs:
            attrs_str = ', '.join([f'{k}="{v}"' for k, v in edge_attrs.items()])
            dot_lines.append(f'    edge [{attrs_str}];')
        
        # Add nodes
        for node in nodes:
            dot_lines.append(f'    "{node}";')
        
        # Add edges
        connector = " -> " if graph_type == "digraph" else " -- "
        for edge in edges:
            from_node = edge.get('from', '')
            to_node = edge.get('to', '')
            label = edge.get('label', '')
            
            if from_node and to_node:
                edge_line = f'    "{from_node}"{connector}"{to_node}"'
                if label:
                    edge_line += f' [label="{label}"]'
                edge_line += ';'
                dot_lines.append(edge_line)
        
        dot_lines.append("}")
        dot_source = '\n'.join(dot_lines)
        
        # Generate filename if not provided and we're saving
        if save_to_folder and not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simple_graph_{timestamp}"
        
        # Use the create_graphviz_diagram function
        return create_graphviz_diagram(
            dot_source, 
            output_format, 
            engine, 
            return_base64=True, 
            save_to_folder=save_to_folder, 
            filename=filename
        )
        
    except Exception as e:
        return f"Error creating simple graph: {str(e)}"


@graphviz_mcp.tool()
def create_flowchart(
    steps: List[Dict[str, Any]],
    connections: List[Dict[str, str]],
    title: Optional[str] = None,
    output_format: str = "png",
    save_to_folder: bool = True,
    filename: Optional[str] = None
) -> str:
    """
    Creates a flowchart diagram from a list of steps and their connections.

    Args:
        steps (List[Dict[str, Any]]): List of step dictionaries with 'id', 'label', and optional 'shape' keys.
                                     Shape can be 'box', 'ellipse', 'diamond', 'circle', etc.
        connections (List[Dict[str, str]]): List of connection dictionaries with 'from' and 'to' keys.
        title (Optional[str]): Optional title for the flowchart.
        output_format (str): Output format (png, svg, pdf, ps, dot). Default is 'png'.
        save_to_folder (bool): If True, saves the diagram to the diagrams folder. Default is True.
        filename (Optional[str]): Custom filename for the saved diagram without extension. If not provided, uses timestamp.

    Returns:
        str: Base64 encoded image data of the generated flowchart.
    """
    try:
        # Start building DOT source for flowchart
        dot_lines = ["digraph flowchart {"]
        dot_lines.append('    rankdir=TD;')  # Top to bottom direction
        
        # Add title if provided
        if title:
            dot_lines.append(f'    label="{title}";')
            dot_lines.append('    labelloc="t";')
        
        # Add steps as nodes
        for step in steps:
            step_id = step.get('id', '')
            label = step.get('label', step_id)
            shape = step.get('shape', 'box')
            
            if step_id:
                dot_lines.append(f'    "{step_id}" [label="{label}", shape="{shape}"];')
        
        # Add connections
        for connection in connections:
            from_step = connection.get('from', '')
            to_step = connection.get('to', '')
            
            if from_step and to_step:
                dot_lines.append(f'    "{from_step}" -> "{to_step}";')
        
        dot_lines.append("}")
        dot_source = '\n'.join(dot_lines)
        
        # Generate filename if not provided and we're saving
        if save_to_folder and not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flowchart_{timestamp}"
        
        # Use the create_graphviz_diagram function
        return create_graphviz_diagram(
            dot_source, 
            output_format, 
            engine="dot", 
            return_base64=True, 
            save_to_folder=save_to_folder, 
            filename=filename
        )
        
    except Exception as e:
        return f"Error creating flowchart: {str(e)}"


@graphviz_mcp.tool()
def list_saved_diagrams(limit: Optional[int] = None) -> str:
    """
    Lists all saved diagrams in the diagrams folder.

    Args:
        limit (Optional[int]): Maximum number of diagrams to list. If None, lists all.

    Returns:
        str: A formatted list of saved diagrams with their creation times.
    """
    try:
        diagram_files = []
        
        # Get all files in the diagrams directory
        for file_path in DIAGRAMS_DIR.glob("*"):
            if file_path.is_file():
                # Get file stats
                stat = file_path.stat()
                creation_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                file_size = stat.st_size
                
                diagram_files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'created': creation_time,
                    'size': file_size
                })
        
        # Sort by creation time (newest first)
        diagram_files.sort(key=lambda x: x['created'], reverse=True)
        
        # Apply limit if specified
        if limit:
            diagram_files = diagram_files[:limit]
        
        if not diagram_files:
            return "No diagrams found in the diagrams folder."
        
        # Format the output
        result = f"Found {len(diagram_files)} diagram(s) in {DIAGRAMS_DIR}:\n\n"
        for diagram in diagram_files:
            size_kb = diagram['size'] / 1024
            result += f"📊 {diagram['name']}\n"
            result += f"   Created: {diagram['created']}\n"
            result += f"   Size: {size_kb:.1f} KB\n"
            result += f"   Path: {diagram['path']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error listing diagrams: {str(e)}"


@graphviz_mcp.tool()
def delete_diagram(filename: str) -> str:
    """
    Deletes a specific diagram from the diagrams folder.

    Args:
        filename (str): The name of the diagram file to delete.

    Returns:
        str: Confirmation message or error.
    """
    try:
        file_path = DIAGRAMS_DIR / filename
        
        if not file_path.exists():
            return f"Diagram '{filename}' not found in the diagrams folder."
        
        if not file_path.is_file():
            return f"'{filename}' is not a file."
        
        file_path.unlink()
        return f"Successfully deleted diagram: {filename}"
        
    except Exception as e:
        return f"Error deleting diagram: {str(e)}"
