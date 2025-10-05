# hal_inventory/blueprints/categories/__init__.py

from flask import Blueprint
categories_bp = Blueprint('categories', __name__, url_prefix='/categories')
from . import routes  # noqa: F401
