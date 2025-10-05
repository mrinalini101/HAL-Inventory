# hal_inventory/models.py

from datetime import datetime, timedelta
from flask_login import UserMixin
from extensions import db, login_manager

# ─── Lookup Tables ────────────────────────────────────────────────────────────

class MaterialCategory(db.Model):
    __tablename__ = 'material_categories'
    category_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    items       = db.relationship('Item', backref='category', lazy=True)


class InventoryType(db.Model):
    __tablename__ = 'inventory_types'
    inv_type_id = db.Column(db.SmallInteger, primary_key=True)
    type_name   = db.Column(db.String(30), unique=True, nullable=False)

    items       = db.relationship('Item', backref='inv_type', lazy=True)


class UOM(db.Model):
    __tablename__ = 'uom'
    uom_id      = db.Column(db.SmallInteger, primary_key=True)
    code        = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.String(50))

    items       = db.relationship('Item', backref='uom', lazy=True)


class OrderStatus(db.Model):
    __tablename__ = 'order_status'
    status_code = db.Column(db.String(20), primary_key=True)
    description = db.Column(db.String(50), nullable=False)


# ─── Master Tables ────────────────────────────────────────────────────────────

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    supplier_id   = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), unique=True, nullable=False)
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city          = db.Column(db.String(50))
    state         = db.Column(db.String(50))
    zip_code      = db.Column(db.String(20))
    phone         = db.Column(db.String(20))
    email         = db.Column(db.String(100))
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    items = db.relationship('Item', backref='supplier', lazy=True)
    # (Order backref defined on Order)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id         = db.Column(db.Integer, primary_key=True)
    emp_id          = db.Column(db.String(50), unique=True, nullable=False)
    first_name      = db.Column(db.String(50), nullable=False)
    middle_name     = db.Column(db.String(50))
    last_name       = db.Column(db.String(50), nullable=False)
    email           = db.Column(db.String(100), unique=True, nullable=False)
    password_hash   = db.Column(db.String(255), nullable=False)
    role            = db.Column(db.Enum('admin','manager','staff'),
                                default='staff', nullable=False)
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime,
                                default=datetime.utcnow,
                                onupdate=datetime.utcnow)

    email_verified  = db.Column(db.Boolean, default=False)
    verify_token    = db.Column(db.String(255))
    token_generated = db.Column(db.DateTime)
    token_expires   = db.Column(db.DateTime)

    login_history   = db.relationship('LoginHistory', backref='user', lazy=True)

    def get_id(self) -> str:
        return str(self.user_id)

    def generate_verification(self, serializer, expires_sec=86400):
        token = serializer.dumps(self.email, salt='email-verify')
        now = datetime.utcnow()
        self.verify_token    = token
        self.token_generated = now
        self.token_expires   = now + timedelta(seconds=expires_sec)
        db.session.commit()
        return token

    def verify_token_is_valid(self, serializer, token, max_age=86400):
        try:
            email = serializer.loads(token, salt='email-verify', max_age=max_age)
        except Exception:
            return False
        return email == self.email and self.verify_token == token


# ─── Operational Tables ───────────────────────────────────────────────────────

class Item(db.Model):
    __tablename__ = 'items'
    item_id     = db.Column(db.BigInteger, primary_key=True)
    mat_code    = db.Column(db.String(50), unique=True, nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('material_categories.category_id'),
                            nullable=False)
    supplier_id = db.Column(db.Integer,
                            db.ForeignKey('suppliers.supplier_id'),
                            nullable=False)
    inv_type_id = db.Column(db.SmallInteger,
                            db.ForeignKey('inventory_types.inv_type_id'),
                            nullable=False)
    uom_id      = db.Column(db.SmallInteger,
                            db.ForeignKey('uom.uom_id'),
                            nullable=False)
    unit_price  = db.Column(db.Numeric(14,4), nullable=False, default=0.0)
    rol         = db.Column(db.Numeric(12,2), nullable=False, default=0.0)
    inv_rate    = db.Column(db.Numeric(12,4))
    stock_qty   = db.Column(db.Numeric(12,2), nullable=False, default=0.0)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,
                            default=datetime.utcnow,
                            onupdate=datetime.utcnow)


class ConsumptionLog(db.Model):
    __tablename__ = 'consumption_logs'
    log_id      = db.Column(db.BigInteger, primary_key=True)
    log_date    = db.Column(db.Date, nullable=False)
    item_id     = db.Column(db.BigInteger,
                            db.ForeignKey('items.item_id'),
                            nullable=False)
    actual_qty  = db.Column(db.Numeric(12,2), nullable=False)
    expected_qty= db.Column(db.Numeric(12,2))
    created_by  = db.Column(db.Integer,
                            db.ForeignKey('users.user_id'),
                            nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


class LoginHistory(db.Model):
    __tablename__ = 'login_history'
    log_id     = db.Column(db.BigInteger, primary_key=True)
    user_id    = db.Column(db.Integer,
                           db.ForeignKey('users.user_id'),
                           nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text)


class Order(db.Model):
    __tablename__ = 'orders'
    order_id     = db.Column(db.BigInteger, primary_key=True)
    order_date   = db.Column(db.Date, nullable=False)
    status_code  = db.Column(db.String(20),
                             db.ForeignKey('order_status.status_code'),
                             default='OPEN', nullable=False)
    requested_by = db.Column(db.Integer,
                             db.ForeignKey('users.user_id'),
                             nullable=False)
    approved_by  = db.Column(db.Integer,
                             db.ForeignKey('users.user_id'))
    supplier_id  = db.Column(db.Integer,
                             db.ForeignKey('suppliers.supplier_id'),
                             nullable=False)
    currency     = db.Column(db.String(10), nullable=False, default='INR')

    # renamed as requested: now called `value`
    value        = db.Column(db.Numeric(14,2), nullable=False, default=0.00)

    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime,
                             default=datetime.utcnow,
                             onupdate=datetime.utcnow)

    lines = db.relationship('OrderLine', backref='order', lazy=True)

    requested_by_user = db.relationship(
        'User',
        foreign_keys=[requested_by],
        backref=db.backref('orders_requested', lazy=True)
    )
    approved_by_user = db.relationship(
        'User',
        foreign_keys=[approved_by],
        backref=db.backref('orders_approved', lazy=True)
    )

    supplier = db.relationship(
        'Supplier',
        backref=db.backref('orders', lazy=True)
    )


class OrderLine(db.Model):
    __tablename__ = 'order_lines'
    line_id    = db.Column(db.BigInteger, primary_key=True)
    order_id   = db.Column(db.BigInteger,
                           db.ForeignKey('orders.order_id'),
                           nullable=False)
    item_id    = db.Column(db.BigInteger,
                           db.ForeignKey('items.item_id'),
                           nullable=False)
    quantity   = db.Column(db.Numeric(12,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # allows `line.item.name` in templates
    item = db.relationship('Item')


class Kit(db.Model):
    __tablename__ = 'kits'
    kit_no     = db.Column(db.String(50), primary_key=True)
    kit_name   = db.Column(db.String(100), nullable=False)
    engine_no  = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer,
                           db.ForeignKey('users.user_id'),
                           nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contents = db.relationship('KitContent', backref='kit', lazy=True)


class KitContent(db.Model):
    __tablename__ = 'kit_contents'
    id            = db.Column(db.BigInteger, primary_key=True)
    kit_no        = db.Column(db.String(50),
                              db.ForeignKey('kits.kit_no'),
                              nullable=False)
    item_id       = db.Column(db.BigInteger,
                              db.ForeignKey('items.item_id'),
                              nullable=False)
    nomen_code_vc = db.Column(db.String(50))
    qty_actual    = db.Column(db.Numeric(12,2), nullable=False)
    qty_issued    = db.Column(db.Numeric(12,2), default=0.0)
    bin_balance   = db.Column(db.Numeric(12,2), nullable=False)


# ──────────────────────────────────────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
