from flask import Blueprint

kits_bp = Blueprint(
    'kits',
    __name__,
    template_folder='templates/kits',
    url_prefix='/kits'
)

from . import routes  # noqa: F401
