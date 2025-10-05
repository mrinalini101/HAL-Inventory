# hal_inventory/blueprints/consumption/__init__.py

from flask import Blueprint

consumption_bp = Blueprint(
    'consumption',
    __name__,
    template_folder='templates/consumption'
)

from . import routes  # noqa: F401
