
def split_text(text, chunk_size=1000, overlap=150):
    """Split text into overlapping chunks."""

    text = " ".join(text.split())

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap.")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to end at a word boundary
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks
