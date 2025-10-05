from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import UOM
from blueprints.admin.routes import admin_required
from . import uom_bp

# LIST / VIEW (any logged-in user)
@uom_bp.route('/', methods=['GET'])
@uom_bp.route('/list', methods=['GET'])
@login_required
def list_uom():
    all_uoms = UOM.query.order_by(UOM.code).all()
    return render_template('uom/list.html', uoms=all_uoms)

# ADD (admin only)
@uom_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_uom():
    if request.method == 'POST':
        code = request.form['code'].strip()
        desc = request.form.get('description', '').strip()

        if not code:
            flash('Code is required.', 'danger')
        elif UOM.query.filter_by(code=code).first():
            flash('That unit already exists.', 'warning')
        else:
            unit = UOM(code=code, description=desc)
            db.session.add(unit)
            db.session.commit()
            flash('Unit of Measure added!', 'success')
            return redirect(url_for('uom.list_uom'))

    return render_template('uom/form.html', action='Add', uom=None)

# EDIT (admin only)
@uom_bp.route('/edit/<int:uom_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_uom(uom_id):
    unit = UOM.query.get_or_404(uom_id)

    if request.method == 'POST':
        unit.code = request.form['code'].strip() or unit.code
        unit.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Unit updated!', 'success')
        return redirect(url_for('uom.list_uom'))

    return render_template('uom/form.html', action='Edit', uom=unit)

# DELETE (admin only)
@uom_bp.route('/delete/<int:uom_id>', methods=['POST'])
@login_required
@admin_required
def delete_uom(uom_id):
    unit = UOM.query.get_or_404(uom_id)
    db.session.delete(unit)
    db.session.commit()
    flash('Unit deleted.', 'success')
    return redirect(url_for('uom.list_uom'))
