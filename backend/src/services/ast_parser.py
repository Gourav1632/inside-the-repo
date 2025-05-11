import os
from tree_sitter import Language, Parser
import subprocess
import tempfile
import tree_sitter_java as tsjava
import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_javascript as tsjavascript
import tree_sitter_python as tspython
import tree_sitter_typescript as tstypescript

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

def detect_file_language(filename: str):
    for language, extensions in LANGUAGE_FILE_EXTENSIONS.items():
        if any(filename.endswith(ext) for ext in extensions):
            return language
    return None

def parse_code(repo_url: str, branch: str):
    with tempfile.TemporaryDirectory() as repo_dir:
        try:
            subprocess.run(["git", "clone", "--branch", branch, "--single-branch", repo_url, repo_dir], check=True)
            code_structure = {}

            for root, _, files in os.walk(repo_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    language = detect_file_language(file)
                    if not language or language not in LANGUAGE_GRAMMARS:
                        continue

                    parser = get_parser(language)
                    if not parser:
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        tree = parser.parse(code.encode('utf-8'))
                        root_node = tree.root_node

                        extracted_info = {
                            "functions": [],
                            "classes": [],
                            "variables": [],
                            "comments": [],
                            "imports": [],
                            "literals": [],
                            "conditionals": [],
                            "loops": [],
                            "error_handling": [],
                            "return_statements": [],
                            "method_calls": [],
                            "annotations": [],
                            "access_modifiers": [],
                            "control_flow_keywords": []  # <-- new feature
                        }

                        def traverse(node):
                            node_text = code[node.start_byte:node.end_byte]
                            start_line = node.start_point[0]
                            end_line = node.end_point[0]

                            node_info = {
                                "text": node_text,
                                "line": [start_line, end_line]  # line number range
                            }
                            t = node.type
                            if language == "python":
                                if t == 'function_definition': extracted_info["functions"].append(node_info)
                                elif t == 'class_definition': extracted_info["classes"].append(node_info)
                                elif t == 'identifier': extracted_info["variables"].append(node_info)
                                elif t == 'comment': extracted_info["comments"].append(node_info)
                                elif t == 'import': extracted_info["imports"].append(node_info)
                                elif t == 'string': extracted_info["literals"].append(node_info)
                                elif t in ['if_statement', 'elif_statement']: extracted_info["conditionals"].append(node_info)
                                elif t in ['while_statement', 'for_statement']: extracted_info["loops"].append(node_info)
                                elif t == 'try_statement': extracted_info["error_handling"].append(node_info)
                                elif t == 'return_statement': extracted_info["return_statements"].append(node_info)
                                elif t == 'call': extracted_info["method_calls"].append(node_info)
                                elif t == 'decorator': extracted_info["annotations"].append(node_info)
                                elif t in ['public', 'private', 'protected']: extracted_info["access_modifiers"].append(node_info)
                                elif t in ['break_statement', 'continue_statement', 'pass_statement']: extracted_info["control_flow_keywords"].append(node_info)

                            elif language in ["javascript", "typescript", "tsx"]:
                                if t in ['function_declaration', 'function_expression']: extracted_info["functions"].append(node_info)
                                elif t == 'class_declaration': extracted_info["classes"].append(node_info)
                                elif t == 'identifier': extracted_info["variables"].append(node_info)
                                elif t == 'comment': extracted_info["comments"].append(node_info)
                                elif t == 'import_declaration': extracted_info["imports"].append(node_info)
                                elif t == 'string_literal': extracted_info["literals"].append(node_info)
                                elif t in ['if_statement', 'else_statement']: extracted_info["conditionals"].append(node_info)
                                elif t in ['while_statement', 'for_statement']: extracted_info["loops"].append(node_info)
                                elif t == 'try_statement': extracted_info["error_handling"].append(node_info)
                                elif t == 'return_statement': extracted_info["return_statements"].append(node_info)
                                elif t == 'call_expression': extracted_info["method_calls"].append(node_info)
                                elif t == 'decorator': extracted_info["annotations"].append(node_info)
                                elif t in ['public', 'private', 'protected']: extracted_info["access_modifiers"].append(node_info)
                                elif t in ['break_statement', 'continue_statement']: extracted_info["control_flow_keywords"].append(node_info)

                            elif language == "java":
                                if t == 'method_declaration': extracted_info["functions"].append(node_info)
                                elif t == 'class_declaration': extracted_info["classes"].append(node_info)
                                elif t == 'variable_declarator': extracted_info["variables"].append(node_info)
                                elif t == 'comment': extracted_info["comments"].append(node_info)
                                elif t == 'import_declaration': extracted_info["imports"].append(node_info)
                                elif t == 'string_literal': extracted_info["literals"].append(node_info)
                                elif t in ['if_statement', 'else_statement']: extracted_info["conditionals"].append(node_info)
                                elif t in ['while_statement', 'for_statement']: extracted_info["loops"].append(node_info)
                                elif t == 'try_statement': extracted_info["error_handling"].append(node_info)
                                elif t == 'return_statement': extracted_info["return_statements"].append(node_info)
                                elif t == 'method_invocation': extracted_info["method_calls"].append(node_info)
                                elif t == 'annotation': extracted_info["annotations"].append(node_info)
                                elif t in ['public', 'private', 'protected']: extracted_info["access_modifiers"].append(node_info)
                                elif t in ['break_statement', 'continue_statement']: extracted_info["control_flow_keywords"].append(node_info)

                            elif language in ["cpp", "c"]:
                                if t == 'function_definition': extracted_info["functions"].append(node_info)
                                elif t == 'class_specifier': extracted_info["classes"].append(node_info)
                                elif t == 'identifier': extracted_info["variables"].append(node_info)
                                elif t == 'comment': extracted_info["comments"].append(node_info)
                                elif t == 'preproc_include': extracted_info["imports"].append(node_info)
                                elif t == 'string_literal': extracted_info["literals"].append(node_info)
                                elif t in ['if_statement', 'else_statement']: extracted_info["conditionals"].append(node_info)
                                elif t in ['while_statement', 'for_statement']: extracted_info["loops"].append(node_info)
                                elif t == 'try_statement': extracted_info["error_handling"].append(node_info)
                                elif t == 'return_statement': extracted_info["return_statements"].append(node_info)
                                elif t == 'call_expression': extracted_info["method_calls"].append(node_info)
                                elif t in ['public', 'private', 'protected']: extracted_info["access_modifiers"].append(node_info)
                                elif t in ['break_statement', 'continue_statement']: extracted_info["control_flow_keywords"].append(node_info)

                            for child in node.children:
                                traverse(child)

                        traverse(root_node)
                        code_structure[file_path] = {"language": language, **extracted_info}

                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Git clone failed: {e}")
        return code_structure
