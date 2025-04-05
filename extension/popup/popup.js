document.addEventListener('DOMContentLoaded', async () => {
    // Get current tab URL
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentUrl = tabs[0].url;
    
    // Display current URL
    document.getElementById('current-url').textContent = currentUrl;
    
    // Analyze button click handler
    document.getElementById('analyze-btn').addEventListener('click', async () => {
      showLoading(true);
      try {
        const result = await analyzeUrl(currentUrl);
        document.getElementById('analysis-result').textContent = result.summary;
        document.getElementById('result-container').style.display = 'block';
        document.querySelector('.interaction-section').style.display = 'block';
      } catch (error) {
        document.getElementById('analysis-result').textContent = `Error: ${error.message}`;
        document.getElementById('result-container').style.display = 'block';
      } finally {
        showLoading(false);
      }
    });
    
    // Ask question button click handler
    document.getElementById('ask-btn').addEventListener('click', async () => {
      const question = document.getElementById('question-input').value.trim();
      if (!question) return;
      
      const responseContainer = document.getElementById('response-container');
      responseContainer.innerHTML = '<div class="loading-text">Getting response...</div>';
      
      try {
        const response = await askQuestion(currentUrl, question);
        responseContainer.textContent = response.answer;
      } catch (error) {
        responseContainer.textContent = `Error: ${error.message}`;
      }
    });
  });
  
  // Show/hide loading indicator
  function showLoading(show) {
    document.getElementById('loading-indicator').style.display = show ? 'flex' : 'none';
    document.getElementById('analyze-btn').disabled = show;
  }
  
  // Send URL to Python backend for analysis
  async function analyzeUrl(url) {
    const response = await fetch('http://localhost:5000/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });
    
    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }
    
    return response.json();
  }
  
  // Send question to Python backend
  async function askQuestion(url, question) {
    const response = await fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, question }),
    });
    
    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }
    
    return response.json();
  }