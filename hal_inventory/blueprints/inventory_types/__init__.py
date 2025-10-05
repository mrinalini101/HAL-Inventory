from flask import Blueprint

types_bp = Blueprint(
    'inventory_types',
    __name__,
    template_folder='templates/inventory_types'
)

from . import routes   # make sure this import is here
