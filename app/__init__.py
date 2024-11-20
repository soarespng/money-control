from flask import Flask
from .routes import app_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = '766b75ea743e79b0'
    app.register_blueprint(app_bp)
    return app
