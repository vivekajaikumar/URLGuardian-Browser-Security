// Function to extract URLs from any website
function extractURLs() {
  const links = document.querySelectorAll("a"); // Select all anchor elements
  const urls = [];

  // Iterate through each link and extract the href attribute
  links.forEach((link) => {
    const href = link.href;

    // Only include valid http/https URLs (exclude other protocols)
    if (href.startsWith("http")) {
      urls.push(href);
    }
  });

  // Send the URLs to the background script
  chrome.runtime.sendMessage({ urls: urls });

  // Send the URLs to the Flask server (update the server endpoint as needed)
  fetch("http://localhost:5000/log_urls", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ urls: urls }),
  })
    .then((response) => response.json())
    .then((data) => console.log("Server response:", data))
    .catch((error) => console.error("Error sending URLs to server:", error));
}

// Run the function when the page loads
extractURLs();

// Optionally, listen for changes on the page and extract new URLs
const observer = new MutationObserver(() => {
  extractURLs();
});

// Start observing the document for changes
observer.observe(document.body, { childList: true, subtree: true });
