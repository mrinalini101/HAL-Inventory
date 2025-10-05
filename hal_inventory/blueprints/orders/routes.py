# hal_inventory/blueprints/orders/routes.py

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy.orm import joinedload
from extensions import db
from models import Order, OrderLine, Item, Supplier
from . import orders_bp

@orders_bp.route('/', methods=['GET'])
@login_required
def list_orders():
    """
    List all orders, newest first, eager‐loading supplier & lines so templates can do:
       o.supplier.name, o.total_value, o.currency, etc.
    """
    # 1) Load orders + their supplier + their lines in one go
    orders = (
        Order.query
             .options(
                 joinedload(Order.supplier),
                 joinedload(Order.lines)
             )
             .order_by(Order.order_date.desc())
             .all()
    )

    # 2) Bulk-load all items so we can look up unit_price by item_id
    items = Item.query.with_entities(Item.item_id, Item.unit_price).all()
    # build a simple map: { item_id: unit_price }
    price_map = { itm.item_id: itm.unit_price for itm in items }

    # 3) Compute total_value on each order
    for o in orders:
        total = 0
        for ln in o.lines:
            unit_price = price_map.get(ln.item_id, 0)
            total += ln.quantity * unit_price
        # attach attribute so template can do o.total_value
        setattr(o, 'total_value', total)

    return render_template('orders/list.html', orders=orders)


@orders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_order():
    """
    Create a new order header.
    GET:  show form (date picker + item + supplier + currency)
    POST: create header + first line item, then redirect back to list.
    """
    items     = Item.query.order_by(Item.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    today     = date.today().isoformat()
    default_currency = 'INR'

    if request.method == 'POST':
        order_date  = request.form.get('order_date') or date.today()
        supplier_id = int(request.form['supplier_id'])
        currency    = request.form.get('currency', default_currency).strip().upper()
        item_id     = int(request.form['item_id'])
        qty         = float(request.form['quantity'])

        new_order = Order(
            order_date   = order_date,
            requested_by = current_user.user_id,
            supplier_id  = supplier_id,
            currency     = currency
        )
        db.session.add(new_order)
        db.session.flush()  # populate new_order.order_id

        line = OrderLine(
            order_id = new_order.order_id,
            item_id  = item_id,
            quantity = qty
        )
        db.session.add(line)
        db.session.commit()

        flash('Order created and first line item added.', 'success')
        return redirect(url_for('orders.list_orders'))

    return render_template(
        'orders/form.html',
        today            = today,
        items            = items,
        suppliers        = suppliers,
        default_currency = default_currency
    )


@orders_bp.route('/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    """
    View an existing order (header + lines) and add more lines.
    Also computes and passes `total_value` into the template.
    """
    order = Order.query.get_or_404(order_id)

    items     = Item.query.order_by(Item.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    item_map  = {it.item_id: it for it in items}

    if request.method == 'POST':
        item_id = int(request.form['item_id'])
        qty     = float(request.form['quantity'])
        line = OrderLine(order_id=order_id, item_id=item_id, quantity=qty)
        db.session.add(line)
        db.session.commit()
        flash('Line item added.', 'success')
        return redirect(url_for('orders.edit_order', order_id=order_id))

    # compute total value for display
    total_value = sum(
        ln.quantity * item_map[ln.item_id].unit_price
        for ln in order.lines
    )

    return render_template(
        'orders/view.html',
        order       = order,
        items       = items,
        suppliers   = suppliers,
        item_map    = item_map,
        total_value = total_value
    )


@orders_bp.route('/approve/<int:order_id>', methods=['POST'])
@login_required
def approve_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role not in ('admin', 'manager') or order.status_code != 'OPEN':
        flash('You are not allowed to approve this order.', 'danger')
    else:
        order.status_code = 'APPROVED'
        order.approved_by = current_user.user_id
        db.session.commit()
        flash('Order approved.', 'success')
    return redirect(url_for('orders.list_orders'))


@orders_bp.route('/reject/<int:order_id>', methods=['POST'])
@login_required
def reject_order(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role not in ('admin', 'manager') or order.status_code != 'OPEN':
        flash('You are not allowed to reject this order.', 'danger')
    else:
        order.status_code = 'REJECTED'
        order.approved_by = current_user.user_id
        db.session.commit()
        flash('Order rejected.', 'warning')
    return redirect(url_for('orders.list_orders'))


@orders_bp.route('/close/<int:order_id>', methods=['POST'])
@login_required
def close_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status_code != 'APPROVED':
        flash('Only approved orders can be closed.', 'danger')
    else:
        order.status_code = 'CLOSED'
        db.session.commit()
        flash('Order closed.', 'info')
    return redirect(url_for('orders.list_orders'))
