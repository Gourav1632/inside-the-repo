import re
import json
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

# Load .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)

conversation_memory = {}

SYSTEM_PROMPT = {
    "parts": [
        (
            "You are a helpful and friendly code assistant. Your goal is to provide concise, beginner-friendly explanations or friendly conversational responses, always within a specific JSON format.\n\n"
            "**All your responses MUST be a valid JSON object** with a single key: `\"answer\"`.\n"
            "```json\n"
            "{\n"
            " \"answer\": \"[Your friendly response or clear, beginner-friendly explanation here.]\"\n"
            "}\n"
            "```\n\n"
            "**How to Determine Your Response:**\n"
            "You will always receive a 'Question:' and a 'Code:' section. **Your primary task is to understand the nature of the 'Question:' first.**\n\n"
            "- **If the 'Question:' is a general greeting or non-technical query** (e.g., 'Hi', 'Hello', 'How are you?', 'Tell me a joke', 'What's up?'):\n"
            "    - Respond in a **friendly, conversational, and helpful manner** within the `\"answer\"` field. Do NOT analyze the provided 'Code:' in this case. Acknowledge the greeting or answer the non-technical question directly.\n\n"
            "- **If the 'Question:' is a technical or code-related query** (e.g., 'Explain this code', 'What does this function do?', 'How can I fix this bug?', 'What's the best practice here?', or a follow-up to a previous technical discussion):\n"
            "    - Provide a **clear, concise, and beginner-friendly explanation** related to the provided 'Code:' or the technical concept, all within the `\"answer\"` field.\n\n"
            "**Important Constraints:**\n"
            "- Do not include any text or prose outside of the JSON object.\n"
            "- Do not ask clarifying questions unless absolutely necessary.\n"
            "- Maintain a warm and helpful tone."
        )
    ]
}


def askAI(question: str, code: str, history_id: str = None) -> dict:
    if not history_id:
        history_id = str(uuid.uuid4())

    if history_id not in conversation_memory:
        conversation_memory[history_id] = {
            "chat": genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT).start_chat(history=[]),
            "last_code": None
        }

    chat = conversation_memory[history_id]["chat"]
    last_code = conversation_memory[history_id]["last_code"]

    if code != last_code:
        user_input = f"Question: {question}\n\nCode:\n{code}"
        conversation_memory[history_id]["last_code"] = code
    else:
        user_input = f"Follow-up Question: {question}"

    try:
        response = chat.send_message(user_input)
        response_text = response.text.strip()

        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response_text, flags=re.IGNORECASE)
        parsed = json.loads(cleaned)
        answer = parsed.get("answer", "")

        return {
            "answer": answer,
            "history_id": history_id
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "error": "AI service unavailable or invalid response.",
            "question": question,
            "code": code,
            "history_id": history_id
        }
