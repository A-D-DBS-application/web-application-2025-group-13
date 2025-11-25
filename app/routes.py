from flask import render_template, request, redirect, url_for, session, flash
from app import db
from app.models import User, Organiser, Trip, TravelerProfile, Group, Notification
from datetime import datetime
import random

def register_routes(app):
    
    # --- CONTEXT PROCESSOR VOOR NOTIFICATIES ---
    @app.context_processor
    def inject_notifications():
        if 'user_id' in session and session.get('role') == 'traveller':
            unread_count = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
            return dict(unread_notifications_count=unread_count)
        return dict(unread_notifications_count=0)

    @app.route('/')
    def home():
        if session.get('role') == 'organizer':
            return redirect(url_for('organizer_dashboard'))
        return render_template('index.html')

    # --- NOTIFICATIES ---
    @app.route('/notifications')
    def notifications():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        my_notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all()
        
        # Markeer alles als gelezen als je de pagina opent (optioneel, of via aparte knop)
        # Laten we het via een aparte actie doen zodat ze 'nieuw' blijven tot de gebruiker ze wegklikt of leest.
        
        return render_template('notifications.html', notifications=my_notifications)

    @app.route('/notifications/mark-read/<int:notif_id>')
    def mark_notification_read(notif_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        notif = Notification.query.get(notif_id)
        if notif and notif.user_id == session['user_id']:
            notif.is_read = True
            db.session.commit()
            
        return redirect(url_for('notifications'))

    @app.route('/notifications/mark-all-read')
    def mark_all_notifications_read():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        unread = Notification.query.filter_by(user_id=session['user_id'], is_read=False).all()
        for n in unread:
            n.is_read = True
        db.session.commit()
        
        return redirect(url_for('notifications'))

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/example-trips')
    def example_trips():
        # Statische pagina met voorbeeldreizen (IJsland & Bali)
        return render_template('example_trips.html')

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
            
            # --- NIEUW: BUDDY LOGICA ---
            buddy_email = request.form.get('buddy_email')
            linked_buddy_id = None
            
            if buddy_email and buddy_email.strip() != "":
                # Zoek de buddy in de database
                buddy_user = User.query.filter_by(email=buddy_email.strip()).first()
                
                if buddy_user:
                    linked_buddy_id = buddy_user.id
                    
                    # Link BUDDY aan HUIDIGE user (wederzijds)
                    buddy_profile = TravelerProfile.query.filter_by(user_id=buddy_user.id).first()
                    if buddy_profile:
                        buddy_profile.linked_buddy_id = session['user_id']
                    
                    flash(f'Je bent nu gekoppeld aan {buddy_user.name}! Jullie komen in dezelfde groep.', 'success')
                else:
                    flash(f'Let op: We konden geen gebruiker vinden met email {buddy_email}. Zorg dat zij zich ook registreren!', 'warning')
            
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
                
                if linked_buddy_id:
                    existing.linked_buddy_id = linked_buddy_id

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
                    sustainability=sustainability,
                    
                    linked_buddy_id=linked_buddy_id
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
        
        # Beperk tot top 10 matches
        good_matches = good_matches[:10]
        
        return render_template('match.html', matches=good_matches, my_profile=my_profile)
    
    # --- MIJN GROEP ---
    @app.route('/my-group')
    def my_group():
        if 'user_id' not in session or session.get('role') == 'organizer':
            flash('Je moet ingelogd zijn als reiziger.', 'danger')
            return redirect(url_for('login'))
        
        # Haal profiel op (voor status check)
        my_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()

        # Zoek in welke groep de user zit
        my_group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        
        if not my_group_entry:
            return render_template('my_group.html', group=None, my_profile=my_profile)
            
        # Haal alle leden van deze groep op
        group_members_entries = Group.query.filter_by(match_id=my_group_entry.match_id).all()
        
        members = []
        for entry in group_members_entries:
            user = User.query.get(entry.user_id)
            profile = TravelerProfile.query.filter_by(user_id=entry.user_id).first()
            members.append({'user': user, 'profile': profile})
            
        # Check of er een reis gekoppeld is aan deze groep
        # We zoeken een Trip met match_id gelijk aan mijn group_id
        assigned_trip = Trip.query.filter_by(match_id=my_group_entry.match_id).first()
        
        # Bereken beschikbare plekken
        spots_left = 0
        if assigned_trip:
            confirmed_count = Group.query.filter_by(match_id=my_group_entry.match_id, confirmed=True).count()
            spots_left = max(0, assigned_trip.max_spots - confirmed_count)
        
        return render_template('my_group.html', 
                               group_id=my_group_entry.match_id, 
                               members=members, 
                               trip=assigned_trip,
                               my_entry=my_group_entry,
                               spots_left=spots_left)

    @app.route('/pay-deposit', methods=['POST'])
    def pay_deposit():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        my_group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        
        if not my_group_entry:
            return redirect(url_for('home'))
            
        # Check of er nog plek is
        assigned_trip = Trip.query.filter_by(match_id=my_group_entry.match_id).first()
        if not assigned_trip:
            flash('Er is nog geen reis gekoppeld.', 'warning')
            return redirect(url_for('my_group'))
            
        confirmed_count = Group.query.filter_by(match_id=my_group_entry.match_id, confirmed=True).count()
        
        if confirmed_count >= assigned_trip.max_spots:
            flash('Helaas, de reis is volzet!', 'danger')
            return redirect(url_for('my_group'))
            
        # "Betaling" verwerken
        my_group_entry.payment_status = 'paid'
        my_group_entry.confirmed = True
        
        # Notificatie
        create_notification(session['user_id'], f"Betaling ontvangen! Je plek voor {assigned_trip.destination} is definitief.")
        
        db.session.commit()
        flash('Betaling geslaagd! Je gaat mee op reis! 🌍✈️', 'success')
            
        return redirect(url_for('my_group'))

    @app.route('/leave-group', methods=['POST'])
    def leave_group():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        # Zoek de entry en verwijder
        my_group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        
        if my_group_entry:
            db.session.delete(my_group_entry)
            
            # Zet profiel op inactief (niet direct opnieuw matchen)
            profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
            if profile:
                profile.is_active = False
                
            db.session.commit()
            flash('Je hebt de groep verlaten. Je staat nu op "Niet beschikbaar" voor nieuwe matches.', 'info')
        
        return redirect(url_for('my_group'))

    @app.route('/update-matching-status', methods=['POST'])
    def update_matching_status():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        status = request.form.get('status') # 'active' or 'inactive'
        profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        
        if profile:
            if status == 'active':
                profile.is_active = True
                flash('Je staat weer AAN! We gaan een nieuwe groep voor je zoeken.', 'success')
            else:
                profile.is_active = False
                flash('Je staat nu UIT. Je wordt niet meegenomen in nieuwe groepen.', 'info')
            db.session.commit()
            
        return redirect(url_for('my_group'))

    # --- ORGANIZER DASHBOARD ---
    @app.route('/organizer/dashboard', methods=['GET', 'POST'])
    def organizer_dashboard():
        # Check of je organisator bent
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            # Check of het een "Maak Groepen" actie is
            if 'generate_groups' in request.form:
                create_automatic_groups()
                flash('Groepen zijn automatisch gegenereerd op basis van matches!', 'success')
                return redirect(url_for('organizer_dashboard'))
            
            # Check of het een "Koppel Reis" actie is
            if 'assign_trip' in request.form:
                group_id = request.form.get('group_id')
                trip_id = request.form.get('trip_id')
                
                if group_id and trip_id:
                    # Update de trip met het match_id (wat we gebruiken als group_id)
                    trip = Trip.query.get(trip_id)
                    trip.match_id = group_id
                    
                    # NOTIFICATIE: Reis gekoppeld
                    # Zoek alle leden van deze groep
                    members = Group.query.filter_by(match_id=group_id).all()
                    for m in members:
                        create_notification(m.user_id, f"Er is een reis gekoppeld aan jouw groep! Jullie gaan naar {trip.destination}. ✈️")
                    
                    db.session.commit()
                    flash(f'Reis gekoppeld aan Groep {group_id}!', 'success')
                return redirect(url_for('organizer_dashboard'))

            # Anders: Nieuwe reis aanmaken
            try:
                # Data ophalen
                dest = request.form.get('destination')
                price = request.form.get('price')
                s_date = request.form.get('start_date')
                e_date = request.form.get('end_date')
                desc = request.form.get('description')
                acts = request.form.get('activities')
                
                # Nieuwe velden
                max_spots = int(request.form.get('max_spots', 20))
                deposit_amount = float(request.form.get('deposit_amount', 0.0))
                
                # Trip aanmaken
                new_trip = Trip(
                    travel_org_id=session['user_id'],
                    destination=dest,
                    price=float(price), # Zorg dat het een getal is
                    start_date=s_date,
                    end_date=e_date,
                    description=desc,
                    activities=acts,
                    match_id=None, # Expliciet leeg laten
                    max_spots=max_spots,
                    deposit_amount=deposit_amount
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
        
        # Groepen ophalen (unieke match_ids)
        # We halen alle groepsleden op en groeperen ze per match_id
        all_group_members = Group.query.all()
        groups = {}
        group_vibes = {}
        grouped_user_ids = []

        for member in all_group_members:
            grouped_user_ids.append(member.user_id)
            if member.match_id not in groups:
                groups[member.match_id] = []
            
            # User info ophalen
            user = User.query.get(member.user_id)
            groups[member.match_id].append(user)
            
        # Calculate vibes for each group
        for match_id in groups.keys():
            group_vibes[match_id] = calculate_group_vibe(match_id)

        # Unassigned users ophalen (voor dropdown)
        # Dit zijn users die NIET in grouped_user_ids zitten
        # We nemen aan dat alle users in User tabel reizigers zijn (tenzij ze ook in Organiser staan, maar dat is aparte tabel)
        unassigned_users = User.query.filter(User.id.notin_(grouped_user_ids)).all()
            
        return render_template('organizer_dashboard.html', 
                               trips=my_trips, 
                               groups=groups, 
                               group_vibes=group_vibes,
                               unassigned_users=unassigned_users)

    # --- GROEP BEHEER (ORGANIZER) ---
    @app.route('/organizer/remove_member/<int:user_id>', methods=['POST'])
    def remove_group_member(user_id):
        if 'user_id' not in session or session.get('role') != 'organizer':
            return redirect(url_for('home'))
            
        group_entry = Group.query.filter_by(user_id=user_id).first()
        if group_entry:
            db.session.delete(group_entry)
            db.session.commit()
            flash('Reiziger verwijderd uit de groep.', 'success')
            
        return redirect(url_for('organizer_dashboard'))

    @app.route('/organizer/add_member', methods=['POST'])
    def add_group_member():
        if 'user_id' not in session or session.get('role') != 'organizer':
            return redirect(url_for('home'))
            
        user_id = request.form.get('user_id')
        group_id = request.form.get('group_id')
        
        if user_id and group_id:
            new_entry = Group(
                match_id=group_id,
                user_id=user_id,
                role='member',
                confirmed=False
            )
            db.session.add(new_entry)
            
            # NOTIFICATIE: Handmatig toegevoegd
            create_notification(user_id, f"De organisator heeft je toegevoegd aan Groep #{group_id}.")
            
            db.session.commit()
            flash('Reiziger toegevoegd aan de groep.', 'success')
            
        return redirect(url_for('organizer_dashboard'))

    # --- REIZIGER CONFIRMATION ---
    @app.route('/confirm-trip', methods=['POST'])
    def confirm_trip():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        if group_entry:
            group_entry.confirmed = True
            db.session.commit()
            flash('Je hebt je reis bevestigd! 🌍✈️', 'success')
            
        return redirect(url_for('my_group'))

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

# --- ALGORITME VOOR GROEPSVORMING ---
def create_automatic_groups():
    """
    Greedy Best-Match Algoritme met Buddy Support:
    1. Haal alle gebruikers op die nog GEEN groep hebben.
    2. Kies een willekeurige gebruiker ('seed').
    3. Check of seed een buddy heeft -> voeg toe.
    4. Zoek de beste matches voor de groep.
    5. Als een match een buddy heeft -> voeg die ook toe.
    6. Herhaal tot groep vol is of iedereen op is.
    """
    
    # 1. Haal alle gebruikers op die al in een groep zitten
    grouped_user_ids = [g.user_id for g in Group.query.all()]
    
    # 2. Haal alle profielen op van gebruikers die nog NIET in een groep zitten
    # EN die actief op zoek zijn (is_active=True)
    available_profiles = TravelerProfile.query.filter(
        TravelerProfile.user_id.notin_(grouped_user_ids),
        TravelerProfile.is_active == True
    ).all()
    
    # Als er te weinig mensen zijn, stop
    if len(available_profiles) < 1:
        return

    # We gebruiken een uniek ID voor elke nieuwe groep
    last_group = Group.query.order_by(Group.match_id.desc()).first()
    next_group_id = (last_group.match_id + 1) if last_group and last_group.match_id else 1
    
    GROUP_SIZE = 20
    
    while len(available_profiles) > 0:
        # Start nieuwe groep
        current_group_id = next_group_id
        next_group_id += 1
        
        group_members = []
        
        # Helper om profiel uit available te halen op ID
        def pop_profile_by_id(uid):
            for i, p in enumerate(available_profiles):
                if p.user_id == uid:
                    return available_profiles.pop(i)
            return None

        # Pak de eerste persoon als 'seed'
        seed_profile = available_profiles.pop(0)
        group_members.append(seed_profile)
        
        # Check of seed een buddy heeft die ook beschikbaar is
        if seed_profile.linked_buddy_id:
            buddy = pop_profile_by_id(seed_profile.linked_buddy_id)
            if buddy:
                group_members.append(buddy)
        
        # Vul de rest van de groep
        while len(group_members) < GROUP_SIZE and len(available_profiles) > 0:
            candidates = []
            for candidate in available_profiles:
                score = calculate_match_score(seed_profile, candidate)
                if score != -1: # Alleen als budget past
                    candidates.append((score, candidate))
            
            # Sorteer op score (hoogste eerst)
            candidates.sort(key=lambda x: x[0], reverse=True)
            
            if not candidates:
                break # Geen geschikte kandidaten meer (budget mismatch?)
            
            # Pak de beste
            best_score, best_match = candidates[0]
            
            # Verwijder uit available
            available_profiles.remove(best_match)
            group_members.append(best_match)
            
            # Check of DEZE match een buddy heeft
            if best_match.linked_buddy_id and len(group_members) < GROUP_SIZE:
                buddy = pop_profile_by_id(best_match.linked_buddy_id)
                if buddy:
                    group_members.append(buddy)
        
        # Sla de groep op in de database
        for member in group_members:
            new_group_entry = Group(
                match_id=current_group_id,
                user_id=member.user_id,
                role='member',
                confirmed=False
            )
            db.session.add(new_group_entry)
            
            # NOTIFICATIE: Je bent in een groep geplaatst
            create_notification(member.user_id, f"Je bent toegevoegd aan Groep #{current_group_id}! Bekijk snel je nieuwe reisgenoten.")
            
    db.session.commit()

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
    else:
        return -1 # Strict budget filter
        
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

def calculate_group_vibe(match_id):
    """
    Calculates the 'vibe' of a group based on average profile scores.
    Returns a list of strings (tags).
    """
    # Get all user IDs in this group
    group_entries = Group.query.filter_by(match_id=match_id).all()
    user_ids = [g.user_id for g in group_entries]
    
    if not user_ids:
        return ["Lege Groep"]

    profiles = TravelerProfile.query.filter(TravelerProfile.user_id.in_(user_ids)).all()
    
    if not profiles:
        return ["Geen Profielen"]

    # Helper to get average of an attribute
    def get_avg(attr):
        values = [getattr(p, attr, 3) for p in profiles if getattr(p, attr, None) is not None]
        if not values: return 0
        return sum(values) / len(values)

    tags = []
    
    # Thresholds (1-5 scale)
    HIGH = 3.8
    
    if get_avg('party_animal') >= HIGH: tags.append("🎉 Party Squad")
    if get_avg('culture_interest') >= HIGH: tags.append("🏛️ Cultuur Lovers")
    if get_avg('nature_lover') >= HIGH: tags.append("🌲 Natuur Vrienden")
    if get_avg('adventure_level') >= HIGH: tags.append("🧗 Avonturiers")
    if get_avg('beach_person') >= HIGH: tags.append("🏖️ Strandgangers")
    if get_avg('foodie_level') >= HIGH: tags.append("🍕 Foodies")
    if get_avg('luxury_comfort') >= HIGH: tags.append("💎 Luxe Paardjes")
    
    # Budget check (average max budget)
    avg_budget = get_avg('budget_max')
    if avg_budget > 0 and avg_budget < 800: tags.append("💰 Budget Reizigers")
    
    # Age range
    ages = [p.age for p in profiles if p.age]
    if ages:
        avg_age = sum(ages) / len(ages)
        if avg_age < 25: tags.append("🎓 Jongeren")
        elif avg_age > 40: tags.append("👴 40+")

    if not tags:
        tags.append("⚖️ Gebalanceerde Groep")
        
    return tags

def create_notification(user_id, message):
    """Helper om een notificatie aan te maken"""
    try:
        notif = Notification(
            user_id=user_id,
            message=message,
            created_at=datetime.now(),
            is_read=False
        )
        db.session.add(notif)
        # Commit moet door de aanroeper gedaan worden of hier als we zeker weten dat het mag
        # We doen hier geen commit om transacties niet te breken, tenzij we het expliciet willen.
        # Maar voor het gemak doen we het hier wel, tenzij er een lopende transactie is.
        # In SQLAlchemy sessie management is het beter om het aan de caller over te laten als onderdeel van een grotere actie.
        # Echter, voor simpele notificaties is het vaak handig.
        # Laten we het veilig spelen en de caller laten committen.
    except Exception as e:
        print(f"Fout bij maken notificatie: {e}")
