
from flask import render_template, request, send_file, Response
from . import main


@main.route("/", methods = ["POST", "GET"])
def home():
    return render_template("index.html")