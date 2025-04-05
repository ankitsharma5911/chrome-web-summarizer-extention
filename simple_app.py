from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Cache to store scraped content
url_cache = {}

def get_url_content(url):
    """Scrape content from a URL using Beautiful Soup"""
    if url in url_cache:
        return url_cache[url]
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator='\n')
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Remove blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit text length to avoid token limits
        max_chars = 15000  # Adjust depending on your LLM's token limit
        text = text[:max_chars]
        
        url_cache[url] = text
        return text
    
    except Exception as e:
        print(f"Error scraping URL {url}: {str(e)}")
        raise

@app.route('/status', methods=['GET'])
def status():
    """Check if the backend is running"""
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a URL and return a summary"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        # Check OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({"error": "OpenAI API key not found. Check your .env file."}), 500
        
        # Get content
        content = get_url_content(url)
        
        # Initialize LLM
        llm = ChatOpenAI(temperature=0)
        
        # Generate summary
        prompt = f"""Please summarize the following web page content concisely:
        
        URL: {url}
        
        CONTENT:
        {content}
        
        Provide a clear, informative summary highlighting the main points.
        """
        
        messages = [HumanMessage(content=prompt)]
        summary = llm(messages).content
        
        return jsonify({
            "url": url,
            "summary": summary
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /analyze: {str(e)}\n{error_details}")
        return jsonify({"error": f"{str(e)}"}), 500

@app.route('/ask', methods=['POST'])
def ask():
    """Ask a question about the content of a URL"""
    data = request.json
    url = data.get('url')
    question = data.get('question')
    
    if not url or not question:
        return jsonify({"error": "URL and question are required"}), 400
    
    try:
        # Check OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({"error": "OpenAI API key not found. Check your .env file."}), 500
        
        # Get content
        content = get_url_content(url)
        
        # Initialize LLM
        llm = ChatOpenAI(temperature=0)
        
        # Generate answer
        prompt = f"""I have the following web page content:
        
        URL: {url}
        
        CONTENT:
        {content}
        
        Based ONLY on the information in the content above, please answer this question: {question}
        If the answer cannot be found in the content, please say so.
        """
        
        messages = [HumanMessage(content=prompt)]
        answer = llm(messages).content
        
        return jsonify({
            "url": url,
            "question": question,
            "answer": answer
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /ask: {str(e)}\n{error_details}")
        return jsonify({"error": f"{str(e)}"}), 500

if __name__ == '__main__':
    print(f"OpenAI API Key detected: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    app.run(debug=True, port=5000)