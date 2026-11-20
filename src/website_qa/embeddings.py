
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "nomic-embed-text:latest"


def generate_embeddings(texts):
    """Generate local embeddings using Ollama."""

    if isinstance(texts, str):
        texts = [texts]

    if not texts:
        return []

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": EMBEDDING_MODEL,
                "input": texts
            },
            timeout=180
        )

        response.raise_for_status()

        data = response.json()
        embeddings = data.get("embeddings", [])

        if len(embeddings) != len(texts):
            raise ValueError("Ollama returned an unexpected number of embeddings.")

        return embeddings

    except requests.RequestException as error:
        raise Exception(
            f"Ollama embedding failed. Check whether Ollama is running: {error}"
        )


def generate_embedding(text):
    """Generate an embedding for one text."""

    return generate_embeddings([text])[0]
