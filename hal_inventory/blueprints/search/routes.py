from flask import request, render_template, url_for
from flask_login import login_required
from models import Item, Supplier, Kit, Order, MaterialCategory
from . import search_bp
from extensions import db

MODEL_MAP = {
    'items':  (Item, 'name'),
    'suppliers': (Supplier, 'name'),
    'kits':   (Kit, 'kit_name'),
    'orders': (Order, 'order_id'),
}

@login_required
@search_bp.route('/search', methods=['GET'])
def search():
    # Basic params
    q        = request.args.get('q', '').strip()
    module   = request.args.get('module', 'items')
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by  = request.args.get('sort_by')
    sort_dir = request.args.get('sort_dir', 'asc')

    Model, default_sort = MODEL_MAP.get(module, MODEL_MAP['items'])
    query = Model.query

    # Text search
    if q:
        if module == 'orders':
            # search by order_id or status
            if q.isdigit():
                query = query.filter(Model.order_id == int(q))
            else:
                query = query.filter(Model.status_code.ilike(f'%{q}%'))
        else:
            field = getattr(Model, default_sort)
            query = query.filter(field.ilike(f'%{q}%'))

    # Advanced filters
    if module == 'items':
        cat_id = request.args.get('category_id', type=int)
        sup_id = request.args.get('supplier_id', type=int)
        stock  = request.args.get('stock_status')  # low, ok
        if cat_id:
            query = query.filter(Model.category_id == cat_id)
        if sup_id:
            query = query.filter(Model.supplier_id == sup_id)
        if stock == 'low':
            query = query.filter(Model.stock_qty < Model.rol)
        elif stock == 'ok':
            query = query.filter(Model.stock_qty >= Model.rol)

    if module == 'orders':
        start = request.args.get('start_date')
        end   = request.args.get('end_date')
        status = request.args.get('status_code')
        if start:
            query = query.filter(Model.order_date >= start)
        if end:
            query = query.filter(Model.order_date <= end)
        if status:
            query = query.filter(Model.status_code == status)

    # Sorting
    if sort_by and hasattr(Model, sort_by):
        col = getattr(Model, sort_by)
        query = query.order_by(col.desc() if sort_dir=='desc' else col.asc())
    else:
        # default sort
        default = getattr(Model, default_sort)
        query = query.order_by(default.asc())

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items

    # For items filter form
    categories = MaterialCategory.query.order_by(MaterialCategory.name).all()
    suppliers  = Supplier.query.order_by(Supplier.name).all()
    order_statuses = [o.status_code for o in db.session.query(Order.status_code).distinct()]

    return render_template(
        'search.html',
        q=q,
        module=module,
        results=results,
        pagination=pagination,
        sort_by=sort_by,
        sort_dir=sort_dir,
        categories=categories,
        suppliers=suppliers,
        order_statuses=order_statuses
    )
