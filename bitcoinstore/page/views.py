import os

from flask import Blueprint
from flask import __version__
from flask import render_template


page = Blueprint("page", __name__, template_folder="templates")


@page.get("/")
def home():
    return render_template(
        "page/home.html",
        flask_ver=__version__,
        python_ver=os.environ["PYTHON_VERSION"],
        flask_env=os.environ["FLASK_ENV"],
    )
