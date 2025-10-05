# hal_inventory/blueprints/admin/routes.py

from flask import render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import (
    User,
    MaterialCategory,
    InventoryType,
    UOM,
    Supplier,
    Item,
    Order,
    Kit,
    ConsumptionLog
)
from . import admin_bp
from datetime import datetime

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # 1. Summary counts
    total_users       = User.query.count()
    cat_count         = MaterialCategory.query.count()
    type_count        = InventoryType.query.count()
    uom_count         = UOM.query.count()
    sup_count         = Supplier.query.count()
    item_count        = Item.query.count()
    order_count       = Order.query.count()
    kit_count         = Kit.query.count()
    consumption_count = ConsumptionLog.query.count()

    # 2. Role distribution for chart
    from sqlalchemy import func
    counts_by_role = dict(
        db.session.query(User.role, func.count(User.user_id))
                  .group_by(User.role)
                  .all()
    )

    # 3. Recent users (most recent 5)
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    # 4. Low-stock data
    try:
        # Items whose quantity is <= low_stock_threshold
        low_q = Item.quantity  # adjust if attribute name differs
        thresh = Item.low_stock_threshold
        low_stock_qs = Item.query.filter(low_q <= thresh)
        low_stock_count = low_stock_qs.count()
        # get top 5 lowest by quantity
        low_stock_items = low_stock_qs.order_by(Item.quantity.asc()).limit(5).all()
    except Exception:
        low_stock_count = 0
        low_stock_items = []

    # 5. Recent Activity (as before—ensure you merged the previous recent_activity code)
    recent_activity = []
    now = datetime.utcnow()
    def compute_time_ago(timestamp):
        if not timestamp:
            return ""
        delta = now - timestamp
        if delta.days >= 1:
            return f"{delta.days}d ago"
        hrs = delta.seconds // 3600
        if hrs >= 1:
            return f"{hrs}h ago"
        mins = delta.seconds // 60
        return f"{mins}m ago" if mins > 0 else "just now"

    # Example: New Inventory Added
    try:
        items = Item.query.order_by(Item.created_at.desc()).limit(5).all()
    except Exception:
        items = []
    for item in items:
        ts = getattr(item, 'created_at', None)
        desc = f"New Inventory Added: {getattr(item, 'part_no', '') or getattr(item, 'name', '') or 'ID '+str(getattr(item,'id', ''))}"
        if 'items.view_item' in current_app.view_functions:
            link = url_for('items.view_item', item_id=getattr(item, 'id', None))
        else:
            link = '#'
        recent_activity.append({
            'icon_class': 'fas fa-box-open',
            'description': desc,
            'time_ago': compute_time_ago(ts),
            'link': link,
            'timestamp': ts or now
        })
    # Orders Shipped
    try:
        shipped_orders = Order.query.filter(Order.status == 'shipped').order_by(Order.shipped_at.desc()).limit(5).all()
    except Exception:
        shipped_orders = []
    for ord in shipped_orders:
        ts = getattr(ord, 'shipped_at', None)
        identifier = getattr(ord, 'order_no', getattr(ord, 'id', None))
        desc = f"Order Shipped: #{identifier}"
        if 'orders.view_order' in current_app.view_functions:
            link = url_for('orders.view_order', order_id=getattr(ord, 'id', None))
        else:
            link = '#'
        recent_activity.append({
            'icon_class': 'fas fa-truck',
            'description': desc,
            'time_ago': compute_time_ago(ts),
            'link': link,
            'timestamp': ts or now
        })
    # Low Stock Alerts
    for item in low_stock_items:
        ts = getattr(item, 'updated_at', None) or getattr(item, 'created_at', None)
        part = getattr(item, 'part_no', '') or getattr(item, 'name', '') or 'ID '+str(getattr(item,'id',''))
        desc = f"Low Stock: {part} ({item.quantity})"
        if 'items.view_item' in current_app.view_functions:
            link = url_for('items.view_item', item_id=getattr(item, 'id', None))
        else:
            link = '#'
        recent_activity.append({
            'icon_class': 'fas fa-exclamation-triangle',
            'description': desc,
            'time_ago': compute_time_ago(ts),
            'link': link,
            'timestamp': ts or now
        })
    # New Users
    for u in recent_users:
        ts = getattr(u, 'created_at', None)
        desc = f"New User: {u.first_name} {u.last_name}"
        if 'admin.list_users' in current_app.view_functions:
            link = url_for('admin.list_users')
        else:
            link = '#'
        recent_activity.append({
            'icon_class': 'fas fa-user-plus',
            'description': desc,
            'time_ago': compute_time_ago(ts),
            'link': link,
            'timestamp': ts or now
        })
    # Sort & limit
    recent_activity.sort(key=lambda ev: ev.get('timestamp', now), reverse=True)
    recent_activity = recent_activity[:8]

    # 6. Notifications placeholder
    notifications = []  # or actual notifications

    # 7. Render
    return render_template(
        'admin/dashboard.html',
        active_page='dashboard',
        total_users=total_users,
        cat_count=cat_count,
        type_count=type_count,
        uom_count=uom_count,
        sup_count=sup_count,
        item_count=item_count,
        order_count=order_count,
        kit_count=kit_count,
        consumption_count=consumption_count,
        counts_by_role=counts_by_role,
        recent_users=recent_users,
        recent_activity=recent_activity,
        low_stock_count=low_stock_count,
        low_stock_items=low_stock_items,
        notifications=notifications,
        current_year=datetime.utcnow().year
    )


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template(
        'admin/user_list.html',
        active_page='users',
        users=users
    )

@admin_bp.route('/users/toggle/<int:user_id>')
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_id == current_user.user_id:
        flash("You cannot deactivate your own account.", 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f"{user.email} {'activated' if user.is_active else 'deactivated'}.", 'success')
    return redirect(url_for('admin.list_users'))
