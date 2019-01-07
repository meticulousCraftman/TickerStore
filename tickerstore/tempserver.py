from flask import Flask, request, redirect
from upstox_api.api import *
import os


app = Flask(__name__)


@app.route("/")
def demo():
    """Redirects user to login page"""
    s = Session(os.getenv("UPSTOX_API_KEY"))
    s.set_redirect_uri(os.getenv("UPSTOX_REDIRECT_URI"))
    s.set_api_secret(os.getenv("UPSTOX_API_SECRET"))
    url = s.get_login_url()
    return redirect(url)


@app.route("/callback", methods=["GET"])
def callback():
    """Receives the callback from server and gets the access token."""
    temp_server_shutdown_url = "http://127.0.0.1:5000/shutdown"
    code = request.args["code"]
    s = Session(os.getenv("UPSTOX_API_KEY"))
    s.set_redirect_uri(os.getenv("UPSTOX_REDIRECT_URI"))
    s.set_api_secret(os.getenv("UPSTOX_API_SECRET"))
    s.set_code(code)
    access_token = s.retrieve_access_token()
    html_code = """
        Access token : %s
        <br>
        <b>Go back to the terminal now!</b>
        <script>
            setInterval(function() {window.location="%s"}, 2000);
        </script>
        """ % (
        access_token,
        temp_server_shutdown_url,
    )
    app.queue.put(access_token)
    return html_code


@app.route("/shutdown")
def shutdown():
    """Shuts down flask server."""
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with Werkzeug Server")
    func()
    return "Server Shutting down..."
