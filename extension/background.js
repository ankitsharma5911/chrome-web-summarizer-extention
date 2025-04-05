// This is a minimal background script for the extension
// It mostly handles communication with the Python backend

chrome.runtime.onInstalled.addListener(() => {
    console.log('Web Content Analyzer extension installed');
  });
  
  // You can add message listeners here if needed for communication
  // between different parts of your extension
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'checkBackendStatus') {
      fetch('https://chrome-web-summarizer-extention.onrender.com//status')
        .then(response => {
          if (response.ok) {
            return response.json();
          }
          throw new Error('Backend not available');
        })
        .then(data => {
          sendResponse({ success: true, data });
        })
        .catch(error => {
          sendResponse({ success: false, error: error.message });
        });
      return true; // Indicates that the response is sent asynchronously
    }
  });