# hal_inventory/blueprints/main/routes.py

from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from . import main_bp

# Import your models. Adjust these imports/names to match your project.
from models import MaterialCategory, Item, Order, Kit, ConsumptionLog

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # --- 1. Compute counts ---
    try:
        items_count = Item.query.count()
    except Exception:
        items_count = 0
    try:
        orders_count = Order.query.count()
    except Exception:
        orders_count = 0
    try:
        kits_count = Kit.query.count()
    except Exception:
        kits_count = 0
    try:
        logs_count = ConsumptionLog.query.count()
    except Exception:
        logs_count = 0

    # --- 2. Recent orders for server-side table (e.g. last 10) ---
    try:
        recent_orders = (
            Order.query
            .order_by(Order.order_date.desc())  # adjust field name if different
            .limit(10)
            .all()
        )
    except Exception:
        recent_orders = []

    # --- 3. Prepare chart data ---
    # Example: Monthly consumption over last 6 months.
    # You need to replace this with your real logic:
    #   e.g. query ConsumptionLog grouped by month, actual vs expected, etc.
    # Here we provide a placeholder example:
    months = []          # e.g. ['Jan 2025', 'Feb 2025', ...]
    cons_actual = []     # [120, 100, ...]
    cons_expected = []   # [110, 90, ...]
    # If you have a function to compute monthly consumption:
    # months, cons_actual, cons_expected = compute_monthly_consumption()

    # Example stock vs reorder-level data:
    item_names = []
    stock_data = []
    rol_data = []
    # You can fill them by querying your Item model:
    # all_items = Item.query.all()
    # for it in all_items:
    #     item_names.append(it.name)
    #     stock_data.append(it.stock_qty)
    #     rol_data.append(it.reorder_level)
    # For now, placeholder empty lists.

    # --- 4. JSON endpoint branch ---
    # If frontend does `fetch(..., headers: {'Accept':'application/json'})`, return JSON:
    accept_mimetypes = request.accept_mimetypes
    if accept_mimetypes.accept_json and not accept_mimetypes.accept_html:
        return jsonify({
            'items_count': items_count,
            'orders_count': orders_count,
            'kits_count': kits_count,
            'logs_count': logs_count,
            'months': months,
            'cons_actual': cons_actual,
            'cons_expected': cons_expected,
            'item_names': item_names,
            'stock_data': stock_data,
            'rol_data': rol_data,
            # You can also include recent orders data if desired:
            # 'recent_orders': [
            #     {'order_id': o.order_id, 'order_date': o.order_date.isoformat(), ...}
            #     for o in recent_orders
            # ]
        })

    # --- 5. Otherwise render the template, passing variables ---
    return render_template(
        'main/dashboard.html',
        user=current_user,
        items_count=items_count,
        orders_count=orders_count,
        kits_count=kits_count,
        logs_count=logs_count,
        recent_orders=recent_orders,
        months=months,
        cons_actual=cons_actual,
        cons_expected=cons_expected,
        item_names=item_names,
        stock_data=stock_data,
        rol_data=rol_data
    )


@main_bp.route('/category')
@login_required
def category():
    categories = MaterialCategory.query.order_by(MaterialCategory.name).all()
    return render_template('main/category.html', categories=categories)


@main_bp.route('/raw-materials')
@login_required
def raw_materials():
    cat = MaterialCategory.query.filter_by(name='Raw Materials').first()
    items = Item.query.filter_by(category_id=cat.category_id).all() if cat else []
    return render_template('main/raw_materials.html', items=items)


@main_bp.route('/spare-parts')
@login_required
def spare_parts():
    cat = MaterialCategory.query.filter_by(name='Spare Parts').first()
    items = Item.query.filter_by(category_id=cat.category_id).all() if cat else []
    return render_template('main/spare_parts.html', items=items)


@main_bp.route('/commercial-items')
@login_required
def commercial_items():
    cat = MaterialCategory.query.filter_by(name='Commercial Items').first()
    items = Item.query.filter_by(category_id=cat.category_id).all() if cat else []
    return render_template('main/commercial_items.html', items=items)


@main_bp.route('/monthly-consumption')
@login_required
def monthly_consumption():
    return render_template('main/monthly_consumption.html')


@main_bp.route('/rol-stock')
@login_required
def rol_stock():
    return render_template('main/rol_stock.html')
