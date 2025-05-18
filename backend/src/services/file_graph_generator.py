import os
import networkx as nx


def build_dependency_graph(ast_dict):
    G = nx.DiGraph()

    # Supported extensions for your project
    supported_extensions = (".js", ".jsx", ".ts", ".tsx", ".c", ".cpp", ".py")

    for file_path, file_info in ast_dict.items():
        norm_file_path = os.path.normpath(file_path)
        G.add_node(norm_file_path)

        for imp in file_info.get("imports", []):
            if not imp["metadata"]["is_third_party"]:
                base_dir = os.path.dirname(norm_file_path)
                import_path = os.path.normpath(os.path.join(base_dir, imp["source_module"]))

                # If no known extension, try to match source file's extension
                if not import_path.endswith(supported_extensions):
                    ext = os.path.splitext(norm_file_path)[1]
                    if ext in supported_extensions:
                        import_path += ext
                    else:
                        import_path += ".js"  # fallback extension

                G.add_edge(norm_file_path, import_path)

    print("\nFinished building dependency graph.")
    print(f"Total nodes: {len(G.nodes())}, Total edges: {len(G.edges())}")
    return graph_to_json(G)


def graph_to_json(graph: nx.DiGraph):
    return {
        "nodes": list(graph.nodes),
        "edges": [{"source": u, "target": v} for u, v in graph.edges]
    }



