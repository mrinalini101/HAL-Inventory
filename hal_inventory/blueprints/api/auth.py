# hal_inventory/blueprints/api/auth.py

from flask       import request
from flask_restful import Resource
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from models      import User
from extensions  import db

class LoginResource(Resource):
    def post(self):
        data = request.get_json() or {}
        email    = data.get('email','').strip().lower()
        password = data.get('password','')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return {'msg':'Bad credentials'}, 401
        if not user.email_verified:
            return {'msg':'Email not verified'}, 403

        token = create_access_token(identity=user.user_id)
        return {'access_token':token}, 200
