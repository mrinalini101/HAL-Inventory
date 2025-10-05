# hal_inventory/utils/mailer.py
from flask import current_app
from flask_mail import Message
from extensions import mail

def send_verification_email(to_email: str, subject: str, html_content: str):
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to_email],
        html=html_content
    )
    mail.send(msg)
    current_app.logger.info(f"Sent email to {to_email}")

def send_password_reset_email(to_email: str, subject: str, html_content: str):
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to_email],
        html=html_content
    )
    mail.send(msg)
    current_app.logger.info(f"Sent password reset email to {to_email}")
