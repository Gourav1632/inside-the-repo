import os
import json
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path
from src.services.git_utils import extract_owner_repo, download_file
from openai import OpenAI
from openai import OpenAIError
import re
from src.services.ast_parser import detect_file_language

# Load .env from root directory
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Load OpenRouter-compatible Claude or GPT model key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("CLAUDE_API_KEY not found in environment variables.")

def get_code_from_file(repo_url: str, branch: str, relative_path: str) -> str:
    owner, repo = extract_owner_repo(repo_url)
    # Ensure path uses forward slashes (denormalize to GitHub style)
    github_path = relative_path.replace("\\", "/")
    code = download_file(owner, repo, github_path, branch)
    return code

def analyze_code_with_claude(repo_url: str, branch: str, relative_path: str) -> Dict[str, str]:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    language = detect_file_language(relative_path)
    code = get_code_from_file(repo_url, branch, relative_path)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a code analysis assistant. Given a single code file, return a JSON object with two fields: \"summary\" and \"tutorial\".\n\n"
                "- \"summary\" should be a detailed explanation of what this file/component/page does. Focus only on this file — do not refer to any other files or the whole repo.\n\n"
                "- \"tutorial\" should be an array of step-by-step explanations of how the code works. Each step must be a JSON object with:\n"
                "  - \"step\": a beginner-friendly explanation of what the code is doing in that part.\n"
                "  - \"lines\": an array of line numbers (integers) or a range of line numbers (as [start, end]).\n"
                "If a step refers to one line, use a single number (e.g., 5). If it spans multiple lines, use a two-element array (e.g., [10, 14]).\n\n"
                "Return only valid JSON with this format:\n"
                "{\n"
                "  \"summary\": \"...\",\n"
                "  \"tutorial\": [\n"
                "    { \"step\": \"This part imports dependencies.\", \"lines\": [1, 3] },\n"
                "    { \"step\": \"Defines the main component and initializes state.\", \"lines\": [5, 12] },\n"
                "    { \"step\": \"Handles side effects with useEffect.\", \"lines\": [14, 25] },\n"
                "    ...\n"
                "  ]\n"
                "}"
            )
        },
        {
            "role": "user",
            "content": code
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4o", 
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
            extra_headers={
                "HTTP-Referer": "http://localhost",  
                "X-Title": "InsideTheRepo",     
            }
        )

        response_text = completion.choices[0].message.content.strip()

        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response_text.strip(), flags=re.IGNORECASE)
        try:
            parsed = json.loads(cleaned)
            parsed["code"] = code 
            parsed["language"] = language
            return parsed
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON returned by model: {response_text}")
    except OpenAIError as e:
        print(f"Openrouter error :{str(e)}")
        return {"error": "AI service is currently unavailable. Please try again later.",
                "code":code,
                "language":language
                }


