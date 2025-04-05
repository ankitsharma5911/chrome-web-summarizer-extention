from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import hashlib
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv
import pickle

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Create a cache to store processed documents by URL
url_cache = {}

# Helper function to create a safe file name from a URL
def safe_file_name(url):
    return hashlib.md5(url.encode()).hexdigest()

def process_url(url):
    """Process a URL by loading, splitting, and embedding its content"""
    file_name = safe_file_name(url)
    faiss_path = f"./faiss_store/{file_name}"
    pkl_path = f"{faiss_path}.pkl"

    # Initialize embedding model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # Check cache first
    if url in url_cache:
        return url_cache[url]

    # Load FAISS if already exists
    if os.path.exists(faiss_path) and os.path.exists(pkl_path):
        with open(pkl_path, "rb") as f:
            faiss_index = pickle.load(f)
        vectorstore = FAISS.load_local(faiss_path, embeddings, faiss_index)
        url_cache[url] = {
            "documents": None,
            "splits": None,
            "vectorstore": vectorstore
        }
        return url_cache[url]

    # Load the webpage content
    loader = WebBaseLoader(url)
    documents = loader.load()

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    # Create FAISS vector store
    vectorstore = FAISS.from_documents(splits, embeddings)
    faiss_index = vectorstore.index

    # Save FAISS index and vectorstore
    os.makedirs("./faiss_store", exist_ok=True)
    vectorstore.save_local(faiss_path)
    with open(pkl_path, "wb") as f:
        pickle.dump(faiss_index, f)

    # Store in cache
    url_cache[url] = {
        "documents": documents,
        "splits": splits,
        "vectorstore": vectorstore
    }

    return url_cache[url]

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/reset-cache', methods=['POST'])
def reset_cache():
    url_cache.clear()
    return jsonify({"status": "ok", "message": "Cache cleared"})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        processed = process_url(url)
        documents = processed["documents"]

        if not documents:
            return jsonify({"error": "Document data not available for summary."}), 500

        llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro', temperature=0)
        summary_chain = load_summarize_chain(llm, chain_type="stuff")
        summary = summary_chain.run(documents)

        return jsonify({
            "url": url,
            "summary": summary,
            "num_chunks": len(processed["splits"]) if processed["splits"] else 0
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    url = data.get('url')
    question = data.get('question')

    if not url or not question:
        return jsonify({"error": "URL and question are required"}), 400

    try:
        processed = process_url(url)
        vectorstore = processed["vectorstore"]

        llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro', temperature=0)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )

        answer = qa_chain.run(question)

        return jsonify({
            "url": url,
            "question": question,
            "answer": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
