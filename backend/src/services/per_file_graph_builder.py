from collections import defaultdict
import networkx as nx

def build_per_file_graph(file_path: str, file_ast: dict) -> dict:
    nodes = []
    edges = []

    # Root node
    nodes.append({
        "id": file_path,
        "label": file_path.split("\\")[-1],
        "type": "file",
        "title": f"File: {file_path}"
    })

    anon_counter = defaultdict(int)

    # Functions
    for func in file_ast.get("functions", []):
        name = func["name"] or "<anonymous>"
        if name == "<anonymous>":
            anon_counter[func["start_line"]] += 1
            name += f"@{func['start_line']}_{anon_counter[func['start_line']]}"

        func_id = f"{file_path}::function::{name}"
        nodes.append({
            "id": func_id,
            "label": func["name"] or "<anonymous>",
            "type": "function",
            "title": f"Function: {func['name'] or '<anonymous>'}\nStart line: {func.get('start_line', '?')}"
        })
        edges.append({
            "from": file_path,
            "to": func_id,
            "type": "contains"
        })

    # Classes and methods
    for cls in file_ast.get("classes", []):
        class_id = f"{file_path}::class::{cls['name']}"
        nodes.append({
            "id": class_id,
            "label": cls["name"],
            "type": "class",
            "title": f"Class: {cls['name']}\nStart line: {cls.get('start_line', '?')}"
        })
        edges.append({
            "from": file_path,
            "to": class_id,
            "type": "contains"
        })

        for method in cls.get("methods", []):
            method_id = f"{class_id}::method::{method['name']}"
            nodes.append({
                "id": method_id,
                "label": method["name"],
                "type": "method",
                "title": f"Method: {method['name']}\nStart line: {method.get('start_line', '?')}"
            })
            edges.append({
                "from": class_id,
                "to": method_id,
                "type": "contains"
            })

    # Call edges
    for call in file_ast.get("calls", []):
        caller = f"{file_path}::function::{call['caller']}"
        callee = f"{file_path}::function::{call['callee']}"
        edges.append({
            "from": caller,
            "to": callee,
            "type": "calls"
        })

    return {
        "nodes": nodes,
        "edges": edges
    }



def build_call_graph(file_ast):
    nodes_set = set()
    edges = []

    calls = file_ast.get("calls", [])

    for call in calls:
        caller = call.get("caller", "<unknown>")
        callee = call.get("callee", "<unknown>")
        location = call.get("location", {})

        # Collect nodes
        nodes_set.add(caller)
        nodes_set.add(callee)

        # Build edge dict
        edge = {
            "from": caller,
            "to": callee,
            "type": "calls"
        }
        if location:
            edge["location"] = location
        edges.append(edge)

    # Build nodes list from unique node names
    nodes = [{
        "id": n,
        "label": n,
    } for n in nodes_set]

    return {
        "nodes": nodes,
        "edges": edges
    }
