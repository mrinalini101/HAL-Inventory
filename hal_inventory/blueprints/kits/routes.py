# hal_inventory/blueprints/kits/routes.py

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Kit, KitContent, Item
from . import kits_bp

def manager_or_admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_user.role not in ('admin', 'manager'):
            flash("You don't have permission to do that.", 'danger')
            return redirect(url_for('main.dashboard'))
        return fn(*args, **kwargs)
    return wrapper

@kits_bp.route('/add', methods=['GET', 'POST'])
@login_required
@manager_or_admin_required
def add_kit():
    items = Item.query.order_by(Item.name).all()
    if request.method == 'POST':
        kit_no   = request.form['kit_no'].strip()
        kit_name = request.form['kit_name'].strip()
        engine   = request.form['engine_no'].strip()

        if not kit_no or not kit_name or not engine:
            flash('Kit number, kit name and engine number are required.', 'danger')
        elif Kit.query.get(kit_no):
            flash('That Kit # already exists.', 'warning')
        else:
            kit = Kit(
                kit_no     = kit_no,
                kit_name   = kit_name,
                engine_no  = engine,
                created_by = current_user.user_id
            )
            db.session.add(kit)
            db.session.commit()
            flash('Kit created! You can now add contents.', 'success')
            return redirect(url_for('kits.view_kit', kit_no=kit.kit_no))

    return render_template(
        'kits/form.html',
        action='Add',
        kit=None,
        items=items
    )

# allow both /view/<kit_no> and /edit/<kit_no>
@kits_bp.route('/view/<kit_no>', methods=['GET', 'POST'])
@kits_bp.route('/edit/<kit_no>', methods=['GET', 'POST'])
@login_required
@manager_or_admin_required
def view_kit(kit_no):
    kit   = Kit.query.get_or_404(kit_no)
    items = Item.query.order_by(Item.name).all()

    # build the lookup map so template can do item_map[content.item_id].name
    item_map = {it.item_id: it for it in items}

    if request.method == 'POST':
        item_id      = request.form.get('item_id')
        if not item_id:
            flash('Please select an item to add.', 'danger')
        else:
            content = KitContent(
                kit_no        = kit.kit_no,
                item_id       = int(item_id),
                nomen_code_vc = request.form.get('nomen_code_vc','').strip(),
                qty_actual    = float(request.form.get('qty_actual') or 0),
                bin_balance   = float(request.form.get('bin_balance') or 0)
            )
            db.session.add(content)
            db.session.commit()
            flash('Kit content added.', 'success')
            return redirect(url_for('kits.view_kit', kit_no=kit_no))

    return render_template(
        'kits/view.html',
        kit      = kit,
        items    = items,
        item_map = item_map   # ← make sure this is passed!
    )

@kits_bp.route('/list', methods=['GET'])
@kits_bp.route('/', methods=['GET'])
@login_required
def list_kits():
    kits = Kit.query.order_by(Kit.kit_no).all()
    return render_template('kits/list.html', kits=kits)
