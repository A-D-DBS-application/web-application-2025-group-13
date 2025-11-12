import os

class Config: 
    SECRET_KEY = 'team132025!'
    # Bepaal database-URL:
    # - Voorkeur: env var DATABASE_URL (bijv. Supabase Postgres)
    # - Fallback: lokale SQLite voor ontwikkeling
    _db_url = os.environ.get('DATABASE_URL')
    # Corrigeer eventueel "postgres://" naar "postgresql://" voor SQLAlchemy 2.x
    if _db_url and _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
    


