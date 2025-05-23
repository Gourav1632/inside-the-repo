from fastapi import APIRouter
from pydantic import BaseModel
from src.services.ast_parser import parse_code
from typing import Dict, Any, Optional
from src.services.per_file_graph_builder import build_per_file_graph,build_call_graph
from src.services.summarizer import analyze_code_with_claude
from src.services.git_utils import get_repo_git_analysis
from src.services.ask_ai import askAI, conversation_memory

router = APIRouter()

class AskRequest(BaseModel):
    question: str
    code: str
    history_id: Optional[str] = None
    reset: Optional[bool] = False

# Define a request model for analyzing repo
class RepoRequest(BaseModel):
    repo_url: str
    branch: str = 'main'  # Default to the main branch


class FileGraphRequest(BaseModel):
    file_path: str
    file_ast: Dict[str,Any]
    repo_url: str
    branch: str


@router.post("/api/analyze")
async def get_ast(req: RepoRequest):
    """
    Parse the given repo and provide the AST and Git metadata.
    """
    ast = parse_code(req.repo_url, req.branch)
    git_metadata = get_repo_git_analysis(req.repo_url, req.branch)
    return {
        "repo_analysis": ast,
        "git_analysis": git_metadata
    }

@router.post("/api/file")
def generate_file_graph(req: FileGraphRequest):
    print("Request for file graph...")
    repo_url = req.repo_url
    branch = req.branch
    file_path = req.file_path
    file_ast = req.file_ast

    # Always generate these
    graph_data = build_per_file_graph(file_path, file_ast)
    call_graph = build_call_graph(file_ast)


    analysis = analyze_code_with_claude(repo_url, branch, file_path)


    return {
        "file_path": file_path,
        "file_graph": graph_data,
        "call_graph": call_graph,
        "analysis": analysis
    }

@router.post("/api/ask")
def ask_route(req: AskRequest):
    print("Requesting ai help...")
    history_id = req.history_id or f"{req.question[:20]}-{hash(req.code)}"

    if req.reset and history_id in conversation_memory:
        print("History deleted for history_id : ",history_id)
        del conversation_memory[history_id]
        return {"message":"Conversation history deleted."}
    response = askAI(req.question, req.code, history_id)
    return response
