# 🌐 URL Intelligence Backend using LangChain, FAISS & Gemini

This project provides a Flask-based backend API that allows you to analyze and interact with the content of any public URL. It extracts webpage data, summarizes it using Google's Gemini Pro, and allows question-answering through vector-based retrieval using FAISS.

---

## 🔧 Tech Stack

- **Python + Flask** – Web server
- **LangChain** – Framework for chaining LLM and retrieval logic
- **Google Generative AI** – Gemini 1.5 Pro (chat + embeddings)
- **FAISS** – Vector database for storing and retrieving URL chunks
- **WebBaseLoader** – For scraping content from URLs
- **Chrome Extension** – For collecting URLs and sending API requests

---

## 🚀 Features

- 🔍 Analyze a webpage and generate a summary
- ❓ Ask questions about the content of a webpage
- 🧠 Uses persistent FAISS vector stores per URL
- ⚡ Caches results in memory to improve performance
- 🌐 Chrome Extension for easy integration with browser tabs

---

## 🗂️ Project Structure

```
.
extension/                # Chrome Extension folder
├── manifest.json
├── popup/
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── background.js
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
├── app.py                # Flask backend
├── .env                  # Environment variables (your Gemini API key)
├── faiss_store/          # Stores FAISS vector indices
|── README.md             # This file
└── requirements.txt      # requirements file
```

Download the `extension/` folder and load it as an unpacked extension in Chrome to use the summarizer and Q&A features directly from your browser.

---

## 📦 Installation

```bash
# To use chrome extention download the extension file
git clone https://github.com/ankitsharma5911/chrome-web-summarizer-extention.git

```

### 🛠️ API Endpoints

> ✅ **Production Backend**: [https://chrome-web-summarizer-extention.onrender.com](https://chrome-web-summarizer-extention.onrender.com)

### `GET /status`

Returns a simple status check.

### `POST /analyze`

Summarizes the content of a given URL.

```json
{
  "url": "https://example.com"
}
```

**Response:**

```json
{
  "summary": "...",
  "num_chunks": 5
}
```

### `POST /ask`

Ask a question based on previously analyzed content.

```json
{
  "url": "https://example.com",
  "question": "What is the main topic?"
}
```

**Response:**

```json
{
  "answer": "The article is about..."
}
```

### `POST /reset-cache`

Clears the in-memory cache.

---

## 🧩 Chrome Extension Usage

1. Go to `chrome://extensions/` in your Chrome browser.
2. Enable **Developer mode** (top right).
3. Click **Load unpacked** and select the `extension/` folder.
4. The extension icon will appear in your toolbar.
5. Click the icon to:
   - Get summary of the current tab
   - Ask questions about the current page

The extension sends the current URL to your deployed backend at:
[https://chrome-web-summarizer-extention.onrender.com](https://chrome-web-summarizer-extention.onrender.com)

---

## 💡 Future Improvements

- Chrome extension enhancements (history, UI feedback)
- Streamlit or React frontend
- Advanced chain types (map-reduce, refine)
- Multiple page ingestion

---

## 📜 License

MIT License

---

## 🙌 Acknowledgements

- [LangChain](https://github.com/langchain-ai/langchain)
- [FAISS by Facebook AI](https://github.com/facebookresearch/faiss)
- [Google Generative AI SDK](https://github.com/google/generative-ai-python)

