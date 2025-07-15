import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import openai
from secret import get_secret


# Load OpenAI key
openai.api_key = get_secret()

# Load embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Load FAISS index and metadata
base_dir = os.path.dirname(os.path.abspath(__file__))
faiss_index_path = os.path.join(base_dir, 'faiss_index', 'index.faiss')
metadata_path = os.path.join(base_dir, 'faiss_index', 'metadata.json')

index = faiss.read_index(faiss_index_path)
with open(metadata_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)


def retrieve_documents(query: str, top_k: int = 5):
    query_embedding = embedder.encode([query])
    D, I = index.search(np.array(query_embedding).astype('float32'), top_k)
    return [metadata[i] for i in I[0]]


def generate_answer(query: str, contexts: list, model="gpt-4o-mini"):
    context_texts = "\n\n".join(
        [f"{i+1}. {c['text']}" for i, c in enumerate(contexts)])
    prompt = f"""You are a legal assistant AI.

Use the context below to answer the question. Only rely on information in the context. If the answer isn't clear, say you don't know.

Context:
{context_texts}

Question: {query}
Answer:"""

    try:
        client = openai.OpenAI(api_key=get_secret())
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=256,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
