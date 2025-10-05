from flask import Blueprint

# Name must be "admin" so url_for('admin.xxx') works
admin_bp = Blueprint('admin', __name__)

# Pull in routes so they're registered exactly once
from . import routes  # noqa: F401
