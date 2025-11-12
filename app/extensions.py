"""
Gedeelde extensies en services.
Importeer deze vanuit hier, niet vanuit app.* om circular imports te voorkomen.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
