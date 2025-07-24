from flask import Flask, render_template_string, request
import requests, json, os, sys

app = Flask(__name__)

CTM_API_ENDPOINT = os.getenv("CTM_API_ENDPOINT", "replace-with-endpoint")
CTM_API_TOKEN = os.getenv("CTM_API_TOKEN", "replace-with-token")
CTM_SERVER = os.getenv("CTM_SERVER", "replace-with-ctm-server")
CTM_FOLDER = os.getenv("CTM_FOLDER", "replace-with-ctm-folder")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Telco Onboarding Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #eef2f3; text-align: center; padding: 50px; }
        button { background-color: #0073e6; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 8px; cursor: pointer; }
        button:hover { background-color: #005bb5; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>📱 Telco Onboarding Tracker</h1>
    <p>Click below to simulate a new mobile customer activation (this will trigger your Control‑M workflow).</p>
    <form method="POST">
        <button type="submit">Start Onboarding</button>
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
            payload = {"ctm": CTM_SERVER, "folder": CTM_FOLDER}
            headers = {"x-api-key": CTM_API_TOKEN, "Content-Type": "application/json", "Accept": "application/json"}
            response = requests.post(f"{CTM_API_ENDPOINT}/run/order", headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                message = "Customer onboarding triggered via Control‑M API."
            else:
                message = f"Failed to trigger workflow. Error: {response.status_code} - {response.text}"
        except Exception as e:
            message = f"Error connecting to Control‑M API: {str(e)}"
    return render_template_string(HTML_PAGE, message=message)

if __name__ == "__main__":
    HOSTNAME = os.getenv("HOSTNAME", "app")
    PORT = os.getenv("PORT", "5000")
    PARTICIPANT_ID = os.getenv("PARTICIPANT_ID", "user")
    if os.fork(): os._exit(0)
    print(f"Telco Tracker app starting at: https://{HOSTNAME}-{PORT}-{PARTICIPANT_ID}.env.play.instruqt.com")
    sys.stdout = open("/home/controlm/telco_tracker.log", "a")
    sys.stderr = sys.stdout
    app.run(host="0.0.0.0", port=int(PORT), debug=False)
