import re
import json
import uuid
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI, OpenAIError
import os

# Load .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables.")

conversation_memory = {}

def askAI(question: str, code: str, history_id: str = None) -> dict:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    if not history_id:
        history_id = str(uuid.uuid4())

    # Initialize conversation if it doesn't exist
    if history_id not in conversation_memory:
        conversation_memory[history_id] = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful code assistant. When the user provides a code snippet and a question, "
                        "respond ONLY with a JSON object containing one field:\n"
                        "- \"answer\": A clear, beginner-friendly answer to the user's question.\n\n"
                        "Respond ONLY with valid JSON, nothing else."
                    )
                }
            ],
            "last_code": None
        }

    messages = conversation_memory[history_id]["messages"]
    last_code = conversation_memory[history_id]["last_code"]

    # Only include full code if it has changed
    if code != last_code:
        user_message = f"Question: {question}\n\nCode:\n{code}"
        conversation_memory[history_id]["last_code"] = code
    else:
        user_message = f"Follow-up Question: {question}"

    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
            extra_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "InsideTheRepo",
            }
        )

        message_content = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": message_content})

        # Remove code block markers, if any
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", message_content, flags=re.IGNORECASE)
        parsed_json = json.loads(cleaned)
        answer = parsed_json.get("answer", "")

        return {
            "answer": answer,
            "history_id": history_id
        }

    except (OpenAIError, json.JSONDecodeError, ValueError) as e:
        print(f"Error: {str(e)}")
        return {
            "error": "AI service unavailable or invalid response.",
            "question": question,
            "code": code,
            "history_id": history_id
        }
