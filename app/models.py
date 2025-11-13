from app import db

# Tabel 1: De Reiziger
class User(db.Model):
    __tablename__ = 'user'  # Komt overeen met jouw screenshot
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    # Password kolom staat in je DB, maar laten we even leeg als je geen ww wilt

# Tabel 2: De Organisator
class Organiser(db.Model):
    __tablename__ = 'Organiser' # Let op de Hoofdletter O, zoals in je screenshot
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)

# Tabel 3: De Reizen (Gekoppeld aan Organisator)
class Trip(db.Model):
    __tablename__ = 'trip'
    
    id = db.Column(db.Integer, primary_key=True)
    # In jouw screenshot heet de koppeling 'travel_org_id'
    travel_org_id = db.Column(db.Integer, db.ForeignKey('Organiser.id')) 
    
    destination = db.Column(db.String(100))
    start_date = db.Column(db.Date) # Of String als je dat makkelijker vindt
    end_date = db.Column(db.Date)
    price = db.Column(db.Float)
    
    # Optioneel: relatie zodat je makkelijk de organisator kan opvragen
    organiser = db.relationship('Organiser', backref='trips')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    travel_org_id = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    feedback_date = db.Column(db.Date)

class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.String(50))
    confirmed = db.Column(db.Boolean)
