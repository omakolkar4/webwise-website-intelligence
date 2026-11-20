# 🌐 Website Q&A Bot

An AI-powered chatbot that reads website content and answers
user questions using local Ollama models.

## Features

- Load 5–10 website URLs
- Extract website content
- Split content into text chunks
- Generate embeddings using Ollama
- Retrieve relevant website information
- Generate answers using Qwen 2.5
- Display source URLs
- Streamlit user interface

## Technologies

- Python
- Streamlit
- BeautifulSoup
- Requests
- Ollama
- Qwen 2.5 (3B)
- Nomic Embed Text

## Installation

Install Ollama and download the models:

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text