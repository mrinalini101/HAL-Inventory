# hal_inventory/blueprints/consumption/routes.py

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import ConsumptionLog, Item, User
from blueprints.admin.routes import admin_required
from . import consumption_bp

# ─── LIST LOGS ────────────────────────────────────────────────────────────────
@consumption_bp.route('/', methods=['GET'])
@consumption_bp.route('/list', methods=['GET'])
@login_required
def list_logs():
    """
    Show all consumption logs, along with the item and the user who created it.
    """
    # Join ConsumptionLog → Item → User so we can display names
    entries = (
        db.session
          .query(ConsumptionLog, Item, User)
          .join(Item, ConsumptionLog.item_id == Item.item_id)
          .join(User, ConsumptionLog.created_by == User.user_id)
          .order_by(ConsumptionLog.log_date.desc())
          .all()
    )
    return render_template('consumption/list.html', entries=entries)


# ─── ADD LOG ─────────────────────────────────────────────────────────────────
@consumption_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_log():
    items = Item.query.order_by(Item.name).all()

    if request.method == 'POST':
        # gather + validate
        try:
            log_date     = request.form['log_date']                # required
            item_id      = int(request.form['item_id'])
            actual_qty   = float(request.form.get('actual_qty') or 0)
            expected_qty = float(request.form.get('expected_qty') or 0)
        except (KeyError, ValueError):
            flash('Please fill out all fields correctly.', 'danger')
            return render_template('consumption/form.html', items=items, action='Add')

        # insert
        log = ConsumptionLog(
            log_date     = log_date,
            item_id      = item_id,
            actual_qty   = actual_qty,
            expected_qty = expected_qty,
            created_by   = current_user.user_id
        )
        db.session.add(log)
        db.session.commit()
        flash('Consumption log added!', 'success')
        return redirect(url_for('consumption.list_logs'))

    # GET
    return render_template('consumption/form.html', items=items, action='Add')


# ─── EDIT LOG ────────────────────────────────────────────────────────────────
@consumption_bp.route('/edit/<int:log_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_log(log_id):
    log   = ConsumptionLog.query.get_or_404(log_id)
    items = Item.query.order_by(Item.name).all()

    if request.method == 'POST':
        # parse + validate updates
        try:
            log.log_date     = request.form.get('log_date') or log.log_date
            log.item_id      = int(request.form['item_id'])
            log.actual_qty   = float(request.form.get('actual_qty') or log.actual_qty)
            log.expected_qty = float(request.form.get('expected_qty') or log.expected_qty)
        except ValueError:
            flash('Invalid input.', 'danger')
            return render_template('consumption/form.html', items=items, log=log, action='Edit')

        db.session.commit()
        flash('Consumption log updated.', 'success')
        return redirect(url_for('consumption.list_logs'))

    # GET
    return render_template('consumption/form.html', items=items, log=log, action='Edit')


# ─── DELETE LOG ──────────────────────────────────────────────────────────────
@consumption_bp.route('/delete/<int:log_id>', methods=['POST'])
@login_required
@admin_required
def delete_log(log_id):
    log = ConsumptionLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    flash('Consumption log deleted.', 'info')
    return redirect(url_for('consumption.list_logs'))
