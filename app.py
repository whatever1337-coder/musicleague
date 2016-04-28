from flask import Flask
from flask import render_template

from feedback.urls import HELLO_URL
from feedback.urls import VIEW_SESSION_URL
from feedback.urls import VIEW_SUBMIT_URL


app = Flask(__name__)


@app.route(HELLO_URL)
def hello():
    return render_template("hello.html")


@app.route(VIEW_SESSION_URL, methods=['GET'])
def view_session(session_code):
    return render_template("view_session.html", session_code=session_code)


@app.route(VIEW_SUBMIT_URL, methods=['GET'])
def view_submit(session_code):
    return render_template("view_submit.html", session_code=session_code)


@app.route(VIEW_SUBMIT_URL, methods=['POST'])
def post_submit(session_code):
    return render_template("post_submit.html", session_code=session_code)


if __name__ == "__main__":
    app.run()
