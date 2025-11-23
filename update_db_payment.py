from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        # 1. Add columns to 'trip' table
        try:
            conn.execute(text("ALTER TABLE trip ADD COLUMN max_spots INTEGER DEFAULT 20"))
            print("Added max_spots to trip")
        except Exception as e:
            print(f"max_spots might already exist: {e}")

        try:
            conn.execute(text("ALTER TABLE trip ADD COLUMN deposit_amount FLOAT DEFAULT 0.0"))
            print("Added deposit_amount to trip")
        except Exception as e:
            print(f"deposit_amount might already exist: {e}")

        # 2. Add column to 'group' table (using "group" with quotes because it's a reserved word)
        try:
            conn.execute(text('ALTER TABLE "group" ADD COLUMN payment_status VARCHAR(50) DEFAULT \'pending\''))
            print("Added payment_status to group")
        except Exception as e:
            print(f"payment_status might already exist: {e}")
            
        conn.commit()
        print("Database update complete!")
