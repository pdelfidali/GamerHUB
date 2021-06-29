from flask import Blueprint

announce = Blueprint('announce', __name__)

from . import views