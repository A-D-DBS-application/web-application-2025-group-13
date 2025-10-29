[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DxqGQVx4)

from flask import Flask 

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)

class Config: 
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:[team132025!]@db.xrmsmxtxmguqwgopzhwi.supabase.co:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

-- Tabellen voor PostgreSQL

-- 1) users
CREATE TABLE users (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  age SMALLINT,
  role SMALLINT,
  date DATE
);

-- 2) travel_preferences
-- composite PK (user_id, interest_id) zoals in het diagram
CREATE TABLE travel_preferences (
  user_id BIGINT NOT NULL,
  interest_id DOUBLE PRECISION NOT NULL,
  budget TEXT,
  periode SMALLINT,
  persoonlijkheid TEXT,
  interests TEXT,
  PRIMARY KEY (user_id, interest_id),
  CONSTRAINT fk_travelpref_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3) travel_organize (organizer / travel organization)
CREATE TABLE travel_organize (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name TEXT NOT NULL,
  contact TEXT,
  type TEXT
);

-- 4) "groups" (in diagram: GROU / GROUP)
CREATE TABLE groups_tbl (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  match_id BIGINT,
  user_id BIGINT,              -- foreign key naar users (member / owner)
  role TEXT,
  status TEXT,
  CONSTRAINT fk_groups_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 5) trip
CREATE TABLE trip (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  travel_org_id BIGINT,        -- FK naar travel_organize
  destination TEXT,
  start_date DATE,
  end_date DATE,
  price DOUBLE PRECISION,
  CONSTRAINT fk_trip_travelorg FOREIGN KEY (travel_org_id) REFERENCES travel_organize(id) ON DELETE SET NULL
);

-- 6) feedback
CREATE TABLE feedback (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  trip_id BIGINT,
  user_id BIGINT,
  travel_org_id BIGINT,
  rating INTEGER,
  comment TEXT,
  feedback_date DATE,
  CONSTRAINT fk_feedback_trip FOREIGN KEY (trip_id) REFERENCES trip(id) ON DELETE CASCADE,
  CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_feedback_travelorg FOREIGN KEY (travel_org_id) REFERENCES travel_organize(id) ON DELETE SET NULL
);

-- 7) optionele koppeltabel: group_books_trip
-- in diagram lijkt "group books trip" (groep boekt trip). 
-- Dit is een many-to-many of 1-to-many afhankelijk van model; hier maak ik een expliciete relatie:
CREATE TABLE group_books_trip (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  group_id BIGINT NOT NULL,
  trip_id BIGINT NOT NULL,
  booked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  seats INTEGER,
  CONSTRAINT fk_gbt_group FOREIGN KEY (group_id) REFERENCES groups_tbl(id) ON DELETE CASCADE,
  CONSTRAINT fk_gbt_trip FOREIGN KEY (trip_id) REFERENCES trip(id) ON DELETE CASCADE,
  UNIQUE (group_id, trip_id)
);

-- Indexes (optioneel, voor lookup snelheid)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_trip_travelorg ON trip(travel_org_id);
CREATE INDEX idx_feedback_trip ON feedback(trip_id);
CREATE INDEX idx_groups_user ON groups_tbl(user_id);