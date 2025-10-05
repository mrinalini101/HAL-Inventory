from flask import Flask
from config import Config

# shared extensions
from extensions import db, login_manager, mail, jwt

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)  # for your REST API

    login_manager.login_view = 'auth.login'

    # ensure your @login_manager.user_loader (from models.py) is registered
    import models  # noqa: F401

    # --- UI blueprints ---
    from blueprints.auth            import auth_bp
    from blueprints.uom             import uom_bp
    from blueprints.orders          import orders_bp
    from blueprints.kits            import kits_bp
    from blueprints.analytics       import analytics_bp
    from blueprints.search          import search_bp
    from blueprints.inventory_types import types_bp
    from blueprints.suppliers       import suppliers_bp
    from blueprints.consumption     import consumption_bp

    # **categories** blueprint
    from blueprints.categories      import categories_bp

    # **admin** blueprint
    from blueprints.admin           import admin_bp

    from blueprints.main            import main_bp
    from blueprints.items           import items_bp

    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(uom_bp,        url_prefix='/uom')
    app.register_blueprint(orders_bp,     url_prefix='/orders')
    app.register_blueprint(kits_bp,       url_prefix='/kits')
    app.register_blueprint(analytics_bp,  url_prefix='/analytics')
    app.register_blueprint(search_bp,     url_prefix='/search')
    app.register_blueprint(types_bp,      url_prefix='/inventory_types')
    app.register_blueprint(suppliers_bp,  url_prefix='/suppliers')
    app.register_blueprint(consumption_bp,url_prefix='/consumption')

    # register categories once, under /categories
    app.register_blueprint(categories_bp, url_prefix='/categories')

    # register admin under /admin
    app.register_blueprint(admin_bp,      url_prefix='/admin')

    # public main & items
    app.register_blueprint(main_bp,       url_prefix='')
    app.register_blueprint(items_bp,      url_prefix='/items')

    # --- REST API blueprint ---
    from blueprints.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app

if __name__ == '__main__':
    create_app().run(debug=True)
