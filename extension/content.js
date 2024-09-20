// content.js

// Function to extract URLs from Google search results
function extractURLs() {
  const links = document.querySelectorAll('a'); // Select all anchor elements
  const urls = [];

  // Iterate through each link and extract the href attribute
  links.forEach(link => {
    const href = link.href;

    // Filter out unwanted URLs (e.g., ads, navigation links)
    if (href.includes('http') && !href.includes('google.com')) {
      urls.push(href);
    }
  });

  // Send the URLs to the background script
  chrome.runtime.sendMessage({ urls: urls });

  // Send the URLs to the Flask server
  fetch('http://localhost:5000/log_urls', { // Adjust the URL as necessary
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ urls: urls })
  })
  .then(response => response.json())
  .then(data => console.log('Server response:', data))
  .catch(error => console.error('Error sending URLs to server:', error));
}

// Run the function when the page loads
extractURLs();
