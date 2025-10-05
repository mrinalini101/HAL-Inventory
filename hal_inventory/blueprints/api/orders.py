# hal_inventory/blueprints/api/orders.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from models      import Order, OrderLine, Item
from extensions  import db
from datetime    import date

order_line_fields = {
    'line_id':  fields.Integer,
    'order_id': fields.Integer,
    'item_id':  fields.Integer,
    'quantity': fields.Float,
}

order_fields = {
    'order_id':     fields.Integer,
    'order_date':   fields.String,
    'status_code':  fields.String,
    'requested_by': fields.Integer,
    'approved_by':  fields.Integer,
    'lines':        fields.List(fields.Nested(order_line_fields)),
}

class OrderList(Resource):
    @jwt_required()
    @marshal_with(order_fields)
    def get(self):
        return Order.query.all()

    @jwt_required()
    @marshal_with(order_fields)
    def post(self):
        data = request.get_json() or {}
        o = Order(
            order_date   = date.fromisoformat(data.get('order_date', date.today().isoformat())),
            requested_by = get_jwt_identity()
        )
        db.session.add(o)
        db.session.commit()
        return o, 201

class OrderResource(Resource):
    @jwt_required()
    @marshal_with(order_fields)
    def get(self, order_id):
        return Order.query.get_or_404(order_id)

    @jwt_required()
    @marshal_with(order_fields)
    def put(self, order_id):
        o = Order.query.get_or_404(order_id)
        data = request.get_json() or {}
        if 'status_code' in data:
            o.status_code = data['status_code']
            if data['status_code'] in ('APPROVED','REJECTED'):
                o.approved_by = get_jwt_identity()
        db.session.commit()
        return o, 200

    @jwt_required()
    def delete(self, order_id):
        o = Order.query.get_or_404(order_id)
        db.session.delete(o)
        db.session.commit()
        return {'msg':'Deleted'}, 204
