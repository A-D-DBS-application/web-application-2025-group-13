from flask import render_template, request, redirect, url_for, session, flash, Response
from app import db
from app.models import User, Organiser, Trip, TravelerProfile, Group, Notification
from datetime import datetime
from sqlalchemy.orm import joinedload
from icalendar import Calendar, Event

# === CONFIGURATIE & LIJSTEN ===

# 1. Reisperiodes
TRAVEL_PERIODS = [
    {"name": "Winter (dec-feb)", "icon": "❄️"},
    {"name": "Lente (mrt-mei)", "icon": "🌸"},
    {"name": "Zomer (jun-aug)", "icon": "☀️"},
    {"name": "Herfst (sep-nov)", "icon": "🍂"},
    {"name": "Flexibel", "icon": "🔄"}
]

# 2. Vibe Check Vragen
VIBE_QUESTIONS = [
    {"id": "adventure_level",  "text": "Hoe avontuurlijk ben je op reis?", "min": "😌 Liever rustig", "max": "🔥 Zoek avontuur"},
    {"id": "beach_person",     "text": "Zon & Strand of Schaduw?", "min": "🚫 Geen zand", "max": "🏖️ Bakken"},
    {"id": "culture_interest", "text": "Interesse in cultuur?", "min": "🥱 Saai", "max": "🏛️ Museumrat"},
    {"id": "party_animal",     "text": "Uitgaan?", "min": "🍵 Thee & Boek", "max": "🎉 Tot het gaatje"},
    {"id": "nature_lover",     "text": "Natuur?", "min": "🏙️ Asfalt", "max": "🌲 Into the Wild"},
    {"id": "luxury_comfort",   "text": "Comfort?", "min": "⛺ Basic", "max": "💎 Luxe"},
    {"id": "morning_person",   "text": "Ritme?", "min": "😴 Snooze", "max": "🌅 Vroege vogel"},
    {"id": "planning_freak",   "text": "Planning?", "min": "📋 Alles vast", "max": "🍃 Go with flow"},
    {"id": "foodie_level",     "text": "Eten?", "min": "🥪 Brandstof", "max": "🍜 Genieten"},
    {"id": "sporty_spice",     "text": "Activiteit?", "min": "🛗 Lift nemen", "max": "🏃‍♂️ Berg op"},
    {"id": "chaos_tolerance",  "text": "Chaos?", "min": "🤯 Stress", "max": "🧘 Zen"},
    {"id": "city_trip",        "text": "Citytrips?", "min": "🏙️ Mwah", "max": "😍 Ja graag"},
    {"id": "road_trip",        "text": "Reizen?", "min": "✈️ Vliegen", "max": "🚐 Roadtrip"},
    {"id": "backpacking",      "text": "Bagage?", "min": "🧳 Koffer", "max": "🎒 Rugzak"},
    {"id": "local_contact",    "text": "Locals?", "min": "🫧 Bubbel", "max": "🌍 Connecten"},
    {"id": "digital_detox",    "text": "Internet?", "min": "📱 Nodig", "max": "📵 Offline"}
]

# =========================================================
# === HELPER FUNCTIES (LOGICA) ===
# =========================================================

def get_intake_data_from_request():
    """Haalt formulierdata op en zet dit om naar een dictionary."""
    def get_int(name, default=3):
        try: return int(request.form.get(name, default))
        except (ValueError, TypeError): return default

    # Basisgegevens
    data = {
        'age': get_int('age', 18),
        'budget_min': get_int('budget_min', 0),
        'budget_max': get_int('budget_max', 0),
        'travel_period': ', '.join(request.form.getlist('period')),
        # Defaults
        'social_battery': 3, 'leader_role': 3, 'talkative': 3, 'sustainability': 3
    }

    # Dynamisch Vibe Vragen toevoegen (Slimme loop!)
    for q in VIBE_QUESTIONS:
        data[q['id']] = get_int(q['id'])

    return data

def calculate_match_score(profile1, profile2):
    """Algoritme: 30% Logistiek (Harde eisen) + 70% Vibe (Interesses)."""
    def get_val(obj, attr, default=3):
        val = getattr(obj, attr, None)
        return val if val is not None else default

    logistics_score = 0
    
    # 1. Leeftijd (Max 10 jaar verschil) - Harde eis
    if abs(get_val(profile1, 'age') - get_val(profile2, 'age')) > 10: return -1
    
    diff = abs(get_val(profile1, 'age') - get_val(profile2, 'age'))
    if diff <= 3: logistics_score += 10
    elif diff <= 5: logistics_score += 7
    elif diff <= 8: logistics_score += 4
    
    # 2. Budget (Overlap check) - Harde eis
    b_max1, b_min1 = get_val(profile1, 'budget_max'), get_val(profile1, 'budget_min')
    b_max2, b_min2 = get_val(profile2, 'budget_max'), get_val(profile2, 'budget_min')
    if (b_max1 < b_min2 or b_max2 < b_min1): return -1 
    logistics_score += 10
        
    # 3. Periode (Overlap check)
    p1 = set((getattr(profile1, 'travel_period', '') or '').split(', '))
    p2 = set((getattr(profile2, 'travel_period', '') or '').split(', '))
    if 'Flexibel' in p1 or 'Flexibel' in p2 or not p1.isdisjoint(p2): logistics_score += 10
        
    # 4. Vibe Check (Loop door de lijst heen)
    total_sim, total_weight = 0, 0
    # Belangrijke vragen wegen zwaarder
    important_ids = ['adventure_level', 'culture_interest', 'nature_lover', 'luxury_comfort']
    
    for q in VIBE_QUESTIONS:
        fid = q['id']
        weight = 1.5 if fid in important_ids else 1.0
        # Verschil tussen 0 (identiek) en 4 (totaal anders)
        diff = abs(get_val(profile1, fid) - get_val(profile2, fid))
        similarity = 1 - (diff / 4)
        
        total_sim += similarity * weight
        total_weight += weight
        
    return int(logistics_score + ((total_sim / total_weight) * 70))

def calculate_group_vibe(match_id):
    """Berekent tags zoals 'Party Squad' op basis van groepsgemiddelde."""
    uids = [g.user_id for g in Group.query.filter_by(match_id=match_id).all()]
    profs = TravelerProfile.query.filter(TravelerProfile.user_id.in_(uids)).all()
    if not profs: return ["Lege Groep"]

    def avg(attr): 
        v = [getattr(p, attr, 3) for p in profs if getattr(p, attr, None) is not None]
        return sum(v)/len(v) if v else 0

    tags = []
    if avg('party_animal') >= 3.8: tags.append("🎉 Party Squad")
    if avg('culture_interest') >= 3.8: tags.append("🏛️ Cultuur Lovers")
    if avg('nature_lover') >= 3.8: tags.append("🌲 Natuur Vrienden")
    if avg('adventure_level') >= 3.8: tags.append("🧗 Avonturiers")
    if avg('budget_max') < 800: tags.append("💰 Budget Reizigers")
    
    ages = [p.age for p in profs if p.age]
    if ages and (sum(ages)/len(ages)) < 25: tags.append("🎓 Jongeren")

    return tags if tags else ["⚖️ Gebalanceerde Groep"]

def get_group_stats(match_id):
    """Verzamelt statistieken voor het organizer dashboard."""
    uids = [g.user_id for g in Group.query.filter_by(match_id=match_id).all()]
    profs = TravelerProfile.query.filter(TravelerProfile.user_id.in_(uids)).all()
    if not profs: return None
        
    ages = [p.age for p in profs if p.age]
    mins = [p.budget_min for p in profs if p.budget_min]
    maxs = [p.budget_max for p in profs if p.budget_max]
    
    # Bereken top interesses dynamisch
    scores = {q['id']: sum(getattr(p, q['id'], 0) or 0 for p in profs) for q in VIBE_QUESTIONS}
    
    return {
        'age_range': f"{min(ages)}-{max(ages)}" if ages else "?",
        'budget_range': f"€{max(mins)}-€{min(maxs)}" if mins and maxs and max(mins) <= min(maxs) else "Krap budget",
        'top_interests': [k.replace('_', ' ').title() for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]]
    }

def create_notification(uid, msg):
    try: db.session.add(Notification(user_id=uid, message=msg, created_at=datetime.now()))
    except: pass

def create_automatic_groups():
    """Greedy algoritme voor groepsvorming."""
    grouped = [g.user_id for g in Group.query.all()]
    available = TravelerProfile.query.filter(TravelerProfile.user_id.notin_(grouped), TravelerProfile.is_active == True).all()
    if not available: return

    last = Group.query.order_by(Group.match_id.desc()).first()
    new_id = (last.match_id + 1) if last and last.match_id else 1
    
    members = [available.pop(0)] # Seed user
    grp_min, grp_max = members[0].budget_min, members[0].budget_max

    while len(members) < 20 and available:
        candidates = []
        for c in available:
            # Check overlap
            p1, p2 = set((members[0].travel_period or '').split(', ')), set((c.travel_period or '').split(', '))
            n_min, n_max = max(grp_min, c.budget_min), min(grp_max, c.budget_max)
            
            if ('Flexibel' in p1 or 'Flexibel' in p2 or not p1.isdisjoint(p2)) and (n_max - n_min >= 500):
                score = calculate_match_score(members[0], c)
                if score >= 50: candidates.append((score, c, n_min, n_max))
        
        if not candidates: break
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        _, best, n_min, n_max = candidates[0]
        available.remove(best)
        members.append(best)
        grp_min, grp_max = n_min, n_max

    for m in members:
        db.session.add(Group(match_id=new_id, user_id=m.user_id, role='member', confirmed=False))
        create_notification(m.user_id, f"Je zit in Groep #{new_id}!")
    db.session.commit()

# =========================================================
# === APP ROUTES ===
# =========================================================

def register_routes(app):
    
    @app.context_processor
    def inject_vars():
        """Zorgt dat de lijsten beschikbaar zijn in ALLE templates (Intake & Edit)."""
        unread_count = 0
        if session.get('role') == 'traveller':
            unread_count = Notification.query.filter_by(user_id=session.get('user_id'), is_read=False).count()
            
        return dict(
            unread_notifications_count=unread_count,
            travel_periods=TRAVEL_PERIODS,
            vibe_questions=VIBE_QUESTIONS
        )

    @app.route('/')
    def home():
        if session.get('role') == 'organizer':
            return redirect(url_for('organizer_dashboard'))
        return render_template('index.html')

    # --- Notification Routes ---
    @app.route('/notifications')
    def notifications():
        if 'user_id' not in session: return redirect(url_for('login'))
        return render_template('notifications.html', notifications=Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all())

    @app.route('/notifications/mark-read/<int:notif_id>')
    def mark_notification_read(notif_id):
        notification = Notification.query.get(notif_id)
        if notification and notification.user_id == session.get('user_id'):
            notification.is_read = True
            db.session.commit()
        return redirect(url_for('notifications'))
    
    @app.route('/notifications/mark-all-read')
    def mark_all_notifications_read():
        if 'user_id' in session:
            for notification in Notification.query.filter_by(user_id=session['user_id'], is_read=False).all():
                notification.is_read = True
            db.session.commit()
        return redirect(url_for('notifications'))

    # --- Static Pages ---
    @app.route('/about')
    def about(): return render_template('about.html')
    @app.route('/example-trips')
    def example_trips(): return render_template('example_trips.html')
    @app.route('/contact')
    def contact(): return render_template('contact.html')

    # --- INTAKE & MATCHING ---
    @app.route('/intake')
    def intake():
        if 'user_id' not in session or session.get('role') == 'organizer':
            flash('Login vereist.', 'warning'); return redirect(url_for('login'))
        
        # Bestaat profiel? -> Overzicht. Zo niet -> Formulier
        existing = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        if existing:
            return render_template('intake_overview.html', user=User.query.get(session['user_id']), profile=existing)
        
        return render_template('intake.html', profile=None) # Lijsten komen nu via context_processor
    
    @app.route('/edit-intake')
    def edit_intake():
        if 'user_id' not in session: return redirect(url_for('login'))
        return render_template('intake.html', profile=TravelerProfile.query.filter_by(user_id=session['user_id']).first())

    @app.route('/submit-intake', methods=['POST'])
    def submit_intake():
        if 'user_id' not in session: return redirect(url_for('login'))
        try:
            data = get_intake_data_from_request()
            
            # Buddy logic
            email = request.form.get('buddy_email', '').strip()
            if email:
                buddy = User.query.filter_by(email=email).first()
                if buddy:
                    data['linked_buddy_id'] = buddy.id
                    buddy_profile = TravelerProfile.query.filter_by(user_id=buddy.id).first()
                    if buddy_profile: 
                        buddy_profile.linked_buddy_id = session['user_id']
                    flash(f'Gekoppeld aan {buddy.name}!', 'success')
                else: 
                    flash('Buddy niet gevonden.', 'warning')

            # Save logic
            existing = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                flash('Profiel geüpdatet!', 'success')
            else:
                new_profile = TravelerProfile(user_id=session['user_id'], created_at=datetime.now(), **data)
                db.session.add(new_profile)
                flash('Profiel aangemaakt!', 'success')
            
            db.session.commit()
            return redirect(url_for('intake'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash('Fout bij opslaan.', 'danger')
            return redirect(url_for('intake'))

    @app.route('/match')
    def match():
        if 'user_id' not in session: return redirect(url_for('login'))
        
        my_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        if not my_profile: return redirect(url_for('intake'))
        
        others = TravelerProfile.query.options(joinedload(TravelerProfile.user)).filter(TravelerProfile.user_id != session['user_id']).all()
        matches = []
        
        for other in others:
            score = calculate_match_score(my_profile, other)
            if score >= 50:
                matches.append({
                    'user': other.user, 
                    'profile': other, 
                    'score': score, 
                    'percentage': score
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Toon alleen de top 10 matches
        top_matches = matches[:10]
        
        return render_template('match.html', matches=top_matches, my_profile=my_profile)

    @app.route('/my-group')
    def my_group():
        if 'user_id' not in session: return redirect(url_for('login'))
        
        my_group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        my_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()

        if not my_group_entry: 
            return render_template('my_group.html', group=None, my_profile=my_profile)
            
        # OPTIMALISATIE: Eager loading van User en Profile via de Group relatie
        # We halen de Group entries op, en laden direct de gekoppelde User EN diens Profile
        group_entries = Group.query.options(
            joinedload(Group.user).joinedload(User.profile)
        ).filter_by(match_id=my_group_entry.match_id).all()
        
        members = []
        for entry in group_entries:
            # Geen extra queries meer nodig hier!
            # Check of profile bestaat om errors te voorkomen
            profile = entry.user.profile if entry.user else None
            members.append({'user': entry.user, 'profile': profile})
            
        trip = Trip.query.filter_by(match_id=my_group_entry.match_id).first()
        spots_left = 0
        
        if trip:
            paid_count = Group.query.filter_by(match_id=my_group_entry.match_id, payment_status='paid').count()
            spots_left = max(0, trip.max_spots - paid_count)
        
        return render_template('my_group.html', 
                               group_id=my_group_entry.match_id, 
                               members=members, 
                               trip=trip, 
                               my_entry=my_group_entry, 
                               spots_left=spots_left,
                               my_profile=my_profile)

    # --- NIEUWE ROUTE: ICAL EXPORT ---
    @app.route('/my-group/calendar')
    def export_group_calendar():
        if 'user_id' not in session: return redirect(url_for('login'))
        
        # 1. Haal groep en reis op
        group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        if not group_entry or not group_entry.match_id:
            flash("Je zit nog niet in een groep.", "warning")
            return redirect(url_for('my_group'))
            
        trip = Trip.query.filter_by(match_id=group_entry.match_id).first()
        if not trip:
            flash("Er is nog geen reis gekoppeld aan jouw groep.", "warning")
            return redirect(url_for('my_group'))
            
        # 2. Maak de iCal aan
        cal = Calendar()
        cal.add('prodid', '-//TrailTribe//trailtribe.be//')
        cal.add('version', '2.0')
        
        event = Event()
        event.add('summary', f"TrailTribe Reis: {trip.destination}")
        event.add('dtstart', trip.start_date) # SQLAlchemy Date objecten werken prima hier
        event.add('dtend', trip.end_date)
        event.add('location', trip.destination)
        event.add('description', f"Jouw TrailTribe avontuur naar {trip.destination}!\n\nPrijs: €{trip.price}\nActiviteiten: {trip.activities}")
        
        cal.add_component(event)
        
        # 3. Stuur terug als download
        return Response(
            cal.to_ical(),
            mimetype="text/calendar",
            headers={"Content-Disposition": f"attachment;filename=trailtribe_{trip.destination}.ics"}
        )

    @app.route('/pay-deposit', methods=['POST'])
    def pay_deposit():
        if 'user_id' in session:
            entry = Group.query.filter_by(user_id=session['user_id']).first()
            if entry:
                entry.payment_status = 'paid'
                entry.confirmed = True
                db.session.commit()
                flash('Betaling geslaagd!', 'success')
        return redirect(url_for('my_group'))

    @app.route('/leave-group', methods=['POST'])
    def leave_group():
        if 'user_id' in session:
            entry = Group.query.filter_by(user_id=session['user_id']).first()
            if entry:
                db.session.delete(entry)
                profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
                if profile: 
                    profile.is_active = False
                db.session.commit()
                flash('Je hebt de groep verlaten.', 'info')
        return redirect(url_for('my_group'))

    @app.route('/update-matching-status', methods=['POST'])
    def update_matching_status():
        if 'user_id' in session:
            profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
            if profile:
                profile.is_active = (request.form.get('status') == 'active')
                db.session.commit()
                flash('Status aangepast.', 'success')
        return redirect(url_for('my_group'))

    # --- ORGANIZER ROUTES ---
    @app.route('/organizer/dashboard')
    def organizer_dashboard():
        if session.get('role') != 'organizer': return redirect(url_for('home'))
        
        grouped_users = [u[0] for u in db.session.query(Group.user_id).distinct().all()]
        unassigned_count = User.query.filter(User.id.notin_(grouped_users)).count()
        
        return render_template('organizer_dashboard.html', 
                               total_users=User.query.count(), 
                               total_trips=Trip.query.count(), 
                               total_groups=db.session.query(Group.match_id).distinct().count(),
                               unassigned_users=unassigned_count)
    
    @app.route('/organizer/create-trip', methods=['GET', 'POST'])
    def organizer_create_trip():
        if session.get('role') != 'organizer': return redirect(url_for('home'))
        
        if request.method == 'POST':
            try:
                db.session.add(Trip(
                    travel_org_id=session['user_id'], 
                    destination=request.form['destination'], 
                    price=float(request.form['price']),
                    start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
                    end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
                    description=request.form['description'], 
                    activities=request.form['activities'],
                    max_spots=int(request.form.get('max_spots', 20)), 
                    deposit_amount=float(request.form.get('deposit_amount', 0))
                ))
                db.session.commit()
                flash('Reis succesvol aangemaakt!', 'success')
                return redirect(url_for('organizer_trips'))
            except Exception as e:
                flash(f'Fout bij aanmaken: {e}', 'danger')
        return render_template('organizer_create_trip.html')

    @app.route('/organizer/all-trips', methods=['GET', 'POST'])
    @app.route('/organizer/all-trips', methods=['GET', 'POST'])
    def organizer_trips():
        if session.get('role') != 'organizer': return redirect(url_for('home'))
        
        # --- VERWIJDER LOGICA (AANGEPAST: Iedereen mag verwijderen) ---
        if request.method == 'POST' and 'delete_trip' in request.form:
            trip_id = request.form.get('trip_id')
            trip = Trip.query.get(trip_id)
            
            if trip:
                # Als de reis aan een groep gekoppeld is, de link verbreken
                groups = Group.query.filter_by(match_id=trip.match_id).all()
                for member in groups:
                    create_notification(member.user_id, f"De reis naar {trip.destination} is geannuleerd.")
                
                db.session.delete(trip)
                db.session.commit()
                flash('Reis succesvol verwijderd.', 'info')
            else:
                flash('Reis niet gevonden.', 'warning')
            
            return redirect(url_for('organizer_trips'))
        
        trips = Trip.query.options(joinedload(Trip.organiser)).all()
        trips_data = [{'trip': t, 'organizer_name': t.organiser.name if t.organiser else 'Onbekend'} for t in trips]
        
        return render_template('organizer_trips.html', trips=trips_data)

    @app.route('/organizer/all-users')
    def organizer_users():
        if session.get('role') != 'organizer': return redirect(url_for('home'))
        
        users = User.query.options(joinedload(User.profile), joinedload(User.groups)).all()
        data = []
        for user in users:
            status = "Nog Geen Profiel"
            if user.profile: 
                status = "Actief" if user.profile.is_active else "Pauze"
            if user.groups: 
                group = user.groups[0]
                status = f"{'✅ ' if group.payment_status=='paid' else ''}In Groep #{group.match_id}"
                
            data.append({'user': user, 'profile': user.profile, 'status': status})
            
        return render_template('organizer_users.html', users=data)

    @app.route('/organizer/groups', methods=['GET', 'POST'])
    def organizer_groups():
        if session.get('role') != 'organizer': return redirect(url_for('home'))
        
        if request.method == 'POST':
            # Actie 1: Genereer groepen
            if 'generate_groups' in request.form:
                create_automatic_groups()
                flash('Groepen gegenereerd!', 'success')
            
            # Actie 2: Reis koppelen
            elif 'assign_trip' in request.form:
                group_id = request.form['group_id']
                trip_id = request.form['trip_id']
                trip = Trip.query.get(trip_id)
                
                if trip and not trip.match_id and not Trip.query.filter_by(match_id=group_id).first():
                    trip.match_id = int(group_id)
                    db.session.commit()
                    # Notificatie
                    for member in Group.query.filter_by(match_id=group_id).all():
                        create_notification(member.user_id, f"Bestemming bekend: {trip.destination}!")
                    flash('Reis succesvol gekoppeld!', 'success')
                else: 
                    flash('Kan reis niet koppelen.', 'warning')

            # Actie 3: Lid toevoegen
            elif 'add_member' in request.form:
                user_id = request.form['user_id']
                group_id = request.form['group_id']
                
                if not Group.query.filter_by(user_id=user_id).first():
                    db.session.add(Group(match_id=int(group_id), user_id=int(user_id), role='member', confirmed=False))
                    create_notification(user_id, f"Je bent toegevoegd aan Groep #{group_id}.")
                    db.session.commit()
                    flash('Lid toegevoegd!', 'success')
                else:
                    flash('Gebruiker zit al in een groep.', 'warning')

            # Actie 4: Groep verwijderen
            elif 'delete_group' in request.form:
                group_id = request.form['group_id']
                
                trip = Trip.query.filter_by(match_id=group_id).first()
                if trip: trip.match_id = None
                
                for member in Group.query.filter_by(match_id=group_id).all():
                    profile = TravelerProfile.query.filter_by(user_id=member.user_id).first()
                    if profile: profile.is_active = True
                    create_notification(member.user_id, "Groep is opgeheven.")
                
                Group.query.filter_by(match_id=group_id).delete()
                db.session.commit()
                flash('Groep verwijderd.', 'info')
                
            return redirect(url_for('organizer_groups'))

        # GET Request
        groups = {}
        for member in Group.query.all():
            if member.match_id not in groups: 
                groups[member.match_id] = []
            
            user = User.query.get(member.user_id)
            user.group_status = member.payment_status 
            user.group_confirmed = member.confirmed
            groups[member.match_id].append(user)

        assigned_trips = {t.match_id: t for t in Trip.query.filter(Trip.match_id.isnot(None)).all()}
        
        return render_template('organizer_groups.html', 
                               groups=groups, 
                               group_vibes={k: calculate_group_vibe(k) for k in groups},
                               group_stats={k: get_group_stats(k) for k in groups},
                               trips=Trip.query.filter(Trip.match_id.is_(None)).all(),
                               unassigned_users=User.query.filter(User.id.notin_([g.user_id for g in Group.query.all()])).all(),
                               assigned_trips=assigned_trips)

    @app.route('/organizer/remove_member/<int:user_id>', methods=['POST'])
    def remove_group_member(user_id):
        if session.get('role') == 'organizer':
            Group.query.filter_by(user_id=user_id).delete()
            
            profile = TravelerProfile.query.filter_by(user_id=user_id).first()
            if profile: profile.is_active = True
            
            create_notification(user_id, "Je bent verwijderd uit de groep.")
            db.session.commit()
            flash('Lid verwijderd.', 'info')
        return redirect(url_for('organizer_groups'))

    # --- AUTHENTICATIE ---
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            role = request.form['role']
            
            Model = User if role == 'traveller' else Organiser
            
            if not Model.query.filter_by(email=email).first():
                db.session.add(Model(name=name, email=email, created_at=datetime.now()))
                db.session.commit()
                flash('Account aangemaakt!', 'success')
                return redirect(url_for('login'))
            flash('Email bestaat al.', 'danger')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            
            user = User.query.filter_by(email=email).first()
            if user:
                session.update({'user_id': user.id, 'name': user.name, 'role': 'traveller'})
                flash(f'Welkom terug, {user.name}!', 'success')
                return redirect(url_for('home'))
            
            organizer = Organiser.query.filter_by(email=email).first()
            if organizer:
                session.update({'user_id': organizer.id, 'name': organizer.name, 'role': 'organizer'})
                flash(f'Welkom, {organizer.name}!', 'success')
                return redirect(url_for('organizer_dashboard'))
            
            flash('Ongeldig emailadres.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Je bent uitgelogd.', 'info')
        return redirect(url_for('login'))