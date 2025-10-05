from flask import render_template
from flask_login import login_required
from datetime import datetime, date
from sqlalchemy import func, extract
from extensions import db
from models import ConsumptionLog, Item, MaterialCategory, Supplier
from . import analytics_bp

@analytics_bp.route('/')
@login_required
def dashboard():
    # 1) Monthly consumption (last 12 months)
    today = date.today()
    year_ago = date(today.year - (1 if today.month <= 12 else 0), today.month, 1)
    cons_q = (
        db.session.query(
          extract('year', ConsumptionLog.log_date).label('yr'),
          extract('month', ConsumptionLog.log_date).label('mo'),
          func.sum(ConsumptionLog.actual_qty).label('actual'),
          func.sum(ConsumptionLog.expected_qty).label('expected')
        )
        .filter(ConsumptionLog.log_date >= year_ago)
        .group_by('yr','mo')
        .order_by('yr','mo')
        .all()
    )
    # Prepare labels and data
    mc_labels = []
    mc_actual = []
    mc_expected = []
    for yr,mo,act,exp in cons_q:
        mc_labels.append(f"{int(mo):02d}/{int(yr)}")
        mc_actual.append(float(act))
        mc_expected.append(float(exp or 0))

    # 2) Stock vs ROL for all active items
    items = Item.query.filter(Item.is_active==True).all()
    sr_labels = [it.name for it in items]
    sr_stock  = [float(it.stock_qty) for it in items]
    sr_rol    = [float(it.rol)       for it in items]

    # 3) Inventory valuation summary by category
    val_q = (
      db.session.query(
        MaterialCategory.name.label('cat'),
        func.sum(Item.stock_qty * Item.unit_price).label('value')
      )
      .join(MaterialCategory, Item.category_id==MaterialCategory.category_id)
      .group_by(MaterialCategory.name)
      .all()
    )
    val_labels = [row.cat for row in val_q]
    val_data   = [float(row.value) for row in val_q]

    return render_template(
      'analytics/dashboard.html',
      mc_labels=mc_labels,
      mc_actual=mc_actual,
      mc_expected=mc_expected,
      sr_labels=sr_labels,
      sr_stock=sr_stock,
      sr_rol=sr_rol,
      val_labels=val_labels,
      val_data=val_data
    )
