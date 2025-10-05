# hal_inventory/blueprints/api/kits.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from models      import Kit, KitContent, Item
from extensions  import db

kit_content_fields = {
    'id':            fields.Integer,
    'kit_no':        fields.String,
    'item_id':       fields.Integer,
    'nomen_code_vc': fields.String,
    'qty_actual':    fields.Float,
    'qty_issued':    fields.Float,
    'bin_balance':   fields.Float,
}

kit_fields = {
    'kit_no':   fields.String,
    'kit_name': fields.String,
    'engine_no':fields.String,
    'contents': fields.List(fields.Nested(kit_content_fields)),
}

class KitList(Resource):
    @jwt_required()
    @marshal_with(kit_fields)
    def get(self):
        return Kit.query.all()

    @jwt_required()
    @marshal_with(kit_fields)
    def post(self):
        data = request.get_json() or {}
        k = Kit(
            kit_no     = data['kit_no'],
            kit_name   = data['kit_name'],
            engine_no  = data['engine_no'],
            created_by = get_jwt_identity()
        )
        db.session.add(k)
        db.session.commit()
        return k, 201

class KitResource(Resource):
    @jwt_required()
    @marshal_with(kit_fields)
    def get(self, kit_no):
        return Kit.query.get_or_404(kit_no)

    @jwt_required()
    @marshal_with(kit_fields)
    def put(self, kit_no):
        k = Kit.query.get_or_404(kit_no)
        data = request.get_json() or {}
        if 'kit_name' in data:  k.kit_name  = data['kit_name']
        if 'engine_no' in data: k.engine_no = data['engine_no']
        # handle contents if provided…
        db.session.commit()
        return k, 200

    @jwt_required()
    def delete(self, kit_no):
        k = Kit.query.get_or_404(kit_no)
        db.session.delete(k)
        db.session.commit()
        return {'msg':'Deleted'}, 204
