# hal_inventory/blueprints/api/__init__.py

from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api    = Api(api_bp)

# Import all resources so they register
from .auth         import LoginResource
from .categories   import CategoryList, CategoryResource
from .uom          import UOMList, UOMResource
from .types        import TypeList, TypeResource
from .suppliers    import SupplierList, SupplierResource
from .items        import ItemListResource, ItemResource
from .consumption  import ConsumptionList, ConsumptionResource
from .orders       import OrderList, OrderResource
from .kits         import KitList, KitResource

# Register routes under /api/v1
api.add_resource(LoginResource,        '/auth/login')
api.add_resource(CategoryList,         '/categories')
api.add_resource(CategoryResource,     '/categories/<int:category_id>')
api.add_resource(UOMList,              '/uom')
api.add_resource(UOMResource,          '/uom/<int:uom_id>')
api.add_resource(TypeList,             '/types')
api.add_resource(TypeResource,         '/types/<int:inv_type_id>')
api.add_resource(SupplierList,         '/suppliers')
api.add_resource(SupplierResource,     '/suppliers/<int:supplier_id>')
api.add_resource(ItemListResource,     '/items')
api.add_resource(ItemResource,         '/items/<int:item_id>')
api.add_resource(ConsumptionList,      '/consumption')
api.add_resource(ConsumptionResource,  '/consumption/<int:log_id>')
api.add_resource(OrderList,            '/orders')
api.add_resource(OrderResource,        '/orders/<int:order_id>')
api.add_resource(KitList,              '/kits')
api.add_resource(KitResource,          '/kits/<string:kit_no>')
