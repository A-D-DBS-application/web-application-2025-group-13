from app import db

# Tabel 1: De Reiziger
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    #age = db.Column(db.Integer, nullable=True)
    
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
    
    # Nieuwe velden voor extra info
    description = db.Column(db.Text, nullable=True)
    activities = db.Column(db.Text, nullable=True)
    
    # Nieuwe velden voor betaling en plekken
    max_spots = db.Column(db.Integer, default=20)
    deposit_amount = db.Column(db.Float, default=0.0)

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
    
    # --- DE 16 VIBE CHECK VRAGEN (Schaal 1-5) ---
    
    # 1. Basis Vibe
    adventure_level = db.Column(db.Integer, nullable=False)  # 1=Rustig, 5=Avontuur
    beach_person = db.Column(db.Integer, nullable=False)     # 1=Geen zand, 5=Bakken
    culture_interest = db.Column(db.Integer, nullable=False) # 1=Slaapverwekkend, 5=Museumrat
    party_animal = db.Column(db.Integer, nullable=False)     # 1=Thee, 5=Feest
    nature_lover = db.Column(db.Integer, nullable=False)     # 1=Asfalt, 5=Wild
    
    # 2. Reisstijl
    luxury_comfort = db.Column(db.Integer, nullable=False)   # 1=Hostel, 5=Hotel
    morning_person = db.Column(db.Integer, nullable=False)   # 1=Snooze, 5=Vroeg
    planning_freak = db.Column(db.Integer, nullable=False)   # 1=Plannen, 5=Loslaten
    foodie_level = db.Column(db.Integer, nullable=False)     # 1=Brandstof, 5=Culinair
    sporty_spice = db.Column(db.Integer, nullable=False)     # 1=Lift, 5=Rennen
    chaos_tolerance = db.Column(db.Integer, nullable=False)  # 1=Stress, 5=Zen

    # 3. Interesses
    city_trip = db.Column(db.Integer, nullable=False)        # 1=Mwah, 5=Ja
    road_trip = db.Column(db.Integer, nullable=False)        # 1=Vliegen, 5=Roadtrip
    backpacking = db.Column(db.Integer, nullable=False)      # 1=Koffer, 5=Rugzak
    local_contact = db.Column(db.Integer, nullable=False)    # 1=Bubbel, 5=Locals
    digital_detox = db.Column(db.Integer, nullable=False)    # 1=Wifi, 5=Offline

    # 4. Ongebruikte velden (voor database compatibiliteit)
    social_battery = db.Column(db.Integer, nullable=False, default=3)
    leader_role = db.Column(db.Integer, nullable=False, default=3)
    talkative = db.Column(db.Integer, nullable=False, default=3)
    sustainability = db.Column(db.Integer, nullable=False, default=3)
    
    # NIEUW: Buddy Systeem
    linked_buddy_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relatie met User
    user = db.relationship('User', foreign_keys=[user_id], backref='profile', uselist=False)

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
    payment_status = db.Column(db.String(50), default='pending') # 'pending', 'paid'

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relatie
    user = db.relationship('User', backref='notifications')
