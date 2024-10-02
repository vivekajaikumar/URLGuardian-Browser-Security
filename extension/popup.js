// Fetch saved URLs from local storage and display them
chrome.storage.local.get("savedURLs", (result) => {
  const urls = result.savedURLs || [];
  const urlList = document.getElementById("url-list");
  urlList.innerHTML = ""; // Clear existing list

  urls.forEach((url) => {
    const li = document.createElement("li");
    li.textContent = url;
    urlList.appendChild(li);
  });
});
