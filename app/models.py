from app import db

# Tabel 1: De Reiziger
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

# Tabel 2: De Organisator (Let op: Organiser met hoofdletter O)
class Organiser(db.Model):
    __tablename__ = 'Organiser' 
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)

# Tabel 3: De Reizen
class Trip(db.Model):
    __tablename__ = 'trip'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dit is de boosdoener. We vertellen Flask dat dit LEEG mag zijn.
    match_id = db.Column(db.Integer, nullable=True)
    
    # Koppeling naar Organiser
    travel_org_id = db.Column(db.Integer, db.ForeignKey('Organiser.id'), nullable=False)
    
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relatie
    organiser = db.relationship('Organiser', backref='trips')
# Tabel 4: Reiziger Profiel (Intake vragenlijst)
class TravelerProfile(db.Model):
    __tablename__ = 'traveler_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=True)
    
    # Basis info
    age = db.Column(db.Integer, nullable=False)
    budget_min = db.Column(db.Integer, nullable=False)  # in euros
    budget_max = db.Column(db.Integer, nullable=False)  # in euros
    
    # Reisperiodes (simpel: seizoenen of maanden)
    travel_period = db.Column(db.String(200))  # bijv. "Lente, Zomer"
    
    # Interesses op schaal 1-5
    adventure_level = db.Column(db.Integer, nullable=False)  # 1=rustig, 5=heel avontuurlijk
    party_level = db.Column(db.Integer, nullable=False)      # 1=rustig, 5=feestbeest
    culture_level = db.Column(db.Integer, nullable=False)    # 1=weinig, 5=veel cultuur
    food_level = db.Column(db.Integer, nullable=False)       # 1=normaal, 5=foodie
    nature_level = db.Column(db.Integer, nullable=False)     # 1=weinig, 5=veel natuur
    
    # Relatie met User
    user = db.relationship('User', backref='profile', uselist=False)

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
