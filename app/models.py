from app.extensions import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"

class TravelPreference(db.Model):
    __tablename__ = 'travel_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    interest_id = db.Column(db.Float)
    budget = db.Column(db.String(50))
    periode = db.Column(db.String(50))
    persoonlijkheid = db.Column(db.String(50))
    interesses = db.Column(db.String(100))

class Trip(db.Model):
    __tablename__ = 'trip'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50))
    travel_org_id = db.Column(db.String(50))
    destination = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    price = db.Column(db.Float)

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
