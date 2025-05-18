import os
import json
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path
from src.services.git_utils import extract_owner_repo, download_file
from openai import OpenAI
import re

# Load .env from root directory
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Load OpenRouter-compatible Claude or GPT model key
claude_api_key = os.getenv("CLAUDE_API_KEY")
if not claude_api_key:
    raise ValueError("CLAUDE_API_KEY not found in environment variables.")

def get_code_from_file(repo_url: str, branch: str, relative_path: str) -> str:
    owner, repo = extract_owner_repo(repo_url)
    code = download_file(owner, repo, relative_path, branch)
    return code

def analyze_code_with_claude(repo_url: str, branch: str, relative_path: str) -> Dict[str, str]:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=claude_api_key,
    )

    code = get_code_from_file(repo_url, branch, relative_path)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a code analysis assistant. Given a code snippet, return a JSON object with two fields: "
                '"summary" and "tutorial".\n\n'
                '- "summary" should be a concise and clear explanation of what the code/component/page does, written in simple terms.\n'
                '- "tutorial" should be a beginner-friendly, step-by-step guide explaining how to understand, run, modify, and extend the code. '
                "This tutorial should avoid jargon, be detailed, and help a new developer onboard easily.\n\n"
                "Return only JSON, with this structure:\n"
                '{\n'
                '  "summary": "...",\n'
                '  "tutorial": [\n'
                '    "Step 1: ...",\n'
                '    "Step 2: ...",\n'
                '    "..."\n'
                '  ]\n'
                '}'
            )
        },
        {
            "role": "user",
            "content": code
        }
    ]


    completion = client.chat.completions.create(
        model="openai/gpt-4o",  # or use "mistralai/mixtral-8x7b-instruct"
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
        extra_headers={
            "HTTP-Referer": "http://localhost",  # optional
            "X-Title": "InsideTheRepo",          # optional
        }
    )

    response_text = completion.choices[0].message.content.strip()

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response_text.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON returned by model: {response_text}")
