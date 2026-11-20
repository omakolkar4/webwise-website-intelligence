
import math
import re

from .embeddings import generate_embedding


STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "of", "for",
    "to", "in", "on", "and", "or", "how", "does", "do",
    "can", "could", "explain", "tell", "me", "about",
    "please", "used", "use"
}


def cosine_similarity(vector_a, vector_b):
    dot = sum(a * b for a, b in zip(vector_a, vector_b))

    mag_a = math.sqrt(sum(a * a for a in vector_a))
    mag_b = math.sqrt(sum(b * b for b in vector_b))

    if not mag_a or not mag_b:
        return 0.0

    return dot / (mag_a * mag_b)


def tokenize(text):
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def keyword_score(question, content):
    question_words = tokenize(question) - STOP_WORDS
    content_words = tokenize(content)

    if not question_words:
        return 0.0

    matched = question_words.intersection(content_words)

    return len(matched) / len(question_words)


def retrieve_chunks(question, knowledge_base, top_k=4):
    """Hybrid retrieval using semantic and keyword relevance."""

    if not knowledge_base:
        return []

    query_embedding = generate_embedding(
        "search_query: " + question
    )

    scored_results = []

    for item in knowledge_base:
        semantic = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        keyword = keyword_score(
            question,
            item["title"] + " " + item["text"]
        )

        # Combine semantic and keyword relevance
        final_score = (0.80 * semantic) + (0.20 * keyword)

        scored_results.append((final_score, item))

    scored_results.sort(
        key=lambda result: result[0],
        reverse=True
    )

    # Avoid allowing one website to dominate the results
    selected = []
    source_counts = {}

    for score, item in scored_results:
        source = item["source"]

        if source_counts.get(source, 0) >= 2:
            continue

        selected.append((score, item))
        source_counts[source] = source_counts.get(source, 0) + 1

        if len(selected) >= top_k:
            break

    return selected
