from fastapi import APIRouter
from pydantic import BaseModel
from src.services.get_history import get_git_history
from src.services.ast_parser import parse_code

router = APIRouter()

# Define a request model for analyzing repo
class RepoRequest(BaseModel):
    repo_url: str
    branch: str = 'main'  # Default to the main branch

# Endpoint for analyzing a repo
@router.post("/analyze-repo")
async def analyze_repo(req: RepoRequest):
    """
    Analyzes the provided repo and returns analysis results such as the
    most frequently changed files, the critical code paths, and architectural insights.
    """
    git_history = get_git_history(req.repo_url, req.branch)
    code_analysis = parse_code(req.repo_url, req.branch)
    
    return {
        "git_history": git_history,
        "code_analysis": code_analysis,
    }
