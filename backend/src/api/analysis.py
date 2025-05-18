from fastapi import APIRouter
from pydantic import BaseModel
from src.services.ast_parser import parse_code
from typing import Dict, Any
from src.services.per_file_graph_builder import build_per_file_graph,build_call_graph
from src.services.summarizer import analyze_code_with_claude

router = APIRouter()

# Define a request model for analyzing repo
class RepoRequest(BaseModel):
    repo_url: str
    branch: str = 'main'  # Default to the main branch


class FileGraphRequest(BaseModel):
    file_path: str
    file_ast: Dict[str,Any]
    repo_url: str
    branch: str


@router.post("/api/ast")
async def get_ast(req: RepoRequest):
    """
    Parse the given repo and provide the ast generated.
    """
    ast = parse_code(req.repo_url, req.branch)
    
    return ast

@router.post("/api/file")
def generate_file_graph(req: FileGraphRequest):

    repo_url = req.repo_url
    branch = req.branch
    file_path = req.file_path
    file_ast = req.file_ast
    
    try:
        graph_data = build_per_file_graph(file_path, file_ast)
        call_graph = build_call_graph(file_ast)
        analysis = analyze_code_with_claude(repo_url,branch,file_path)
    except Exception as e:
        raise e

    return {
        "file_path":file_path,
        "file_graph": graph_data,
        "call_graph":call_graph,
        "analysis":analysis
    }

