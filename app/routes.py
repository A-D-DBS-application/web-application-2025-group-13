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
            
            # --- 16 VIBE CHECK VRAGEN ---
            # 1. Basis Vibe
            adventure_level = int(request.form.get('adventure_level'))
            beach_person = int(request.form.get('beach_person'))
            culture_interest = int(request.form.get('culture_interest'))
            party_animal = int(request.form.get('party_animal'))
            nature_lover = int(request.form.get('nature_lover'))
            
            # 2. Reisstijl
            luxury_comfort = int(request.form.get('luxury_comfort'))
            morning_person = int(request.form.get('morning_person'))
            planning_freak = int(request.form.get('planning_freak'))
            foodie_level = int(request.form.get('foodie_level'))
            sporty_spice = int(request.form.get('sporty_spice'))
            chaos_tolerance = int(request.form.get('chaos_tolerance'))

            # 3. Interesses
            city_trip = int(request.form.get('city_trip'))
            road_trip = int(request.form.get('road_trip'))
            backpacking = int(request.form.get('backpacking'))
            local_contact = int(request.form.get('local_contact'))
            digital_detox = int(request.form.get('digital_detox'))

            # 4. Ongebruikte velden (defaults)
            social_battery = 3
            leader_role = 3
            talkative = 3
            sustainability = 3
            
            # Check of profiel al bestaat
            existing = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
            
            if existing:
                # Update bestaand profiel
                existing.age = age
                existing.budget_min = budget_min
                existing.budget_max = budget_max
                existing.travel_period = travel_period
                
                existing.adventure_level = adventure_level
                existing.beach_person = beach_person
                existing.culture_interest = culture_interest
                existing.party_animal = party_animal
                existing.nature_lover = nature_lover
                
                existing.luxury_comfort = luxury_comfort
                existing.morning_person = morning_person
                existing.planning_freak = planning_freak
                existing.foodie_level = foodie_level
                existing.sporty_spice = sporty_spice
                existing.chaos_tolerance = chaos_tolerance
                
                existing.city_trip = city_trip
                existing.road_trip = road_trip
                existing.backpacking = backpacking
                existing.local_contact = local_contact
                existing.digital_detox = digital_detox
                
                # Defaults
                existing.social_battery = social_battery
                existing.leader_role = leader_role
                existing.talkative = talkative
                existing.sustainability = sustainability

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
                    beach_person=beach_person,
                    culture_interest=culture_interest,
                    party_animal=party_animal,
                    nature_lover=nature_lover,
                    
                    luxury_comfort=luxury_comfort,
                    morning_person=morning_person,
                    planning_freak=planning_freak,
                    foodie_level=foodie_level,
                    sporty_spice=sporty_spice,
                    chaos_tolerance=chaos_tolerance,
                    
                    city_trip=city_trip,
                    road_trip=road_trip,
                    backpacking=backpacking,
                    local_contact=local_contact,
                    digital_detox=digital_detox,
                    
                    social_battery=social_battery,
                    leader_role=leader_role,
                    talkative=talkative,
                    sustainability=sustainability
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
    Matching algoritme gebaseerd op 16 Vibe Check vragen + Basis info
    Totaal score = 70% Vibe + 30% Logistiek (Leeftijd, Budget, Periode)
    """
    
    # Helper om veilig waardes op te halen (voorkomt NoneType errors)
    def get_val(obj, attr, default=3):
        val = getattr(obj, attr, None)
        return val if val is not None else default

    # --- 1. LOGISTIEK (30 punten) ---
    logistics_score = 0
    
    # Leeftijd (10 punten)
    age1 = get_val(profile1, 'age', 25)
    age2 = get_val(profile2, 'age', 25)
    age_diff = abs(age1 - age2)
    
    if age_diff <= 3: logistics_score += 10
    elif age_diff <= 5: logistics_score += 7
    elif age_diff <= 8: logistics_score += 4
    
    # Budget (10 punten)
    b_max1 = get_val(profile1, 'budget_max', 0)
    b_min1 = get_val(profile1, 'budget_min', 0)
    b_max2 = get_val(profile2, 'budget_max', 0)
    b_min2 = get_val(profile2, 'budget_min', 0)
    
    budget_overlap = not (b_max1 < b_min2 or b_max2 < b_min1)
    if budget_overlap:
        logistics_score += 10
        
    # Periode (10 punten)
    p1 = getattr(profile1, 'travel_period', '') or ''
    p2 = getattr(profile2, 'travel_period', '') or ''
    periods1 = set(p1.split(', '))
    periods2 = set(p2.split(', '))
    if 'Flexibel' in periods1 or 'Flexibel' in periods2 or len(periods1.intersection(periods2)) > 0:
        logistics_score += 10
        
    # --- 2. VIBE CHECK (70 punten) ---
    # We vergelijken de 16 vragen. Elke vraag is max 4 punten verschil (1 vs 5).
    # We berekenen de gelijkenis per vraag (1 - diff/4) en nemen het gemiddelde.
    
    vibe_fields = [
        'adventure_level', 'beach_person', 'culture_interest', 'party_animal', 'nature_lover',
        'luxury_comfort', 'morning_person', 'planning_freak', 'foodie_level', 'sporty_spice',
        'chaos_tolerance', 
        'city_trip', 'road_trip', 'backpacking', 'local_contact', 'digital_detox'
    ]
    
    total_similarity = 0
    
    for field in vibe_fields:
        val1 = get_val(profile1, field, 3)
        val2 = get_val(profile2, field, 3)
        
        # Verschil tussen 0 en 4
        diff = abs(val1 - val2)
        
        # Similarity score voor deze vraag (0.0 tot 1.0)
        # 0 verschil = 1.0 (100% match)
        # 4 verschil = 0.0 (0% match)
        similarity = 1 - (diff / 4)
        total_similarity += similarity
        
    # Gemiddelde similarity over 16 vragen (0.0 tot 1.0)
    avg_vibe_score = total_similarity / len(vibe_fields)
    
    # Omzetten naar punten (max 70)
    vibe_points = avg_vibe_score * 70
    
    # --- TOTAAL ---
    final_score = logistics_score + vibe_points
    
    return int(final_score)
