from flask import render_template, request, redirect, url_for, session, flash
from app import db
from app.models import User, Organiser, Trip, TravelerProfile
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
        
        # Check of gebruiker al een profiel heeft
        existing_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        
        if existing_profile:
            # Toon overzicht van bestaand profiel
            user = User.query.get(session['user_id'])
            return render_template('intake_overview.html', user=user, profile=existing_profile)
        
        # Geen profiel -> toon intake formulier
        return render_template('intake.html')
    
    # --- INTAKE SUBMIT ---
    @app.route('/edit-intake')
    def edit_intake():
        """Show the intake form pre-filled with existing data for editing"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Toon altijd het intake formulier, zelfs als er al een profiel is
        # Het formulier zal worden ingevuld met bestaande data via de submit route
        return render_template('intake.html')


    @app.route('/submit-intake', methods=['POST'])
    def submit_intake():
        if 'user_id' not in session or session.get('role') == 'organizer':
            flash('Je moet ingelogd zijn als reiziger.', 'danger')
            return redirect(url_for('login'))
        
        try:
            # Data ophalen
            age = int(request.form.get('age'))
            budget_min = int(request.form.get('budget_min'))
            budget_max = int(request.form.get('budget_max'))
            
            # Periodes (checkboxes) samenvoegen tot een string
            periods = request.form.getlist('period')
            travel_period = ', '.join(periods)
            
            # Ratings ophalen
            adventure_level = int(request.form.get('adventure_level'))
            party_level = int(request.form.get('party_level'))
            culture_level = int(request.form.get('culture_level'))
            food_level = int(request.form.get('food_level'))
            nature_level = int(request.form.get('nature_level'))
            
            # Check of profiel al bestaat
            existing = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
            
            if existing:
                # Update bestaand profiel
                existing.age = age
                existing.budget_min = budget_min
                existing.budget_max = budget_max
                existing.travel_period = travel_period
                existing.adventure_level = adventure_level
                existing.party_level = party_level
                existing.culture_level = culture_level
                existing.food_level = food_level
                existing.nature_level = nature_level
                flash('Je profiel is bijgewerkt! 🎉', 'success')
            else:
                # Nieuw profiel aanmaken
                new_profile = TravelerProfile(
                    user_id=session['user_id'],
                    created_at=datetime.now(),
                    age=age,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    travel_period=travel_period,
                    adventure_level=adventure_level,
                    party_level=party_level,
                    culture_level=culture_level,
                    food_level=food_level,
                    nature_level=nature_level
                )
                db.session.add(new_profile)
                flash('Je profiel is opgeslagen! 🎉', 'success')
            
            db.session.commit()
            return redirect(url_for('match'))
            
        except Exception as e:
            db.session.rollback()
            print(f"\n!!! INTAKE FOUT !!!\n{e}\n")
            flash('Er ging iets mis bij het opslaan. Check de terminal.', 'danger')
            return redirect(url_for('intake'))
    
    # --- MATCHING ALGORITME ---
    @app.route('/match')
    def match():
        if 'user_id' not in session or session.get('role') == 'organizer':
            flash('Je moet ingelogd zijn als reiziger.', 'danger')
            return redirect(url_for('login'))
        
        # Check of gebruiker een profiel heeft
        my_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        if not my_profile:
            flash('Vul eerst je profiel in!', 'warning')
            return redirect(url_for('intake'))
        
        # Haal alle andere profielen op (niet van mezelf)
        all_profiles = TravelerProfile.query.filter(TravelerProfile.user_id != session['user_id']).all()
        
        # Bereken match score voor elk profiel
        matches = []
        for profile in all_profiles:
            score = calculate_match_score(my_profile, profile)
            
            # Haal user info op
            user = User.query.get(profile.user_id)
            
            matches.append({
                'user': user,
                'profile': profile,
                'score': score,
                'percentage': int(score)  # Score is al percentage
            })
        
        # Sorteer op score (hoogste eerst)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Alleen matches boven 50% tonen
        good_matches = [m for m in matches if m['score'] >= 50]
        
        return render_template('match.html', matches=good_matches, my_profile=my_profile)
    
    # --- ORGANIZER DASHBOARD ---
    @app.route('/organizer/dashboard', methods=['GET', 'POST'])
    def organizer_dashboard():
        # Check of je organisator bent
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            try:
                # Data ophalen
                dest = request.form.get('destination')
                price = request.form.get('price')
                s_date = request.form.get('start_date')
                e_date = request.form.get('end_date')
                
                # Trip aanmaken
                new_trip = Trip(
                    travel_org_id=session['user_id'],
                    destination=dest,
                    price=float(price), # Zorg dat het een getal is
                    start_date=s_date,
                    end_date=e_date,
                    match_id=None # Expliciet leeg laten
                )
                
                db.session.add(new_trip)
                db.session.commit()
                
                flash(f'Succes! De reis naar {dest} is opgeslagen.', 'success')
                return redirect(url_for('organizer_dashboard'))

            except Exception as e:
                db.session.rollback()
                # DIT ZIE JE IN JE TERMINAL ALS HET FOUT GAAT:
                print(f"\n!!! DATABASE FOUT !!!\n{e}\n") 
                flash('Er ging iets mis. Kijk in je terminal voor de exacte fout.', 'danger')
        
        # Reizen ophalen
        my_trips = Trip.query.filter_by(travel_org_id=session['user_id']).all()
        return render_template('organizer_dashboard.html', trips=my_trips)

    # --- REGISTRATIE ---
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            role_choice = request.form.get('role')
            
            # Check dubbel email
            if User.query.filter_by(email=email).first() or Organiser.query.filter_by(email=email).first():
                flash('E-mailadres bestaat al.', 'danger')
                return redirect(url_for('login'))

            if role_choice == 'organizer':
                new_org = Organiser(name=name, email=email, created_at=datetime.now())
                db.session.add(new_org)
                db.session.commit()
                
                session['user_id'] = new_org.id
                session['name'] = new_org.name
                session['role'] = 'organizer'
                return redirect(url_for('organizer_dashboard'))
            
            else:
                new_user = User(name=name, email=email, created_at=datetime.now())
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

            # Zoek Reiziger
            user = User.query.filter_by(email=email).first()
            if user:
                session['user_id'] = user.id
                session['name'] = user.name
                session['role'] = 'traveller'
                flash('Ingelogd als Reiziger!', 'success')
                return redirect(url_for('home'))

            # Zoek Organisator
            org = Organiser.query.filter_by(email=email).first()
            if org:
                session['user_id'] = org.id
                session['name'] = org.name
                session['role'] = 'organizer'
                flash('Ingelogd als Organisator!', 'success')
                return redirect(url_for('organizer_dashboard'))

            flash('Account onbekend.', 'danger')
            return redirect(url_for('register'))
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Uitgelogd.', 'info')
        return redirect(url_for('login'))

# Helper functie voor matching (buiten register_routes)
def calculate_match_score(profile1, profile2):
    """
    Simpel matching algoritme dat een percentage teruggeeft (0-100)
    Gebaseerd op gelijkenis in interesses, budget en reisperiode
    """
    total_score = 0
    max_score = 0
    
    # 1. Leeftijd (10 punten max) - moet binnen 5 jaar zitten
    age_diff = abs(profile1.age - profile2.age)
    if age_diff <= 3:
        total_score += 10
    elif age_diff <= 5:
        total_score += 7
    elif age_diff <= 8:
        total_score += 4
    max_score += 10
    
    # 2. Budget overlap (15 punten max)
    # Check of budgetten overlappen
    budget_overlap = not (profile1.budget_max < profile2.budget_min or profile2.budget_max < profile1.budget_min)
    if budget_overlap:
        # Bereken hoe groot de overlap is
        overlap_min = max(profile1.budget_min, profile2.budget_min)
        overlap_max = min(profile1.budget_max, profile2.budget_max)
        overlap_size = overlap_max - overlap_min
        
        # Grotere overlap = betere match
        avg_budget_range = ((profile1.budget_max - profile1.budget_min) + (profile2.budget_max - profile2.budget_min)) / 2
        overlap_ratio = min(overlap_size / avg_budget_range, 1.0)
        total_score += int(15 * overlap_ratio)
    max_score += 15
    
    # 3. Reisperiode overlap (15 punten max)
    periods1 = set(profile1.travel_period.split(', '))
    periods2 = set(profile2.travel_period.split(', '))
    
    # Als een van beiden "Flexibel" heeft, is dat altijd een match
    if 'Flexibel' in periods1 or 'Flexibel' in periods2:
        total_score += 15
    else:
        # Bereken overlap
        overlap = periods1.intersection(periods2)
        if len(overlap) > 0:
            # Meer overlappende periodes = betere score
            overlap_ratio = len(overlap) / max(len(periods1), len(periods2))
            total_score += int(15 * overlap_ratio)
    max_score += 15
    
    # 4. Avontuur niveau (10 punten max) - max verschil van 2
    adventure_diff = abs(profile1.adventure_level - profile2.adventure_level)
    if adventure_diff == 0:
        total_score += 10
    elif adventure_diff == 1:
        total_score += 7
    elif adventure_diff == 2:
        total_score += 4
    max_score += 10
    
    # 5. Party niveau (10 punten max)
    party_diff = abs(profile1.party_level - profile2.party_level)
    if party_diff == 0:
        total_score += 10
    elif party_diff == 1:
        total_score += 7
    elif party_diff == 2:
        total_score += 4
    max_score += 10
    
    # 6. Cultuur niveau (10 punten max)
    culture_diff = abs(profile1.culture_level - profile2.culture_level)
    if culture_diff == 0:
        total_score += 10
    elif culture_diff == 1:
        total_score += 7
    elif culture_diff == 2:
        total_score += 4
    max_score += 10
    
    # 7. Food niveau (10 punten max)
    food_diff = abs(profile1.food_level - profile2.food_level)
    if food_diff == 0:
        total_score += 10
    elif food_diff == 1:
        total_score += 7
    elif food_diff == 2:
        total_score += 4
    max_score += 10
    
    # 8. Natuur niveau (10 punten max)
    nature_diff = abs(profile1.nature_level - profile2.nature_level)
    if nature_diff == 0:
        total_score += 10
    elif nature_diff == 1:
        total_score += 7
    elif nature_diff == 2:
        total_score += 4
    max_score += 10
    
    # Bereken percentage
    percentage = int((total_score / max_score) * 100)
    return percentage
