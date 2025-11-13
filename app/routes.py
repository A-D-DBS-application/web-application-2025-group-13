from flask import render_template, request, redirect, url_for, session, flash
from app import db
from app.models import User, Organiser, Trip
from datetime import datetime  

def register_routes(app):
    
    @app.route('/')
    def home():
        if session.get('role') == 'organizer':
            return redirect(url_for('organizer_dashboard'))
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/intake')
    def intake():
        if 'user_id' not in session or session.get('role') == 'organizer':
            return redirect(url_for('login'))
        return render_template('intake.html')

    # --- ORGANIZER DASHBOARD ---
    @app.route('/organizer/dashboard', methods=['GET', 'POST'])
    def organizer_dashboard():
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Geen toegang.', 'danger')
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            dest = request.form.get('destination')
            price = request.form.get('price')
            s_date = request.form.get('start_date')
            
            # Hier voegen we ook een datum toe voor de zekerheid (indien nodig)
            new_trip = Trip(
                travel_org_id=session['user_id'], 
                destination=dest, 
                price=price, 
                start_date=s_date
            )
            db.session.add(new_trip)
            db.session.commit()
            flash('Reis toegevoegd!', 'success')
        
        my_trips = Trip.query.filter_by(travel_org_id=session['user_id']).all()
        return render_template('organizer_dashboard.html', trips=my_trips)

    # --- REGISTRATIE ---
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            role_choice = request.form.get('role')
            
            # Checken of email al bestaat
            if User.query.filter_by(email=email).first() or Organiser.query.filter_by(email=email).first():
                flash('E-mailadres bestaat al. Probeer in te loggen.', 'danger')
                return redirect(url_for('login'))

            if role_choice == 'organizer':
                # --- HIER ZAT DE FOUT: We sturen nu created_at mee ---
                new_org = Organiser(
                    name=name, 
                    email=email, 
                    created_at=datetime.now() # <--- DIT LOST HET OP
                )
                db.session.add(new_org)
                db.session.commit()
                
                session['user_id'] = new_org.id
                session['name'] = new_org.name
                session['role'] = 'organizer'
                return redirect(url_for('organizer_dashboard'))
            
            else:
                # --- Ook voor de reiziger doen we dit voor de zekerheid ---
                new_user = User(
                    name=name, 
                    email=email, 
                    created_at=datetime.now() # <--- OOK HIER
                )
                db.session.add(new_user)
                db.session.commit()
                
                session['user_id'] = new_user.id
                session['name'] = new_user.name
                session['role'] = 'traveller'
                return redirect(url_for('home'))
        
        return render_template('register.html')

    # --- LOGIN ---
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')

            # Stap 1: Zoek in User (Reiziger)
            user = User.query.filter_by(email=email).first()
            if user:
                session['user_id'] = user.id
                session['name'] = user.name
                session['role'] = 'traveller'
                flash('Ingelogd als Reiziger!', 'success')
                return redirect(url_for('home'))

            # Stap 2: Zoek in Organiser
            org = Organiser.query.filter_by(email=email).first()
            if org:
                session['user_id'] = org.id
                session['name'] = org.name
                session['role'] = 'organizer'
                flash('Ingelogd als Organisator!', 'success')
                return redirect(url_for('organizer_dashboard'))

            flash('E-mailadres onbekend.', 'danger')
            return redirect(url_for('register'))
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Uitgelogd.', 'info')
        return redirect(url_for('login'))