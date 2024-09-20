// background.js

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.urls) {
      // Save URLs to local storage
      chrome.storage.local.set({ savedURLs: message.urls }, () => {
        console.log('URLs saved:', message.urls);
      });
    }
  });
  