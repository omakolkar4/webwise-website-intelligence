
import requests

MODEL = "qwen2.5:3b"

API_URL = "http://localhost:11434/api/chat"


def generate_answer(question, context):
    """Generate a grounded answer using local Ollama."""

    prompt = f"""
You are a Website Question Answering Assistant.

Answer using ONLY the website content provided below.

Rules:
1. Do not use outside knowledge.
2. Give a simple and clear answer.
3. If information is unavailable, say so.
4. Never invent facts.
5. Keep the answer relevant to the question.

WEBSITE CONTENT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You answer questions strictly from supplied "
                    "website context. Never invent information."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 1000
        }
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get("message", {}).get("content", "")

        if not answer:
            raise Exception("Ollama returned an empty answer.")

        return answer.strip()

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Cannot connect to Ollama. Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:
        raise Exception(
            "Ollama request timed out. Try a shorter question."
        )

    except requests.exceptions.RequestException as error:
        raise Exception(f"Ollama request failed: {error}")
