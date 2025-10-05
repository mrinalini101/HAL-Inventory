# hal_inventory/blueprints/api/uom.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required
from models      import UOM
from extensions  import db

uom_fields = {
    'uom_id':     fields.Integer,
    'code':       fields.String,
    'description':fields.String,
}

class UOMList(Resource):
    @jwt_required()
    @marshal_with(uom_fields)
    def get(self):
        return UOM.query.all()

    @jwt_required()
    @marshal_with(uom_fields)
    def post(self):
        data = request.get_json() or {}
        u = UOM(code=data['code'], description=data.get('description'))
        db.session.add(u)
        db.session.commit()
        return u, 201

class UOMResource(Resource):
    @jwt_required()
    @marshal_with(uom_fields)
    def get(self, uom_id):
        return UOM.query.get_or_404(uom_id)

    @jwt_required()
    @marshal_with(uom_fields)
    def put(self, uom_id):
        u = UOM.query.get_or_404(uom_id)
        data = request.get_json() or {}
        if 'code' in data:        u.code        = data['code']
        if 'description' in data: u.description = data['description']
        db.session.commit()
        return u, 200

    @jwt_required()
    def delete(self, uom_id):
        u = UOM.query.get_or_404(uom_id)
        db.session.delete(u)
        db.session.commit()
        return {'msg':'Deleted'}, 204
