from app import db

TRAVEL_PERIODS = [
    {"name": "Winter (dec-feb)", "icon": "❄️"},
    {"name": "Lente (mrt-mei)", "icon": "🌸"},
    {"name": "Zomer (jun-aug)", "icon": "☀️"},
    {"name": "Herfst (sep-nov)", "icon": "🍂"},
    {"name": "Flexibel", "icon": "🔄"}
]

VIBE_QUESTIONS = [
    {"id": "adventure_level","text": "Hoe avontuurlijk ben je op reis?","min": "😌 Liever rustig","max": "🔥 Zoek avontuur"},
    {"id": "beach_person","text": "Het is een warme vakantiedag. Kies je een terras in de schaduw met een drankje, of lig je de hele dag op het strand?","min": "🚫 Geen zand","max": "🏖️ Bakken"},
    {"id": "culture_interest","text": "Je bent in een nieuwe stad en hebt enkele uren vrij. Waar trek je automatisch naartoe?","min": "🥱 Gewoon rondslenteren","max": "🏛️ Musea & cultuur"},
    {"id": "party_animal","text": "Je bent op reis en het is avond. Kies je eerder voor een rustige plek of beland je in een club en dans je tot sluitingstijd?","min": "🍵 Thee & Boek","max": "🎉 Tot het gaatje"},
    {"id": "nature_lover","text": "Bij het plannen van een trip: wat spreekt je instinctief het meest aan?","min": "🏙️ Stad & beton","max": "🌲 Bergen, bossen & natuur"},
    {"id": "luxury_comfort","text": "Na een lange dag op reis, wat maakt jou écht gelukkig?","min": "⛺ Simpel bed & klaar","max": "💎 Comfort & luxe"},
    {"id": "morning_person","text": "De wekker gaat op vakantie. Druk jij liever op snooze of ben je degene die voor de zon opstaat om alles uit de dag te halen?","min": "😴 Snooze","max": "🌅 Vroege vogel"},
    {"id": "planning_freak","text": "Hoe ziet jouw ideale reisplanning eruit?","min": "📋 Alles vastgelegd","max": "🍃 We zien wel waar we uitkomen"},
    {"id": "foodie_level","text": "Wat betekent eten voor jou tijdens het reizen?","min": "🥪 Gewoon nodig","max": "🍜 Hoogtepunt van de dag"},
    {"id": "sporty_spice","text": "Je wilt een perfecte zonsondergang spot bereiken. Wat doe je?","min": "🛗 Lift nemen","max": "🏃‍♂️ Berg op"},
    {"id": "chaos_tolerance","text": "Plannen veranderen plots op reis. Hoe reageer je?","min": "🤯 Stress","max": "🧘 Komt wel goed"},
    {"id": "city_trip","text": "Wat is jouw gevoel bij citytrips?","min": "🏙️ Mwah","max": "😍 Altijd goed"},
    {"id": "road_trip","text": "Je gaat op reis maar het is 20 uur rijden met de auto. Wat zou je eerder doen?","min": "✈️ Vliegen","max": "🚐 Roadtrip"},
    {"id": "backpacking","text": "Hoe reis jij het liefst?","min": "🧳 Alles netjes mee","max": "🎒 Zo licht mogelijk"},
    {"id": "local_contact","text": "Blijf je liever in je eigen bubbel, of zoek je actief contact met locals om hun cultuur echt te leren kennen?","min": "🫧 Bubbel","max": "🌍 Connecten"},
    {"id": "digital_detox","text": "Tijdens een tweedaagse hike heb je geen bereik. Zoek je actief naar signaal of ga je helemaal offline?","min": "📱 Internet nodig","max": "📵 Offline"}
]

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Organiser(db.Model):
    __tablename__ = 'Organiser' 
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)

class Trip(db.Model):
    __tablename__ = 'trip'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, nullable=True)
    travel_org_id = db.Column(db.Integer, db.ForeignKey('Organiser.id'), nullable=False)
    
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    activities = db.Column(db.Text, nullable=True)
    max_spots = db.Column(db.Integer, default=20)
    deposit_amount = db.Column(db.Float, default=0.0)
    organiser = db.relationship('Organiser', backref='trips')

class TravelerProfile(db.Model):
    __tablename__ = 'traveler_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=True)
    age = db.Column(db.Integer, nullable=False)
    budget_min = db.Column(db.Integer, nullable=False)
    budget_max = db.Column(db.Integer, nullable=False)
    travel_period = db.Column(db.String(200))

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
    social_battery = db.Column(db.Integer, nullable=False, default=3)
    leader_role = db.Column(db.Integer, nullable=False, default=3)
    talkative = db.Column(db.Integer, nullable=False, default=3)
    sustainability = db.Column(db.Integer, nullable=False, default=3)
    linked_buddy_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('profile', uselist=False))

class Group(db.Model):
    __tablename__ = 'group'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.String(50))
    confirmed = db.Column(db.Boolean)
    payment_status = db.Column(db.String(50), default='pending')
    user = db.relationship('User', backref='groups')


class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='notifications')