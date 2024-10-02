import joblib
import logging
import requests
import threading
import tkinter as tk
from flask import Flask, request, jsonify
from tkinter import ttk, scrolledtext, PhotoImage, messagebox

# Flask app for URL logging
app = Flask(__name__)

# Custom logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

# In-memory storage for URLs
urls = []


@app.route("/log_urls", methods=["POST", "OPTIONS"])
def log_urls():
    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response

    data = request.get_json()
    global urls
    urls = data.get("urls", [])

    # Log the URLs to the console
    logging.info(f"Received URLs: {urls}")

    response = jsonify({"status": "success", "count": len(urls)})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/log_urls", methods=["GET"])
def get_urls():
    response = jsonify({"urls": urls})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# Load the trained vectorizer and model for URL classification
vectorizer = joblib.load("models/vectorizer.pkl")
svm_model = joblib.load("models/svm_model.pkl")


# Function to predict URLs
def predict_urls(urls):
    results = []
    for url in urls:
        if isinstance(url, str):  # Ensure url is a string
            try:
                url = url.strip()

                # Check if the URL starts with 'http://'
                if url.startswith("http://"):
                    results.append((url, "Bad"))  # Mark 'http' URLs as bad
                else:
                    # Transform the URL using the loaded vectorizer
                    url_features = vectorizer.transform([url])

                    # Make the prediction
                    prediction = svm_model.predict(url_features)

                    # Append result
                    results.append((url, "Bad" if prediction[0] == 1 else "Good"))
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
                logging.error(
                    "Fetched data is not in expected format or contains non-string URLs."
                )
        else:
            logging.error(f"Error fetching URLs: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
    return []


# Function to update the GUI with predictions
def update_gui():
    # Fetch URLs from the Flask server
    urls = fetch_urls()

    if urls:
        # Clear previous results
        app.result_area.delete("1.0", tk.END)

        # Predict classifications for fetched URLs
        predictions = predict_urls(urls)

        # Display the predictions in the GUI
        for url, result in predictions:
            if result == "Good":
                app.result_area.image_create(
                    tk.END, image=app.tick_icon
                )  # Add tick icon
            else:
                app.result_area.image_create(
                    tk.END, image=app.cross_icon
                )  # Add cross icon
            app.result_area.insert(
                tk.END, f" {url} - {result}\n"
            )  # Insert URL after icon
    else:
        app.result_area.insert(tk.END, "No URLs received or an error occurred.\n")

    # Schedule the next check after 10 seconds
    app.root.after(10000, update_gui)  # Fetch and update every 10 seconds


# Flask app runner in a separate thread
def run_flask_app():
    app.run(debug=False, port=5000, use_reloader=False)


class URLGuardianGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Guardian")
        self.root.geometry("900x700")
        self.root.configure(bg="#282c34")

        self.setup_styles()
        self.create_widgets()

        # Load icons (ensure the paths are correct)
        self.load_icons()

        # Start Flask in a separate thread
        flask_thread = threading.Thread(target=run_flask_app)
        flask_thread.start()

        # Start updating the GUI
        self.root.after(1000, update_gui)  # Start after 1 second

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#282c34")
        style.configure(
            "TButton",
            background="#61dafb",
            foreground="#282c34",
            font=("Helvetica Neue", 12),
            padding=10,
        )
        style.map(
            "TButton",
            background=[("active", "#4fa8d5")],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "TLabel",
            background="#282c34",
            foreground="#ffffff",
            font=("Helvetica Neue", 12),
        )

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(
            main_frame,
            text="URL Guardian",
            font=("Helvetica Neue", 24, "bold"),
            foreground="#61dafb",
        )
        title_label.pack(pady=(0, 20))

        self.result_area = scrolledtext.ScrolledText(
            main_frame,
            width=80,
            height=20,
            font=("Helvetica Neue", 12),
            bg="#2c2f33",
            fg="#ffffff",
        )
        self.result_area.pack(pady=10, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)

        refresh_button = ttk.Button(
            button_frame, text="Refresh Now", command=self.update_gui_with_status
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        clear_button = ttk.Button(
            button_frame, text="Clear Results", command=self.clear_results
        )
        clear_button.pack(side=tk.LEFT)

        self.status_label = ttk.Label(main_frame, text="Waiting for URLs...")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    def clear_results(self):
        self.result_area.delete("1.0", tk.END)

    def update_status(self, message):
        self.status_label.config(text=message)

    def load_icons(self):
        try:
            self.tick_icon = PhotoImage(file="gui_icons/tick.png")
            self.cross_icon = PhotoImage(file="gui_icons/cross.png")
        except Exception as e:
            messagebox.showerror("Icon Load Error", f"Could not load icons: {e}")

    def update_gui_with_status(self):
        update_gui()


if __name__ == "__main__":
    root = tk.Tk()
    app = URLGuardianGUI(root)
    root.mainloop()
