# hal_inventory/blueprints/api/consumption.py

from flask       import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from models      import ConsumptionLog, Item
from extensions  import db
from datetime    import datetime

cons_fields = {
    'log_id':      fields.Integer,
    'log_date':    fields.String,
    'item_id':     fields.Integer,
    'actual_qty':  fields.Float,
    'expected_qty':fields.Float,
    'created_by':  fields.Integer,
    'created_at':  fields.String,
}

class ConsumptionList(Resource):
    @jwt_required()
    @marshal_with(cons_fields)
    def get(self):
        return ConsumptionLog.query.all()

    @jwt_required()
    @marshal_with(cons_fields)
    def post(self):
        data = request.get_json() or {}
        log = ConsumptionLog(
            log_date    = datetime.fromisoformat(data['log_date']).date(),
            item_id     = data['item_id'],
            actual_qty  = data['actual_qty'],
            expected_qty= data.get('expected_qty'),
            created_by  = get_jwt_identity()
        )
        # adjust stock
        item = Item.query.get_or_404(log.item_id)
        item.stock_qty -= log.actual_qty

        db.session.add(log)
        db.session.commit()
        return log, 201

class ConsumptionResource(Resource):
    @jwt_required()
    @marshal_with(cons_fields)
    def get(self, log_id):
        return ConsumptionLog.query.get_or_404(log_id)

    @jwt_required()
    @marshal_with(cons_fields)
    def put(self, log_id):
        log = ConsumptionLog.query.get_or_404(log_id)
        data = request.get_json() or {}
        # you can implement updating logic here; for brevity, skip
        return log, 200

    @jwt_required()
    def delete(self, log_id):
        log = ConsumptionLog.query.get_or_404(log_id)
        db.session.delete(log)
        db.session.commit()
        return {'msg':'Deleted'}, 204
