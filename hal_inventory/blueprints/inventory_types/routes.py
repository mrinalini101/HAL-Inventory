from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import InventoryType
from blueprints.admin.routes import admin_required
from . import types_bp

# List all types
@types_bp.route('/list')
@login_required
@admin_required
def list_types():
    all_types = InventoryType.query.order_by(InventoryType.type_name).all()
    return render_template('types/list.html', types=all_types)

# Add a new type
@types_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_type():
    if request.method == 'POST':
        name = request.form['type_name'].strip()
        if not name:
            flash('Name is required.', 'danger')
        elif InventoryType.query.filter_by(type_name=name).first():
            flash('That type already exists.', 'warning')
        else:
            db.session.add(InventoryType(type_name=name))
            db.session.commit()
            flash('Type added!', 'success')
            return redirect(url_for('types.list_types'))
    return render_template('types/form.html', action='Add')

# Edit an existing type
@types_bp.route('/edit/<int:inv_type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_type(inv_type_id):
    t = InventoryType.query.get_or_404(inv_type_id)
    if request.method == 'POST':
        new_name = request.form['type_name'].strip()
        if new_name:
            t.type_name = new_name
            db.session.commit()
            flash('Type updated!', 'success')
            return redirect(url_for('types.list_types'))
    return render_template('types/form.html', action='Edit', inv_type=t)

# Delete a type
@types_bp.route('/delete/<int:inv_type_id>', methods=['POST'])
@login_required
@admin_required
def delete_type(inv_type_id):
    t = InventoryType.query.get_or_404(inv_type_id)
    db.session.delete(t)
    db.session.commit()
    flash('Type deleted.', 'success')
    return redirect(url_for('types.list_types'))
