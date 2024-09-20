import tkinter as tk
from tkinter import scrolledtext
import joblib
import requests
import threading
import time

# Load the trained vectorizer and model
vectorizer = joblib.load('models/vectorizer.pkl')
svm_model = joblib.load('models/svm_model.pkl')

# Function to predict URLs
def predict_urls(urls):
    results = []
    for url in urls:
        if isinstance(url, str):  # Ensure url is a string
            try:
                # Transform the URL using the loaded vectorizer
                url_features = vectorizer.transform([url.strip()])

                # Make the prediction
                prediction = svm_model.predict(url_features)

                # Append result
                results.append((url, 'Bad' if prediction[0] == 1 else 'Good'))
            except Exception as e:
                results.append((url, f"Error: {str(e)}"))
        else:
            results.append((url, "Error: URL is not a string"))
    
    return results

# Function to fetch URLs from the Flask server
def fetch_urls():
    try:
        response = requests.get("http://127.0.0.1:5000/log_urls")
        if response.status_code == 200:
            data = response.json()
            urls = data.get("urls", [])
            if isinstance(urls, list) and all(isinstance(url, str) for url in urls):
                return urls
            else:
                print("Fetched data is not in expected format or contains non-string URLs.")
        else:
            print(f"Error fetching URLs: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    return []

# Function to update the GUI with predictions
def update_gui():
    # Step 1: Fetch URLs from the Flask server
    urls = fetch_urls()
    
    # Step 2: Check if URLs were fetched
    if urls:
        # Clear previous results
        result_area.delete("1.0", tk.END)
        
        # Step 3: Predict classifications for fetched URLs
        predictions = predict_urls(urls)
        
        # Step 4: Display the predictions in the GUI
        for url, result in predictions:
            result_area.insert(tk.END, f"{url} - {result}\n")
    else:
        result_area.insert(tk.END, "No URLs received or an error occurred.\n")
    
    # Schedule the next check after 10 seconds
    root.after(10000, update_gui)  # Fetch and update every 10 seconds

# Create the main window
root = tk.Tk()
root.title("URL Classification")

# Set window size and background color
root.geometry("1920x1080")
root.configure(bg="#f0f0f0")

# Create a frame for better organization
frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a bold label
bold_label = tk.Label(frame, text="URLGuardian", font=("Arial", 16, "bold"), bg="#f0f0f0")
bold_label.pack(pady=10)

# Create a label for results
result_label = tk.Label(frame, text="Results:", font=("Arial", 12), bg="#f0f0f0")
result_label.pack(pady=5)

# Create a text area to display the results
result_area = scrolledtext.ScrolledText(frame, width=60, height=15, font=("Arial", 12), bd=2, relief="groove")
result_area.pack(pady=10)

# Start updating the GUI
root.after(1000, update_gui)  # Start after 1 second

# Run the GUI event loop
root.mainloop()
