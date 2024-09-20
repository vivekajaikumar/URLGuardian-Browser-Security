import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Custom logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set this to INFO to avoid the default request logs
    format='%(asctime)s %(levelname)s: %(message)s',  # Customize the log format
)

# In-memory storage for URLs
urls = []

@app.route('/log_urls', methods=['POST', 'OPTIONS'])
def log_urls():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    data = request.get_json()
    global urls
    urls = data.get('urls', [])
    
    # Log the URLs to the console
    print("Received URLs:")
    for url in urls:
        print(url)
    
    response = jsonify({"status": "success", "count": len(urls)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/log_urls', methods=['GET'])
def get_urls():
    response = jsonify({'urls': urls})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=False, port=5000)
