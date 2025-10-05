# hal_inventory/blueprints/api/categories.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required
from models      import MaterialCategory
from extensions  import db

category_fields = {
    'category_id': fields.Integer,
    'name':        fields.String,
    'description': fields.String,
}

class CategoryList(Resource):
    @jwt_required()
    @marshal_with(category_fields)
    def get(self):
        return MaterialCategory.query.all()

    @jwt_required()
    @marshal_with(category_fields)
    def post(self):
        data = request.get_json() or {}
        cat = MaterialCategory(
            name        = data['name'],
            description = data.get('description')
        )
        db.session.add(cat)
        db.session.commit()
        return cat, 201

class CategoryResource(Resource):
    @jwt_required()
    @marshal_with(category_fields)
    def get(self, category_id):
        return MaterialCategory.query.get_or_404(category_id)

    @jwt_required()
    @marshal_with(category_fields)
    def put(self, category_id):
        cat = MaterialCategory.query.get_or_404(category_id)
        data = request.get_json() or {}
        if 'name' in data:        cat.name        = data['name']
        if 'description' in data: cat.description = data['description']
        db.session.commit()
        return cat, 200

    @jwt_required()
    def delete(self, category_id):
        cat = MaterialCategory.query.get_or_404(category_id)
        db.session.delete(cat)
        db.session.commit()
        return {'msg':'Deleted'}, 204
