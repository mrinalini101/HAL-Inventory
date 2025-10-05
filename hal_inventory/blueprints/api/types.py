# hal_inventory/blueprints/api/types.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required
from models      import InventoryType
from extensions  import db

type_fields = {
    'inv_type_id': fields.Integer,
    'type_name':   fields.String,
}

class TypeList(Resource):
    @jwt_required()
    @marshal_with(type_fields)
    def get(self):
        return InventoryType.query.all()

    @jwt_required()
    @marshal_with(type_fields)
    def post(self):
        data = request.get_json() or {}
        t = InventoryType(type_name=data['type_name'])
        db.session.add(t)
        db.session.commit()
        return t, 201

class TypeResource(Resource):
    @jwt_required()
    @marshal_with(type_fields)
    def get(self, inv_type_id):
        return InventoryType.query.get_or_404(inv_type_id)

    @jwt_required()
    @marshal_with(type_fields)
    def put(self, inv_type_id):
        t = InventoryType.query.get_or_404(inv_type_id)
        data = request.get_json() or {}
        if 'type_name' in data: t.type_name = data['type_name']
        db.session.commit()
        return t, 200

    @jwt_required()
    def delete(self, inv_type_id):
        t = InventoryType.query.get_or_404(inv_type_id)
        db.session.delete(t)
        db.session.commit()
        return {'msg':'Deleted'}, 204
