# hal_inventory/blueprints/suppliers/routes.py

from flask import (
    render_template, request, redirect, url_for, flash
)
from flask_login import login_required
from extensions import db
from models import Supplier
from . import suppliers_bp

@suppliers_bp.route('/list')
@login_required
def list_suppliers():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers/list.html', suppliers=suppliers)

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        # pull every field from the form
        name    = request.form['name'].strip()
        city    = request.form.get('city', '').strip() or None
        state   = request.form.get('state', '').strip() or None
        phone   = request.form.get('phone', '').strip() or None
        email   = request.form.get('email', '').strip() or None

        if not name:
            flash('Name is required.', 'danger')
            return redirect(url_for('suppliers.add_supplier'))

        sup = Supplier(
            name=name,
            city=city,
            state=state,
            phone=phone,
            email=email
        )
        db.session.add(sup)
        db.session.commit()
        flash('Supplier added successfully.', 'success')
        return redirect(url_for('suppliers.list_suppliers'))

    # GET
    return render_template('suppliers/form.html', supplier=None, action='Add')

@suppliers_bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    sup = Supplier.query.get_or_404(supplier_id)

    if request.method == 'POST':
        # update all the fields from the form
        sup.name  = request.form['name'].strip() or sup.name
        sup.city  = request.form.get('city','').strip() or sup.city
        sup.state = request.form.get('state','').strip() or sup.state
        sup.phone = request.form.get('phone','').strip() or sup.phone
        sup.email = request.form.get('email','').strip() or sup.email

        db.session.commit()
        flash('Supplier updated successfully.', 'success')
        return redirect(url_for('suppliers.list_suppliers'))

    # GET
    return render_template('suppliers/form.html', supplier=sup, action='Edit')

@suppliers_bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    sup = Supplier.query.get_or_404(supplier_id)
    db.session.delete(sup)
    db.session.commit()
    flash('Supplier deleted.', 'success')
    return redirect(url_for('suppliers.list_suppliers'))
