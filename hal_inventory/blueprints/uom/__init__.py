from flask import Blueprint

uom_bp = Blueprint(
    'uom',                # blueprint name for url_for()
    __name__,
    template_folder='templates/uom',
    url_prefix='/uom'     # mounts all routes at /uom
)

from . import routes    # noqa: F401
