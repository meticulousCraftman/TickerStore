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
    return redirect(url)


@app.route("/callback", methods=["GET"])
def callback():
    code = request.args['code']
    s.set_code(code)
    access_token = s.retrieve_access_token()
    return f'Access Token: {access_token}<br><b>Now drop back to the shell!</b>'


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.secret_key = os.urandom(24)
    app.run(debug=True)
