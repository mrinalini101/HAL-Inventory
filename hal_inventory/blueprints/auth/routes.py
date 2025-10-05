# blueprints/auth/routes.py

from flask import (
    render_template, request, redirect, url_for, flash, current_app
)
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app import db
from models import User
from utils.mailer import send_verification_email
from . import auth_bp

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            emp_id        = request.form['emp_id'],
            first_name    = request.form['first_name'],
            middle_name   = request.form.get('middle_name'),
            last_name     = request.form['last_name'],
            email         = email,
            password_hash = generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()

        serializer = get_serializer()
        token = user.generate_verification(serializer)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        html = render_template('emails/verify.html', user=user, verify_url=verify_url)
        send_verification_email(email, "Verify your HAL Koraput IMS account", html)

        flash('Registration successful! Check your email to verify.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/verify-email')
def verify_email():
    token = request.args.get('token')
    user = User.query.filter_by(verify_token=token).first()
    serializer = get_serializer()
    if not user or not user.verify_token_is_valid(serializer, token):
        flash('Invalid or expired link.', 'danger')
        return redirect(url_for('auth.register'))

    user.email_verified  = True
    user.verify_token    = None
    user.token_generated = None
    user.token_expires   = None
    db.session.commit()

    flash('Email verified! You may now log in.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            if not user.email_verified:
                flash('Please verify your email first.', 'warning')
                return redirect(url_for('auth.login'))

            # Log them in
            login_user(user)

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.dashboard'))

        flash('Invalid credentials.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/test-email')
def test_email():
    send_verification_email(
        to_email=current_app.config['MAIL_USERNAME'],
        subject='SMTP Test from HAL IMS',
        html_content='<p>If you see this, SMTP is working!</p>'
    )
    return 'Test email sent—check your Gmail inbox.'
