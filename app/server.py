from flask import Flask, request, jsonify
from app.model import retrieve_documents, generate_answer
import os

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})


@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query')
    if not user_query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    top_chunks = retrieve_documents(user_query, top_k=5)
    answer = generate_answer(user_query, top_chunks)
    citations = [
        {"text": c["text"], "source": c["file"]}
        for c in top_chunks
    ]
    return jsonify({
        "answer": answer,
        "citations": citations
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
