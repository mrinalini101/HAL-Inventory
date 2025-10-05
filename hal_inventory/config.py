# hal_inventory/config.py

from datetime import timedelta

class Config:
    # -----------------------------------------------------------------------------
    # General
    # -----------------------------------------------------------------------------
    SECRET_KEY = 'd7f3c8a1b2e4f5c6d8a9b0c1e2f3a4b5c6d7e8f9a0b1c2d3'
    
    # -----------------------------------------------------------------------------
    # SQLAlchemy / MySQL
    # -----------------------------------------------------------------------------
    MYSQL_HOST     = 'localhost'
    MYSQL_USER     = 'root'
    MYSQL_PASSWORD = '2005'
    MYSQL_DB       = 'hal_inventory'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------------------------------------------------------
    # Flask-Mail (Gmail SMTP)
    # -----------------------------------------------------------------------------
    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USE_SSL        = False
    MAIL_USERNAME       = 'victim505050@gmail.com'       # your Gmail
    MAIL_PASSWORD       = 'cczy adpx rkrv joov'          # App Password
    MAIL_DEFAULT_SENDER = ('HAL Koraput IMS', MAIL_USERNAME)

    # -----------------------------------------------------------------------------
    # JWT (for REST API)
    # -----------------------------------------------------------------------------
    JWT_SECRET_KEY              = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES    = timedelta(hours=1)
