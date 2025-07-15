import os
import fitz
import docx
import faiss
import json
from sentence_transformers import SentenceTransformer


def extract_text_from_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(docx_path: str):
    doc = docx.Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def extract_text(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text, chunk_size=500):
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    overlapped_chunks = []
    for i in range(0, len(chunks), 1):
        start = max(0, i - 1)
        overlapped_chunks.append(" ".join(chunks[start:i+1]))
    return overlapped_chunks


def build_index_from_folder(folder_path: str, persist_directory: str = "./faiss_index"):
    os.makedirs(persist_directory, exist_ok=True)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = []
    metadata = []
    chunk_id = 0

    for fname in os.listdir(folder_path):
        if not (fname.lower().endswith('.pdf') or fname.lower().endswith('.docx')):
            continue
        fpath = os.path.join(folder_path, fname)
        try:
            text = extract_text(fpath)
        except Exception as e:
            print(f"Failed to extract {fname}: {e}")
            continue
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            emb = model.encode(chunk)
            embeddings.append(emb)
            metadata.append({
                "file": fname,
                "chunk_id": i,
                "text": chunk
            })
            chunk_id += 1

    if not embeddings:
        print("No embeddings to index.")
        return

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))

    faiss.write_index(index, os.path.join(persist_directory, "index.faiss"))

    with open(os.path.join(persist_directory, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Indexed {len(embeddings)} chunks from {len(metadata)} documents.")


if __name__ == "__main__":
    import numpy as np
    build_index_from_folder("../sample_docs")
