from flask import Flask, request, redirect
from dotenv import find_dotenv, load_dotenv
from upstox_api.api import *
import os

load_dotenv(find_dotenv())

app = Flask(__name__)
s = Session(os.getenv("UPSTOX_API_KEY"))
s.set_redirect_uri(os.getenv("UPSTOX_REDIRECT_URI"))
s.set_api_secret(os.getenv("UPSTOX_API_SECRET"))
url = s.get_login_url()


@app.route("/")
def demo():
    """Redirects user to login page"""
    return redirect(url)


@app.route("/callback", methods=["GET"])
def callback():
    """Receives the callback from server and gets the access token."""
    code = request.args["code"]
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
        os.getenv("TEMP_SERVER_SHUTDOWN_URL"),
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
