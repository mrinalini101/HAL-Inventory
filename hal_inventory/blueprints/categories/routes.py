from flask import (
    render_template, request, redirect, url_for, flash
)
from flask_login import login_required
from extensions import db
from models import MaterialCategory, Item
from blueprints.admin.routes import admin_required  # only admins
from . import categories_bp

@categories_bp.route('/', methods=['GET'])
@categories_bp.route('/list', methods=['GET'])
@login_required
@admin_required
def list_categories():
    """Show all categories (under /categories/ and /categories/list)."""
    cats = MaterialCategory.query.order_by(MaterialCategory.name).all()
    return render_template('categories/list.html', categories=cats)

@categories_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Create a new category."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()

        if not name:
            flash('Name is required.', 'danger')
        elif MaterialCategory.query.filter_by(name=name).first():
            flash('That category already exists.', 'warning')
        else:
            db.session.add(MaterialCategory(name=name, description=desc))
            db.session.commit()
            flash('Category added!', 'success')
            return redirect(url_for('categories.list_categories'))

    # GET or validation failure
    return render_template('categories/form.html',
                           action='Add',
                           category=None)

@categories_bp.route('/edit/<int:cat_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(cat_id):
    """Edit an existing category."""
    cat = MaterialCategory.query.get_or_404(cat_id)

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        new_desc = request.form.get('description', '').strip()

        if not new_name:
            flash('Name is required.', 'danger')
        else:
            cat.name = new_name
            cat.description = new_desc
            db.session.commit()
            flash('Category updated!', 'success')
            return redirect(url_for('categories.list_categories'))

    # GET
    return render_template('categories/form.html',
                           action='Edit',
                           category=cat)

@categories_bp.route('/delete/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    """Delete a category only if no items reference it."""
    cat = MaterialCategory.query.get_or_404(cat_id)

    if Item.query.filter_by(category_id=cat.category_id).first():
        flash('Cannot delete: items still assigned to this category.', 'danger')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash('Category deleted.', 'success')

    return redirect(url_for('categories.list_categories'))
