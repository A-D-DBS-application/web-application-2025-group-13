from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            # Postgres uses TRUE/FALSE for boolean, not 1/0
            conn.execute(text("ALTER TABLE traveler_profile ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
            conn.commit()
            print("Added is_active to traveler_profile")
        except Exception as e:
            print(f"is_active might already exist: {e}")
