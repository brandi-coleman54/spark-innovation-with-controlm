from flask import Flask, render_template_string, request
import requests
import json
import subprocess
import os
import sys

app = Flask(__name__)

# Read Control-M API variables from environment (set these in Instruqt!)
CTM_API_ENDPOINT = os.getenv("CTM_API_ENDPOINT", "replace-with-endpoint")
CTM_API_TOKEN = os.getenv("CTM_API_TOKEN", "replace-with-token")
CTM_SERVER = os.getenv("CTM_SERVER", "replace-with-ctm-server")
CTM_FOLDER = os.getenv("CTM_FOLDER", "replace-with-ctm-folder")

# HTML page for the Pizza Tracker
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Pizza Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f8f8f8; text-align: center; padding: 50px; }
        button { background-color: #ff4500; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 8px; cursor: pointer; }
        button:hover { background-color: #e03e00; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>🍕 Sample Pizza Tracker</h1>
    <p>Click below to simulate a new pizza order (this will trigger your Control‑M workflow).</p>
    <form method="POST">
        <button type="submit">Place Order</button>
    </form>
    {% if message %}
        <p style="color:green; font-weight:bold;">{{ message }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        try:
             # Build JSON payload for Control-M API
            payload = {
                "ctm": CTM_SERVER,
                "folder": CTM_FOLDER
            }
            # Send API request to trigger the workflow
            headers = {
                "x-api-key": CTM_API_TOKEN,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.post(f"{CTM_API_ENDPOINT}/run/order", headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                message = "Pizza order placed! Workflow ordered via API."
            else:
                message = f"Failed to trigger workflow. Error: {response.status_code} - {response.text}"
        except Exception as e:
            message = f"Error connecting to Control-M API: {str(e)}"
    return render_template_string(HTML_PAGE, message=message)

if __name__ == "__main__":
    # Read hostname, port, and participant ID from Instruqt environment
    HOSTNAME = os.getenv("HOSTNAME", "app")
    PORT = os.getenv("PORT", "5000")
    PARTICIPANT_ID = os.getenv("PARTICIPANT_ID", "user")
    
    # Daemonize (run in the background)
    if os.fork():
        # Parent process exits, leaving Flask running in the background
        os._exit(0)

    print(f"App is starting in the background... Access it at:")
    print(f"https://{HOSTNAME}-{PORT}-{PARTICIPANT_ID}.env.play.instruqt.com")
    
    # Redirect output to a log file
    sys.stdout = open("/home/controlm/pizza_tracker.log", "a")
    sys.stderr = sys.stdout

    # Run Flask server
    app.run(host="0.0.0.0", port=int(PORT), debug=False)
