from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# 1. Maak de database instantie aan (buiten de functie!)
db = SQLAlchemy()

def create_app():
    # 2. Maak de app aan
    app = Flask(__name__)
    app.config.from_object(Config)

    # 3. Koppel de database aan de app
    db.init_app(app)

    # 4. Importeer routes HIER pas (om de cirkel te voorkomen)
    from app.routes import register_routes
    register_routes(app)

    return app