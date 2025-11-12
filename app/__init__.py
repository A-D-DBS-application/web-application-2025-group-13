from flask import Flask
from .config import Config
from .extensions import db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # Importeer models EERST zodat alle db.Model-klassen geregistreerd zijn
        from app import models, routes
        
        # Registreer routes nadat models geladen zijn
        routes.register_routes(app)
        
        # Alleen automatisch tabellen aanmaken voor lokale SQLite.
        # Voor externe databases (bv. Supabase) liever migrations gebruiken en niet op startup verbinden.
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '') or ''
        is_sqlite = db_uri.startswith('sqlite:')
        if is_sqlite:
            try:
                db.create_all()
                print("Info: SQLite tables created/verified.")
            except Exception as e:
                print(f"Warning: Could not create SQLite tables: {e}")
        else:
            print("Info: Skipping db.create_all for non-SQLite database (avoid remote connect at startup).")

    return app