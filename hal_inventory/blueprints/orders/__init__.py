from flask import Blueprint

orders_bp = Blueprint(
    'orders',
    __name__,
    template_folder='templates/orders',
    url_prefix='/orders'
)

from . import routes  # noqa: F401
