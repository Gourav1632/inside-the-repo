from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from fastapi.concurrency import run_in_threadpool
import asyncio

from src.services.ast_parser import parse_code
from src.services.per_file_graph_builder import build_per_file_graph, build_call_graph
from src.services.summarizer import analyze_code_with_claude
from src.services.git_utils import get_repo_git_analysis
from src.services.ask_ai import askAI, conversation_memory

router = APIRouter()

# === Request Schemas ===
class AskRequest(BaseModel):
    question: str
    code: str
    history_id: Optional[str] = None
    reset: Optional[bool] = False

class RepoRequest(BaseModel):
    repo_url: str
    branch: str = 'main' 

class FileGraphRequest(BaseModel):
    file_path: str
    file_ast: Dict[str, Any]
    repo_url: str
    branch: str


# === Routes ===

@router.post("/api/analyze")
async def get_ast(req: RepoRequest):
    try:
        ast_task = asyncio.create_task(run_in_threadpool(parse_code, req.repo_url, req.branch))
        git_metadata_task = asyncio.create_task(run_in_threadpool(get_repo_git_analysis, req.repo_url, req.branch))

        ast, git_metadata = await asyncio.gather(ast_task, git_metadata_task)

        return {
            "repo_analysis": ast,
            "git_analysis": git_metadata
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@router.post("/api/file")
async def generate_file_graph(req: FileGraphRequest):
    print("Request for file graph...")

    file_graph_task = asyncio.create_task(run_in_threadpool(build_per_file_graph, req.file_path, req.file_ast))
    call_graph_task = asyncio.create_task(run_in_threadpool(build_call_graph, req.file_ast))
    analysis_task = asyncio.create_task(run_in_threadpool(analyze_code_with_claude, req.repo_url, req.branch, req.file_path))

    file_graph, call_graph, analysis = await asyncio.gather(file_graph_task, call_graph_task, analysis_task)

    return {
        "file_path": req.file_path,
        "file_graph": file_graph,
        "call_graph": call_graph,
        "analysis": analysis
    }


@router.post("/api/ask")
async def ask_route(req: AskRequest):
    print("Requesting AI help...")
    history_id = req.history_id or f"{req.question[:20]}-{hash(req.code)}"

    if req.reset and history_id in conversation_memory:
        print("History deleted for history_id:", history_id)
        del conversation_memory[history_id]
        return {"message": "Conversation history deleted."}

    response = await run_in_threadpool(askAI, req.question, req.code, history_id)
    return response
