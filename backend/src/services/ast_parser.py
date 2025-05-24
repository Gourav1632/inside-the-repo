import os
from typing import Dict, List, Optional, Any
from tree_sitter import Language, Parser
import subprocess
import tempfile
import tree_sitter_java as tsjava
import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_javascript as tsjavascript
import tree_sitter_python as tspython
import tree_sitter_typescript as tstypescript
from src.config.language_node_maps import language_node_maps
from src.services.file_graph_generator import build_dependency_graph
from src.services.git_utils import extract_owner_repo,get_repo_tree,download_file,get_file_git_info


LANGUAGE_GRAMMARS = {
    "python": tspython.language(),
    "javascript": tsjavascript.language(),
    "typescript": tstypescript.language_typescript(),
    "tsx": tstypescript.language_tsx(),
    "java": tsjava.language(),
    "cpp": tscpp.language(),
    "c": tsc.language(),
}

LANGUAGE_FILE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts"],
    "tsx": [".tsx"],
    "java": [".java"],
    "cpp": [".cpp", ".hpp"],
    "c": [".c", ".h"],
}

parser_cache = {}

def get_parser(language):
    if language in parser_cache:
        return parser_cache[language]
    try:
        grammar_path = LANGUAGE_GRAMMARS[language]
        lang_obj = Language(grammar_path)
        parser = Parser(lang_obj)
        parser_cache[language] = parser
        return parser
    except KeyError:
        raise ValueError(f"Unsupported language: {language}")
    except TypeError:
        raise ValueError(f"Invalid grammar path for {language}: {grammar_path}")



def calculate_complexity(node):
    """Calculate simplified cyclomatic complexity"""
    complexity = 1
    stack = [node]
    while stack:
        current = stack.pop()
        if current.type in ("if_statement", "for_statement", "while_statement"):
            complexity += 1
        stack.extend(current.children)
    return complexity

def is_third_party_module(module_name):
    return not module_name.startswith(".")  # check for relative imports

def extract_import_data(node, code):
    import_info = {
        "content": code[node.start_byte:node.end_byte],
        "start_line": node.start_point[0] + 1,
        "source_module": None,
        "imported_items": [],
        "metadata": {
            "type": None,
            "is_third_party": False
        }
    }

    for child in node.children:
        if child.type == 'string':
            import_info["source_module"] = child.text.decode().strip('"').strip("'")
            import_info["metadata"]["is_third_party"] = is_third_party_module(import_info["source_module"])

        elif child.type == 'import_clause':
            for sub in child.children:
                if sub.type == 'identifier':
                    import_info["imported_items"].append(sub.text.decode())
                    import_info["metadata"]["type"] = 'default'
                elif sub.type == 'named_imports':
                    import_info["metadata"]["type"] = 'named'
                    for ni in sub.named_children:
                        if ni.type == 'import_specifier':
                            name_node = ni.child_by_field_name('name')
                            if name_node:
                                import_info["imported_items"].append(name_node.text.decode())
                elif sub.type == 'namespace_import':
                    import_info["metadata"]["type"] = 'namespace'
                    as_node = sub.child_by_field_name('name')
                    if as_node:
                        import_info["imported_items"].append('* as ' + as_node.text.decode())

    return import_info


def detect_file_language(filename: str):
    for language, extensions in LANGUAGE_FILE_EXTENSIONS.items():
        if any(filename.endswith(ext) for ext in extensions):
            return language
    return None



def extract_methods(node):
    """Helper function to extract methods from a class node."""
    methods = []
    for child in node.children:
        if child.type in ["function_definition", "method_definition"]:
            method_name = child.child_by_field_name("name").text.decode()
            methods.append(method_name)
    return methods

def extract_callee_name(call_node):
    """
    Given a call_expression node, extract a readable callee name.
    """
    callee_node = call_node.child_by_field_name("function") or call_node.child_by_field_name("callee") or call_node.children[0]

    if callee_node is None:
        callee_node = call_node.children[0]

    return get_node_name(callee_node)

def get_node_name(node):
    """
    Recursively convert a node to a string representing the callee name.
    Supports identifiers, member expressions, etc.
    """
    if node.type == "identifier":
        return node.text.decode()

    if node.type == "member_expression":
        object_node = node.child_by_field_name("object")
        property_node = node.child_by_field_name("property")
        object_name = get_node_name(object_node) if object_node else ""
        property_name = get_node_name(property_node) if property_node else ""
        if object_name and property_name:
            return f"{object_name}.{property_name}"
        return object_name or property_name

    if node.type == "call_expression":
        return extract_callee_name(node)

    return node.text.decode()

def parse_code(repo_url: str, branch: str):
    print("Parsing repo ...")
    owner, repo = extract_owner_repo(repo_url)
    tree = get_repo_tree(owner,repo, branch)
    print("Got the repo tree")

    result = {}
    with tempfile.TemporaryDirectory() as tmpdir:

        for item in tree:
            if item["type"] != "blob":
                continue
            
            path = item["path"]
            norm_path = os.path.normpath(path)

            language = detect_file_language(path)
            if not language or language not in LANGUAGE_GRAMMARS:
                continue

            parser = get_parser(language)
            if not parser:
                continue

            try:
                code = download_file(owner, repo, path, branch)
                tree = parser.parse(code.encode('utf-8'))

                extracted_info = {
                    "language":language,
                    "imports":[],
                    "classes":[],
                    "functions":[],
                    "git_info": {
                    "commit_count": 0,
                    "last_modified": None,
                    "recent_commits": [],
                    },
                    "calls": [] 
                }

                extracted_info["git_info"] = get_file_git_info(owner,repo , branch, path)


                current_function = None
                def traverse(node):
                    nonlocal current_function
                    node_text = code[node.start_byte:node.end_byte]
                    start_line = node.start_point[0] + 1  # 1-based line numbering
                    node_type = node.type
                    node_map = language_node_maps.get(language, {})


                    # Handle import extraction
                    if node_type in node_map.get('imports',[]):
                        import_info = extract_import_data(node, code)
                        extracted_info["imports"].append(import_info)

                    # Handle class extraction
                    if node_type in node_map.get('classes', []):
                        class_info = {
                            "name": node.child_by_field_name("name").text.decode(),
                            "content": node_text,
                            "start_line": start_line,
                            "methods": extract_methods(node),
                            "metadata": {
                                "type": node_type,
                                "complexity": calculate_complexity(node)
                            }
                        }
                        extracted_info["classes"].append(class_info)

                    # Handle functions
                    if node_type in node_map.get('functions', []):
                        name_node = node.child_by_field_name("name")
                        name = name_node.text.decode() if name_node else f"<anonymous>:Line-{start_line}"
                        current_function = name
                        func_info = {
                            "name": name_node.text.decode() if name_node else f"<anonymous>:Line-{start_line}",
                            "content": node_text,
                            "start_line": start_line,
                            "metadata": {
                                "type": node_type,
                                "complexity": calculate_complexity(node)
                            }
                        }
                        extracted_info["functions"].append(func_info)
                    
                    # Handle calls
                    if node_type in node_map.get('calls', []):
                        caller = current_function  # track this while traversing
                        callee_name = extract_callee_name(node)
                        extracted_info["calls"].append({
                            "caller": caller,
                            "callee": callee_name,
                            "location": {
                                "line": node.start_point[0] + 1,
                                "column": node.start_point[1] + 1
                            }
                        })

                    # Handle other node types similarly...
                    for child in node.children:
                        traverse(child)

                traverse(tree.root_node)
                result[norm_path] = extracted_info
            except Exception as e:
                print(f"Error processing {path}: {e}")
            
        print("Repo parsed successfully...")
        graph = build_dependency_graph(result)
        return {
            "ast":result,
            "dependency_graph":graph
        }
