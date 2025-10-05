from flask import Blueprint

auth_bp = Blueprint(
    'auth', __name__,
    template_folder='../../templates/auth'
)

# import the routes so auth_bp is registered
from . import routes
