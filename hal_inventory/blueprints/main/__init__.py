from flask import Blueprint

# no custom template_folder—use the app's templates/ dir
main_bp = Blueprint('main', __name__)

from .routes import *  # noqa: F401
