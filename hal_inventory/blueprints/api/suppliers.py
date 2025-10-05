# hal_inventory/blueprints/api/suppliers.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required
from models      import Supplier
from extensions  import db

supplier_fields = {
    'supplier_id':   fields.Integer,
    'name':          fields.String,
    'address_line1': fields.String,
    'address_line2': fields.String,
    'city':          fields.String,
    'state':         fields.String,
    'zip_code':      fields.String,
    'phone':         fields.String,
    'email':         fields.String,
    'is_active':     fields.Boolean,
}

class SupplierList(Resource):
    @jwt_required()
    @marshal_with(supplier_fields)
    def get(self):
        return Supplier.query.all()

    @jwt_required()
    @marshal_with(supplier_fields)
    def post(self):
        data = request.get_json() or {}
        sup = Supplier(
            name          = data['name'],
            address_line1 = data.get('address_line1'),
            address_line2 = data.get('address_line2'),
            city          = data.get('city'),
            state         = data.get('state'),
            zip_code      = data.get('zip_code'),
            phone         = data.get('phone'),
            email         = data.get('email'),
        )
        db.session.add(sup)
        db.session.commit()
        return sup, 201

class SupplierResource(Resource):
    @jwt_required()
    @marshal_with(supplier_fields)
    def get(self, supplier_id):
        return Supplier.query.get_or_404(supplier_id)

    @jwt_required()
    @marshal_with(supplier_fields)
    def put(self, supplier_id):
        sup = Supplier.query.get_or_404(supplier_id)
        data = request.get_json() or {}
        for attr in supplier_fields:
            if attr in data:
                setattr(sup, attr, data[attr])
        db.session.commit()
        return sup, 200

    @jwt_required()
    def delete(self, supplier_id):
        sup = Supplier.query.get_or_404(supplier_id)
        db.session.delete(sup)
        db.session.commit()
        return {'msg':'Deleted'}, 204
