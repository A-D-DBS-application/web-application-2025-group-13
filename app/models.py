from app import db

# --- TABEL 1: USER ---
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

# --- TABEL 2: ORGANISER ---
class Organiser(db.Model):
    __tablename__ = 'Organiser' 
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)

# --- TABEL 3: TRIP ---
class Trip(db.Model):
    __tablename__ = 'trip'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, nullable=True)
    
    # Foreign Key naar Organiser
    travel_org_id = db.Column(db.Integer, db.ForeignKey('Organiser.id'), nullable=False)
    
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    activities = db.Column(db.Text, nullable=True)
    max_spots = db.Column(db.Integer, default=20)
    deposit_amount = db.Column(db.Float, default=0.0)

    # RELATIE MET BACKREF (Zoals op de slide)
    # Hierdoor kun je doen:
    # 1. trip.organiser  -> Geeft de organisator van deze reis
    # 2. organiser.trips -> Geeft een LIJST van alle reizen van deze organisator
    organiser = db.relationship('Organiser', backref='trips')

# --- TABEL 4: TRAVELER PROFILE ---
class TravelerProfile(db.Model):
    __tablename__ = 'traveler_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=True)
    
    # Profiel Data
    age = db.Column(db.Integer, nullable=False)
    budget_min = db.Column(db.Integer, nullable=False)
    budget_max = db.Column(db.Integer, nullable=False)
    travel_period = db.Column(db.String(200))
    
    # Vibe Check Vragen (1-5)
    adventure_level = db.Column(db.Integer, nullable=False)
    beach_person = db.Column(db.Integer, nullable=False)
    culture_interest = db.Column(db.Integer, nullable=False)
    party_animal = db.Column(db.Integer, nullable=False)
    nature_lover = db.Column(db.Integer, nullable=False)
    luxury_comfort = db.Column(db.Integer, nullable=False)
    morning_person = db.Column(db.Integer, nullable=False)
    planning_freak = db.Column(db.Integer, nullable=False)
    foodie_level = db.Column(db.Integer, nullable=False)
    sporty_spice = db.Column(db.Integer, nullable=False)
    chaos_tolerance = db.Column(db.Integer, nullable=False)
    city_trip = db.Column(db.Integer, nullable=False)
    road_trip = db.Column(db.Integer, nullable=False)
    backpacking = db.Column(db.Integer, nullable=False)
    local_contact = db.Column(db.Integer, nullable=False)
    digital_detox = db.Column(db.Integer, nullable=False)
    
    # Defaults
    social_battery = db.Column(db.Integer, nullable=False, default=3)
    leader_role = db.Column(db.Integer, nullable=False, default=3)
    talkative = db.Column(db.Integer, nullable=False, default=3)
    sustainability = db.Column(db.Integer, nullable=False, default=3)
    
    linked_buddy_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # RELATIE MET BACKREF
    # uselist=False zorgt voor een 1-op-1 relatie.
    # 1. profile.user -> Geeft de User
    # 2. user.profile -> Geeft direct het profiel (geen lijst)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('profile', uselist=False))

# --- TABEL 5: GROUP (NIEUW MET BACKREF) ---
class Group(db.Model):
    __tablename__ = 'group'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.String(50))
    confirmed = db.Column(db.Boolean)
    payment_status = db.Column(db.String(50), default='pending')

    # RELATIE MET BACKREF (Deze ontbrak!)
    # Hierdoor kun je doen:
    # 1. group_entry.user -> Wie is dit groepslid?
    # 2. user.groups      -> In welke groepen zit deze user? (Geeft lijst terug)
    user = db.relationship('User', backref='groups')

# --- TABEL 6: NOTIFICATION ---
class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # RELATIE MET BACKREF
    # 1. notification.user -> Voor wie is dit?
    # 2. user.notifications -> Geef mij alle notificaties van deze user
    user = db.relationship('User', backref='notifications')