# hal_inventory/blueprints/items/__init__.py

from flask import Blueprint

items_bp = Blueprint(
    'items',
    __name__,
    template_folder='templates/items'
)

from . import routes  # noqa: F401


