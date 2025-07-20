from flask import Flask, render_template_string, request
import subprocess
import os

app = Flask(__name__)

# HTML page for the Pizza Tracker
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Domino's Pizza Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f8f8f8; text-align: center; padding: 50px; }
        button { background-color: #ff4500; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 8px; cursor: pointer; }
        button:hover { background-color: #e03e00; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>🍕 Domino's Pizza Tracker</h1>
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
            # Trigger the Control-M Event (NewPizzaOrder)
            subprocess.run(["ctm", "run", "event::send", "NewPizzaOrder"], check=True)
            message = "Pizza order placed! Your Control‑M workflow is running."
        except subprocess.CalledProcessError as e:
            message = f"Error triggering Control‑M event: {e}"
    return render_template_string(HTML_PAGE, message=message)

if __name__ == "__main__":
    # Read hostname, port, and participant ID from Instruqt environment
    HOSTNAME = os.getenv("HOSTNAME", "app")
    PORT = os.getenv("PORT", "5000")
    PARTICIPANT_ID = os.getenv("PARTICIPANT_ID", "user")

    # Flask will bind to 0.0.0.0 (Instruqt proxy maps it to the HTTPS URL)
    print(f"App is starting... Access it at:")
    print(f"https://{HOSTNAME}-{PORT}-{PARTICIPANT_ID}.env.play.instruqt.com")

    # No self-signed SSL needed — Instruqt provides valid certs via proxy
    app.run(host="0.0.0.0", port=int(PORT), debug=True)
