
from .web_loader import load_website
from .text_processor import split_text
from .embeddings import generate_embeddings
from .retriever import retrieve_chunks
from .llm_service import generate_answer


def build_knowledge_base(urls, progress_callback=None):
    """Load websites and build an in-memory knowledge base."""

    knowledge_base = []
    successful_urls = []
    failed_urls = []

    for index, url in enumerate(urls):
        try:
            website = load_website(url)

            chunks = split_text(website["text"])

            # Limit chunks per website for a faster demo
            chunks = chunks[:8]

            for chunk in chunks:
                knowledge_base.append({
                    "text": chunk,
                    "source": website["url"],
                    "title": website["title"],
                    "embedding": None
                })

            successful_urls.append({
                "url": website["url"],
                "title": website["title"]
            })

        except Exception as error:
            failed_urls.append({
                "url": url,
                "error": str(error)
            })

        if progress_callback:
            progress_callback(
                (index + 1) / len(urls),
                f"Processed website {index + 1}/{len(urls)}"
            )

    if not knowledge_base:
        raise Exception(
            "No website content could be loaded. Check your URLs."
        )

    # Generate embeddings in batches
    texts = [
        "search_document: " + item["title"] + "\n" + item["text"]
        for item in knowledge_base
    ]

    batch_size = 16

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]

        vectors = generate_embeddings(batch)

        for offset, vector in enumerate(vectors):
            knowledge_base[start + offset]["embedding"] = vector

        if progress_callback:
            progress_callback(
                min(0.95, 0.5 + 0.45 * (
                    (start + len(batch)) / len(texts)
                )),
                "Generating local embeddings..."
            )

    return knowledge_base, successful_urls, failed_urls


def answer_question(question, knowledge_base):
    """Retrieve relevant content and generate an answer."""

    results = retrieve_chunks(
        question,
        knowledge_base,
        top_k=4
    )

    if not results:
        raise Exception("No relevant website content found.")

    context_parts = []
    sources = []

    for score, item in results:
        context_parts.append(
            f"Website: {item['title']}\n"
            f"Source: {item['source']}\n"
            f"Content: {item['text']}"
        )

        if item["source"] not in sources:
            sources.append(item["source"])

    context = "\n\n".join(context_parts)

    answer = generate_answer(question, context)

    return answer, sources, results
