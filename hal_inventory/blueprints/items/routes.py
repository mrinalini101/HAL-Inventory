# hal_inventory/blueprints/items/routes.py

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models import Item, MaterialCategory, Supplier, InventoryType, UOM
from blueprints.admin.routes import admin_required
from . import items_bp

# -------------------------------------------------------------------
# LIST (any authenticated user)
# -------------------------------------------------------------------
@items_bp.route('/', methods=['GET'])
@items_bp.route('/list', methods=['GET'])
@login_required
def list_items():
    items = Item.query.order_by(Item.name).all()
    return render_template('items/list.html', items=items)


# -------------------------------------------------------------------
# ADD (admin only)
# -------------------------------------------------------------------
@items_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    cats     = MaterialCategory.query.order_by(MaterialCategory.name).all()
    sups     = Supplier.query.order_by(Supplier.name).all()
    inv_types = InventoryType.query.order_by(InventoryType.type_name).all()  # ← use type_name
    uoms     = UOM.query.order_by(UOM.code).all()

    if request.method == 'POST':
        mat_code    = request.form['mat_code'].strip()
        name        = request.form['name'].strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id')
        supplier_id = request.form.get('supplier_id')
        inv_type_id = request.form.get('inv_type_id')
        uom_id      = request.form.get('uom_id')
        unit_price  = request.form.get('unit_price') or 0
        rol         = request.form.get('rol') or 0
        stock_qty   = request.form.get('stock_qty') or 0

        if not mat_code or not name:
            flash('Mat Code and Name are required.', 'danger')
        else:
            itm = Item(
                mat_code    = mat_code,
                name        = name,
                description = description,
                category_id = category_id,
                supplier_id = supplier_id,
                inv_type_id = inv_type_id,
                uom_id      = uom_id,
                unit_price  = unit_price,
                rol         = rol,
                stock_qty   = stock_qty
            )
            db.session.add(itm)
            db.session.commit()
            flash('Item created!', 'success')
            return redirect(url_for('items.list_items'))

    return render_template('items/form.html',
                           action     ='Add',
                           item       = None,
                           categories = cats,
                           suppliers  = sups,
                           inv_types  = inv_types,
                           uoms       = uoms)


# -------------------------------------------------------------------
# EDIT (admin only)
# -------------------------------------------------------------------
@items_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(item_id):
    itm       = Item.query.get_or_404(item_id)
    cats      = MaterialCategory.query.order_by(MaterialCategory.name).all()
    sups      = Supplier.query.order_by(Supplier.name).all()
    inv_types = InventoryType.query.order_by(InventoryType.type_name).all()  # ← use type_name
    uoms      = UOM.query.order_by(UOM.code).all()

    if request.method == 'POST':
        itm.mat_code    = request.form['mat_code'].strip() or itm.mat_code
        itm.name        = request.form['name'].strip()     or itm.name
        itm.description = request.form.get('description','').strip()
        itm.category_id = request.form.get('category_id')
        itm.supplier_id = request.form.get('supplier_id')
        itm.inv_type_id = request.form.get('inv_type_id')
        itm.uom_id      = request.form.get('uom_id')
        itm.unit_price  = request.form.get('unit_price') or itm.unit_price
        itm.rol         = request.form.get('rol')         or itm.rol
        itm.stock_qty   = request.form.get('stock_qty')   or itm.stock_qty

        db.session.commit()
        flash('Item updated!', 'success')
        return redirect(url_for('items.list_items'))

    return render_template('items/form.html',
                           action     ='Edit',
                           item       = itm,
                           categories = cats,
                           suppliers  = sups,
                           inv_types  = inv_types,
                           uoms       = uoms)


# -------------------------------------------------------------------
# DELETE (admin only)
# -------------------------------------------------------------------
@items_bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    itm = Item.query.get_or_404(item_id)
    db.session.delete(itm)
    db.session.commit()
    flash('Item deleted.', 'success')
    return redirect(url_for('items.list_items'))
