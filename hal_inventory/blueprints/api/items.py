# hal_inventory/blueprints/api/items.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required
from models      import Item
from extensions  import db

item_fields = {
    'item_id':      fields.Integer,
    'mat_code':     fields.String,
    'name':         fields.String,
    'description':  fields.String,
    'category_id':  fields.Integer,
    'supplier_id':  fields.Integer,
    'inv_type_id':  fields.Integer,
    'uom_id':       fields.Integer,
    'unit_price':   fields.Float,
    'rol':          fields.Float,
    'inv_rate':     fields.Float,
    'stock_qty':    fields.Float,
    'is_active':    fields.Boolean,
}

class ItemListResource(Resource):
    @jwt_required()
    @marshal_with(item_fields)
    def get(self):
        return Item.query.all()

    @jwt_required()
    @marshal_with(item_fields)
    def post(self):
        data = request.get_json() or {}
        item = Item(
            mat_code   = data['mat_code'],
            name       = data['name'],
            description= data.get('description'),
            category_id= data['category_id'],
            supplier_id= data['supplier_id'],
            inv_type_id= data['inv_type_id'],
            uom_id     = data['uom_id'],
            unit_price = data.get('unit_price',0),
            rol        = data.get('rol',0),
            inv_rate   = data.get('inv_rate',0),
            stock_qty  = data.get('stock_qty',0),
        )
        db.session.add(item)
        db.session.commit()
        return item, 201

class ItemResource(Resource):
    @jwt_required()
    @marshal_with(item_fields)
    def get(self, item_id):
        return Item.query.get_or_404(item_id)

    @jwt_required()
    @marshal_with(item_fields)
    def put(self, item_id):
        item = Item.query.get_or_404(item_id)
        data = request.get_json() or {}
        for attr in item_fields:
            if attr in data:
                setattr(item, attr, data[attr])
        db.session.commit()
        return item, 200

    @jwt_required()
    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {'msg':'Deleted'}, 204
