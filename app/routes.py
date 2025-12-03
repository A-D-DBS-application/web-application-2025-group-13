from flask import render_template, request, redirect, url_for, session, flash
from app import db
from app.models import User, Organiser, Trip, TravelerProfile, Group, Notification
from datetime import datetime


# ------------------------------------
# --- HELPER FUNCTIES VOOR ALGORITME ---
# ------------------------------------

def calculate_match_score(profile1, profile2):
    """
    Matching algoritme gebaseerd op 16 Vibe Check vragen + Basis info
    Totaal score = 70% Vibe + 30% Logistiek (Leeftijd, Budget, Periode)
    """
    
    def get_val(obj, attr, default=3):
        val = getattr(obj, attr, None)
        return val if val is not None else default

    # --- 1. LOGISTIEK (30 punten) ---
    logistics_score = 0
    
    # Leeftijd (10 punten)
    age1 = get_val(profile1, 'age', 25)
    age2 = get_val(profile2, 'age', 25)
    age_diff = abs(age1 - age2)
    
    # NIEUW: Harde eis van max 10 jaar verschil
    if age_diff > 10:
        return -1
    
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
        return -1 
        
    # Periode (10 punten)
    p1 = getattr(profile1, 'travel_period', '') or ''
    p2 = getattr(profile2, 'travel_period', '') or ''
    periods1 = set(p1.split(', '))
    periods2 = set(p2.split(', '))
    if 'Flexibel' in periods1 or 'Flexibel' in periods2 or len(periods1.intersection(periods2)) > 0:
        logistics_score += 10
        
    # --- 2. VIBE CHECK (70 punten) ---
    vibe_fields = [
        'adventure_level', 'beach_person', 'culture_interest', 'party_animal', 'nature_lover',
        'luxury_comfort', 'morning_person', 'planning_freak', 'foodie_level', 'sporty_spice',
        'chaos_tolerance', 
        'city_trip', 'road_trip', 'backpacking', 'local_contact', 'digital_detox'
    ]
    
    # Belangrijke velden krijgen iets meer gewicht (1.5x)
    important_fields = ['adventure_level', 'culture_interest', 'nature_lover', 'luxury_comfort']
    
    total_weighted_similarity = 0
    total_weight = 0
    
    for field in vibe_fields:
        val1 = get_val(profile1, field, 3)
        val2 = get_val(profile2, field, 3)
        
        diff = abs(val1 - val2)
        similarity = 1 - (diff / 4)
        
        weight = 1.5 if field in important_fields else 1.0
        
        total_weighted_similarity += similarity * weight
        total_weight += weight
        
    avg_vibe_score = total_weighted_similarity / total_weight
    vibe_points = avg_vibe_score * 70
    
    final_score = logistics_score + vibe_points
    
    return int(final_score)

def calculate_group_vibe(match_id):
    """Berekent de 'vibe' van een groep."""
    
    group_entries = Group.query.filter_by(match_id=match_id).all()
    user_ids = [g.user_id for g in group_entries]
    profiles = TravelerProfile.query.filter(TravelerProfile.user_id.in_(user_ids)).all()
    
    if not profiles:
        return ["Lege Groep"]

    def get_avg(attr):
        values = [getattr(p, attr, 3) for p in profiles if getattr(p, attr, None) is not None]
        if not values: return 0
        return sum(values) / len(values)

    tags = []
    HIGH = 3.8
    
    if get_avg('party_animal') >= HIGH: tags.append("🎉 Party Squad")
    if get_avg('culture_interest') >= HIGH: tags.append("🏛️ Cultuur Lovers")
    if get_avg('nature_lover') >= HIGH: tags.append("🌲 Natuur Vrienden")
    if get_avg('adventure_level') >= HIGH: tags.append("🧗 Avonturiers")
    if get_avg('beach_person') >= HIGH: tags.append("🏖️ Strandgangers")
    if get_avg('foodie_level') >= HIGH: tags.append("🍕 Foodies")
    
    avg_budget = get_avg('budget_max')
    if avg_budget > 0 and avg_budget < 800: tags.append("💰 Budget Reizigers")
    
    ages = [p.age for p in profiles if p.age]
    if ages:
        avg_age = sum(ages) / len(ages)
        if avg_age < 25: tags.append("🎓 Jongeren")
        elif avg_age > 40: tags.append("👴 40+")

    if not tags:
        tags.append("⚖️ Gebalanceerde Groep")
        
    return tags

def get_group_stats(match_id):
    """Berekent statistieken voor een groep (leeftijd, budget, interesses)."""
    group_entries = Group.query.filter_by(match_id=match_id).all()
    user_ids = [g.user_id for g in group_entries]
    profiles = TravelerProfile.query.filter(TravelerProfile.user_id.in_(user_ids)).all()
    
    if not profiles:
        return None
        
    # Leeftijd (Min - Max + Gemiddelde)
    ages = [p.age for p in profiles if p.age]
    if ages:
        avg_age = round(sum(ages) / len(ages))
        age_str = f"{min(ages)} - {max(ages)} (Gem. {avg_age})"
    else:
        age_str = "?"
        
    # Budget (Overlap: Hoogste Minimum - Laagste Maximum)
    mins = [p.budget_min for p in profiles if p.budget_min is not None]
    maxs = [p.budget_max for p in profiles if p.budget_max is not None]
    
    if mins and maxs:
        safe_min = max(mins) # De hoogste ondergrens
        safe_max = min(maxs) # De laagste bovengrens
        
        if safe_min > safe_max:
            budget_str = f"€{safe_max} (Krap)"
        else:
            budget_str = f"€{safe_min} - €{safe_max}"
    else:
        budget_str = "?"
    
    # Top interests
    interest_fields = [
        'adventure_level', 'beach_person', 'culture_interest', 'party_animal', 'nature_lover',
        'foodie_level', 'sporty_spice'
    ]
    
    interest_scores = {field: 0 for field in interest_fields}
    for p in profiles:
        for field in interest_fields:
            val = getattr(p, field, 0) or 0
            interest_scores[field] += val
            
    # Sort by score
    sorted_interests = sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = [k.replace('_', ' ').title() for k, v in sorted_interests[:3]]
    
    return {
        'age_range': age_str,
        'budget_range': budget_str,
        'top_interests': top_3
    }

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
    except Exception as e:
        print(f"Fout bij maken notificatie: {e}")

def create_automatic_groups():
    """Greedy Best-Match Algoritme: Maakt ÉÉN groep aan."""
    
    # 1. Haal alle users op die al in een groep zitten
    grouped_user_ids = [g.user_id for g in Group.query.all()]
    
    # 2. Haal alle actieve profielen op die nog NIET in een groep zitten
    available_profiles = TravelerProfile.query.filter(
        TravelerProfile.user_id.notin_(grouped_user_ids),
        TravelerProfile.is_active == True
    ).all()
    
    # Als er niemand beschikbaar is, stop direct
    if len(available_profiles) < 1:
        return

    # 3. Bepaal het volgende Match ID
    last_group = Group.query.order_by(Group.match_id.desc()).first()
    next_group_id = (last_group.match_id + 1) if last_group and last_group.match_id else 1
    
    GROUP_SIZE = 20
    current_group_id = next_group_id
    
    group_members = []
    
    # Helper om iemand uit de lijst te halen op basis van ID
    def pop_profile_by_id(uid):
        for i, p in enumerate(available_profiles):
            if p.user_id == uid:
                return available_profiles.pop(i)
        return None

    # --- START LOGICA VOOR 1 GROEP ---

    # Pak de eerste persoon als 'Seed' (het startpunt)
    seed_profile = available_profiles.pop(0)
    group_members.append(seed_profile)
    
    # Houd de gezamenlijke budget range bij van de HELE groep
    current_group_min = seed_profile.budget_min
    current_group_max = seed_profile.budget_max

    # Heeft de seed een buddy? Voeg die direct toe
    if seed_profile.linked_buddy_id:
        buddy = pop_profile_by_id(seed_profile.linked_buddy_id)
        if buddy:
            # Check of buddy past in budget (zou moeten als ze buddies zijn, maar voor zekerheid)
            new_min = max(current_group_min, buddy.budget_min)
            new_max = min(current_group_max, buddy.budget_max)
            
            # Eis: Minimaal 500 overlap (dus max - min >= 500)
            if (new_max - new_min) >= 500:
                group_members.append(buddy)
                current_group_min = new_min
                current_group_max = new_max
            else:
                # Buddy past niet in budget range -> Buddy wordt niet toegevoegd aan deze groep
                # (In praktijk zou je hier misschien de seed ook willen skippen, maar voor nu laten we seed staan)
                available_profiles.append(buddy) # Zet buddy terug

    # Vul de rest van DEZE groep aan tot 20 (of tot op is)
    while len(group_members) < GROUP_SIZE and len(available_profiles) > 0:
        candidates = []
        for candidate in available_profiles:
            # 1. Check period overlap with seed_profile (Harde eis voor groepsvorming)
            p1 = getattr(seed_profile, 'travel_period', '') or ''
            p2 = getattr(candidate, 'travel_period', '') or ''
            periods1 = set(p1.split(', '))
            periods2 = set(p2.split(', '))
            
            has_overlap = 'Flexibel' in periods1 or 'Flexibel' in periods2 or len(periods1.intersection(periods2)) > 0
            
            if not has_overlap:
                continue

            # 2. Check Budget Overlap met de HELE groep (Harde eis)
            # De nieuwe kandidaat moet passen binnen de huidige groeps-range
            # EN de overlap moet minstens 500 zijn.
            
            new_min = max(current_group_min, candidate.budget_min)
            new_max = min(current_group_max, candidate.budget_max)
            
            # Als new_max - new_min < 500, is de overlap te klein (of negatief)
            if (new_max - new_min) < 500:
                continue

            score = calculate_match_score(seed_profile, candidate)
            if score != -1: 
                # Sla ook de nieuwe range op, zodat we die kunnen updaten als we deze kandidaat kiezen
                candidates.append((score, candidate, new_min, new_max))
        
        # Sorteer op beste score
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        if not candidates:
            break # Geen matches meer gevonden die bij de groep passen
        
        best_score, best_match, new_min, new_max = candidates[0]
        
        # NIEUW: Drempelwaarde van 50%
        if best_score < 50:
            break
        
        # Voeg beste match toe en update groeps-range
        available_profiles.remove(best_match)
        group_members.append(best_match)
        current_group_min = new_min
        current_group_max = new_max
        
        # Heeft deze match een buddy? Voeg die ook toe (mits plek en budget past)
        if best_match.linked_buddy_id and len(group_members) < GROUP_SIZE:
            buddy = pop_profile_by_id(best_match.linked_buddy_id)
            if buddy:
                b_min = max(current_group_min, buddy.budget_min)
                b_max = min(current_group_max, buddy.budget_max)
                
                if (b_max - b_min) >= 500:
                    group_members.append(buddy)
                    current_group_min = b_min
                    current_group_max = b_max
                else:
                    available_profiles.append(buddy) # Buddy past niet, zet terug
    
    # --- OPSLAAN IN DATABASE ---
    for member in group_members:
        new_group_entry = Group(
            match_id=current_group_id,
            user_id=member.user_id,
            role='member',
            confirmed=False
        )
        db.session.add(new_group_entry)
        
        create_notification(member.user_id, f"Je bent toegevoegd aan Groep #{current_group_id}! Bekijk snel je nieuwe reisgenoten.")
            
    db.session.commit()

# -------------------------
# --- ROUTES DEFINITIES ---
# -------------------------

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
        return render_template('example_trips.html')
        
    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/intake')
    def intake():
        if 'user_id' not in session or session.get('role') == 'organizer':
            flash('Je moet ingelogd zijn als reiziger om de intake te doen.', 'warning')
            return redirect(url_for('login'))
        
        existing_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        
        if existing_profile:
            user = User.query.get(session['user_id'])
            return render_template('intake_overview.html', user=user, profile=existing_profile)
        
        return render_template('intake.html')
    
    @app.route('/edit-intake')
    def edit_intake():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        return render_template('intake.html', profile=profile)


    @app.route('/submit-intake', methods=['POST'])
    def submit_intake():
        if 'user_id' not in session or session.get('role') == 'organizer':
            flash('Je moet ingelogd zijn als reiziger.', 'danger')
            return redirect(url_for('login'))
        
        try:
            # Data ophalen (Originele logica)
            age = int(request.form.get('age'))
            budget_min = int(request.form.get('budget_min'))
            budget_max = int(request.form.get('budget_max'))
            periods = request.form.getlist('period')
            travel_period = ', '.join(periods)
            
            # 16 VIBE CHECK VRAGEN
            adventure_level = int(request.form.get('adventure_level'))
            beach_person = int(request.form.get('beach_person'))
            culture_interest = int(request.form.get('culture_interest'))
            party_animal = int(request.form.get('party_animal'))
            nature_lover = int(request.form.get('nature_lover'))
            luxury_comfort = int(request.form.get('luxury_comfort'))
            morning_person = int(request.form.get('morning_person'))
            planning_freak = int(request.form.get('planning_freak'))
            foodie_level = int(request.form.get('foodie_level'))
            sporty_spice = int(request.form.get('sporty_spice'))
            chaos_tolerance = int(request.form.get('chaos_tolerance'))
            city_trip = int(request.form.get('city_trip'))
            road_trip = int(request.form.get('road_trip'))
            backpacking = int(request.form.get('backpacking'))
            local_contact = int(request.form.get('local_contact'))
            digital_detox = int(request.form.get('digital_detox'))

            # Ongebruikte velden (defaults)
            social_battery = 3
            leader_role = 3
            talkative = 3
            sustainability = 3
            
            existing = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
            
            # --- BUDDY LOGICA ---
            buddy_email = request.form.get('buddy_email')
            linked_buddy_id = None
            
            if buddy_email and buddy_email.strip() != "":
                buddy_user = User.query.filter_by(email=buddy_email.strip()).first()
                
                if buddy_user:
                    linked_buddy_id = buddy_user.id
                    
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
            return redirect(url_for('intake'))
            
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
        
        my_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()
        if not my_profile:
            flash('Vul eerst je profiel in!', 'warning')
            return redirect(url_for('intake'))
        
        all_profiles = TravelerProfile.query.filter(TravelerProfile.user_id != session['user_id']).all()
        
        matches = []
        for profile in all_profiles:
            score = calculate_match_score(my_profile, profile)
            
            user = User.query.get(profile.user_id)
            
            matches.append({
                'user': user,
                'profile': profile,
                'score': score,
                'percentage': int(score)
            })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        good_matches = [m for m in matches if m['score'] >= 50]
        good_matches = good_matches[:10]
        
        return render_template('match.html', matches=good_matches, my_profile=my_profile)
    
    # --- MIJN GROEP ---
    @app.route('/my-group')
    def my_group():
        if 'user_id' not in session or session.get('role') == 'organizer':
            flash('Je moet ingelogd zijn als reiziger.', 'danger')
            return redirect(url_for('login'))
        
        my_profile = TravelerProfile.query.filter_by(user_id=session['user_id']).first()

        my_group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        
        if not my_group_entry:
            return render_template('my_group.html', group=None, my_profile=my_profile)
            
        group_members_entries = Group.query.filter_by(match_id=my_group_entry.match_id).all()
        
        members = []
        for entry in group_members_entries:
            user = User.query.get(entry.user_id)
            profile = TravelerProfile.query.filter_by(user_id=entry.user_id).first()
            members.append({'user': user, 'profile': profile})
            
        assigned_trip = Trip.query.filter_by(match_id=my_group_entry.match_id).first()
        
        spots_left = 0
        if assigned_trip:
            confirmed_count = Group.query.filter_by(match_id=my_group_entry.match_id, payment_status='paid').count()
            spots_left = max(0, assigned_trip.max_spots - confirmed_count)
        
        return render_template('my_group.html', 
                               group_id=my_group_entry.match_id, 
                               members=members, 
                               trip=assigned_trip,
                               my_entry=my_group_entry,
                               spots_left=spots_left,
                               my_profile=my_profile)


    @app.route('/pay-deposit', methods=['POST'])
    def pay_deposit():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        my_group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        
        if not my_group_entry:
            flash('Je zit niet in een groep.', 'danger')
            return redirect(url_for('my_group'))
            
        assigned_trip = Trip.query.filter_by(match_id=my_group_entry.match_id).first()
        if not assigned_trip:
            flash('Er is nog geen reis gekoppeld.', 'warning')
            return redirect(url_for('my_group'))
            
        confirmed_count = Group.query.filter_by(match_id=my_group_entry.match_id, payment_status='paid').count()
        
        if confirmed_count >= assigned_trip.max_spots and my_group_entry.payment_status != 'paid':
            flash('Helaas, de reis is volzet!', 'danger')
            return redirect(url_for('my_group'))
            
        my_group_entry.payment_status = 'paid'
        my_group_entry.confirmed = True
        
        create_notification(session['user_id'], f"Betaling ontvangen! Je plek voor {assigned_trip.destination} is definitief.")
        
        db.session.commit()
        flash('Betaling geslaagd! Je gaat mee op reis! 🌍✈️', 'success')
            
        return redirect(url_for('my_group'))

    @app.route('/leave-group', methods=['POST'])
    def leave_group():
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        my_group_entry = Group.query.filter_by(user_id=session['user_id']).first()
        
        if my_group_entry:
            db.session.delete(my_group_entry)
            
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
            
        status = request.form.get('status')
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

    # -------------------------------------
    # --- ORGANIZER ROUTES (NIEUW/HERZIEN) ---
    # -------------------------------------

    @app.route('/organizer/dashboard')
    def organizer_dashboard():
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('home'))
        
        total_users = User.query.count()
        total_trips = Trip.query.count()
        total_groups = db.session.query(Group.match_id).distinct().count() 
        
        users_in_group_ids = db.session.query(Group.user_id).distinct().all()
        users_in_group_ids = [u[0] for u in users_in_group_ids]
        unassigned_users = User.query.filter(
            User.id.notin_(users_in_group_ids)
        ).count()
        
        return render_template('organizer_dashboard.html', 
                               total_users=total_users, 
                               total_trips=total_trips, 
                               total_groups=total_groups,
                               unassigned_users=unassigned_users)
    
    @app.route('/organizer/create-trip', methods=['GET', 'POST'])
    def organizer_create_trip():
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            try:
                dest = request.form.get('destination')
                price = request.form.get('price')
                s_date = request.form.get('start_date')
                e_date = request.form.get('end_date')
                desc = request.form.get('description')
                acts = request.form.get('activities')
                max_spots = int(request.form.get('max_spots', 20))
                deposit_amount = float(request.form.get('deposit_amount', 0.0))
                
                new_trip = Trip(
                    travel_org_id=session['user_id'],
                    destination=dest,
                    price=float(price),
                    # Opgelost: Gebruik datetime.strptime om de datum om te zetten naar een Python date object
                    start_date=datetime.strptime(s_date, '%Y-%m-%d').date(),
                    end_date=datetime.strptime(e_date, '%Y-%m-%d').date(),
                    description=desc,
                    activities=acts,
                    match_id=None,
                    max_spots=max_spots,
                    deposit_amount=deposit_amount
                )
                
                db.session.add(new_trip)
                db.session.commit()
                
                flash(f'Succes! De reis naar {dest} is opgeslagen.', 'success')
                return redirect(url_for('organizer_trips'))

            except Exception as e:
                db.session.rollback()
                print(f"DATABASE FOUT bij aanmaken reis: {e}") 
                flash('Er ging iets mis bij het aanmaken van de reis.', 'danger')
        
        return render_template('organizer_create_trip.html')

    # --- ORGANIZER: ALL TRIPS (Alle Reizen) ---
    @app.route('/organizer/all-trips')
    def organizer_trips():
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('home'))   
        all_trips = Trip.query.all()
    
        trips_with_org = []
        organizers_cache = {}
        for trip in all_trips:
            org_name = organizers_cache.get(trip.travel_org_id)
            if not org_name:
                organiser = Organiser.query.get(trip.travel_org_id)
                org_name = organiser.name if organiser else 'Onbekend'
                organizers_cache[trip.travel_org_id] = org_name
        
        # NIEUWE CONTROLE: Zet None-waardes om naar lege strings
            trip.description = trip.description or ""
            trip.activities = trip.activities or ""
        
            trips_with_org.append({
                'trip': trip,
                'organizer_name': org_name
         })
        
        return render_template('organizer_trips.html', trips=trips_with_org)
        
    @app.route('/organizer/all-users')
    def organizer_users():
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('home'))

        all_users = User.query.all()
        
        users_with_info = []
        for user in all_users:
            profile = TravelerProfile.query.filter_by(user_id=user.id).first()
            group_entry = Group.query.filter_by(user_id=user.id).first()
            
            status = "Nog Geen Profiel"
            if profile:
                status = "Actief (Zoekt)"
                if not profile.is_active:
                    status = "Inactief (Pauze)"
            if group_entry:
                status = f"In Groep #{group_entry.match_id}"
                if group_entry.payment_status == 'paid':
                    status = f"✅ Bevestigd in Groep #{group_entry.match_id}"
                    
            users_with_info.append({
                'user': user,
                'profile': profile,
                'status': status
            })
            
        return render_template('organizer_users.html', users=users_with_info)

    @app.route('/organizer/groups', methods=['GET', 'POST'])
    def organizer_groups():
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            # 1. Groepen Genereren
            if 'generate_groups' in request.form:
                create_automatic_groups() 
                flash('Groepen zijn automatisch gegenereerd!', 'success')
                return redirect(url_for('organizer_groups'))
            
            # 2. Reis Koppelen
            if 'assign_trip' in request.form:
                group_id = request.form.get('group_id')
                trip_id = request.form.get('trip_id')
                
                if group_id and trip_id:
                    trip = Trip.query.get(trip_id)
                    
                    # Check of de groep al een reis heeft
                    existing_trip = Trip.query.filter_by(match_id=group_id).first()
                    if existing_trip:
                         flash(f'Deze groep heeft al een reis ({existing_trip.destination})!', 'danger')
                         return redirect(url_for('organizer_groups'))

                    if trip.match_id and str(trip.match_id) != group_id:
                        flash(f'Reis is al gekoppeld aan groep #{trip.match_id}!', 'warning')
                        return redirect(url_for('organizer_groups'))
                        
                    trip.match_id = int(group_id) 
                    
                    members = Group.query.filter_by(match_id=group_id).all()
                    for m in members:
                        create_notification(m.user_id, f"Er is een reis gekoppeld aan jouw groep! Jullie gaan naar {trip.destination}. ✈️") 
                    
                    db.session.commit()
                    flash(f'Reis naar {trip.destination} gekoppeld aan Groep {group_id}!', 'success')
                return redirect(url_for('organizer_groups'))
            
            # 3. Lid Toevoegen
            if 'add_member' in request.form:
                user_id = request.form.get('user_id')
                group_id = request.form.get('group_id')
                
                if user_id and group_id:
                    user_id = int(user_id)
                    group_id = int(group_id)
                    
                    if Group.query.filter_by(user_id=user_id).first():
                        flash('Deze reiziger zit al in een groep!', 'warning')
                        return redirect(url_for('organizer_groups'))
                        
                    new_entry = Group(
                        match_id=group_id,
                        user_id=user_id,
                        role='member',
                        confirmed=False
                    )
                    db.session.add(new_entry)
                    create_notification(user_id, f"De organisator heeft je handmatig toegevoegd aan Groep #{group_id}.")
                    db.session.commit()
                    flash('Reiziger handmatig toegevoegd aan de groep.', 'success')
                return redirect(url_for('organizer_groups'))

            # 4. Groep Verwijderen (NIEUW)
            if 'delete_group' in request.form:
                group_id = request.form.get('group_id')
                if group_id:
                    # A. Koppel reis los (zodat reis weer beschikbaar wordt)
                    linked_trip = Trip.query.filter_by(match_id=group_id).first()
                    if linked_trip:
                        linked_trip.match_id = None
                    
                    # B. Zet profielen van leden weer op 'active'
                    members = Group.query.filter_by(match_id=group_id).all()
                    for m in members:
                        profile = TravelerProfile.query.filter_by(user_id=m.user_id).first()
                        if profile:
                            profile.is_active = True
                        create_notification(m.user_id, "Helaas, de groep waarin je zat is opgeheven door de organisator.")
                    
                    # C. Verwijder groep entries
                    Group.query.filter_by(match_id=group_id).delete()
                    
                    db.session.commit()
                    flash(f'Groep #{group_id} is verwijderd.', 'info')
                return redirect(url_for('organizer_groups'))

        # GET Request: Data ophalen
        all_group_members = Group.query.all()
        groups = {}
        group_vibes = {}
        group_stats = {}
        
        users_in_group_ids = db.session.query(Group.user_id).distinct().all()
        users_in_group_ids = [u[0] for u in users_in_group_ids]

        for member in all_group_members:
            if member.match_id not in groups:
                groups[member.match_id] = []
            
            user = User.query.get(member.user_id)
            user.group_status = member.payment_status
            user.group_confirmed = member.confirmed
            groups[member.match_id].append(user)
            
        # NIEUW: Maak een map van match_id -> Trip object
        # Zodat we in de HTML weten welke groep welke reis heeft
        assigned_trips_query = Trip.query.filter(Trip.match_id.isnot(None)).all()
        assigned_trips = {t.match_id: t for t in assigned_trips_query}

        for match_id in groups.keys():
            group_vibes[match_id] = calculate_group_vibe(match_id)
            group_stats[match_id] = get_group_stats(match_id)

        # Dropdown voor ALLE ONGEKOPPELDE reizen (niet alleen van mij)
        trips_for_dropdown = Trip.query.filter(
            Trip.match_id.is_(None)
        ).all()
        
        unassigned_users = User.query.outerjoin(
            TravelerProfile,
            TravelerProfile.user_id == User.id 
        ).filter(
            User.id.notin_(users_in_group_ids)
        ).all()
            
        return render_template('organizer_groups.html', 
                               groups=groups, 
                               group_vibes=group_vibes,
                               group_stats=group_stats,
                               trips=trips_for_dropdown,
                               unassigned_users=unassigned_users,
                               assigned_trips=assigned_trips) # Geef assigned_trips mee!
                               
    @app.route('/organizer/remove_member/<int:user_id>', methods=['POST'])
    def remove_group_member(user_id):
        if 'user_id' not in session or session.get('role') != 'organizer':
            return redirect(url_for('home'))
            
        group_entry = Group.query.filter_by(user_id=user_id).first()
        if group_entry:
            create_notification(user_id, f"Je bent uit Groep #{group_entry.match_id} verwijderd door een organisator.")
            db.session.delete(group_entry)
            
            profile = TravelerProfile.query.filter_by(user_id=user_id).first()
            if profile:
                profile.is_active = True 
            
            db.session.commit()
            flash('Reiziger verwijderd uit de groep en op zoek gezet naar een nieuwe match.', 'success')
            
        return redirect(url_for('organizer_groups'))

    # --- REGISTRATIE / LOGIN / LOGOUT ---
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            role = request.form.get('role')

            if role == 'traveller':
                if User.query.filter_by(email=email).first():
                    flash('Dit e-mailadres is al geregistreerd als reiziger.', 'danger')
                    return render_template('register.html')
                    
                new_user = User(name=name, email=email, created_at=datetime.now())
                db.session.add(new_user)
                db.session.commit()
                flash('Account aangemaakt! Je kunt nu inloggen en je intake invullen.', 'success')
                return redirect(url_for('login'))
            
            elif role == 'organizer':
                if Organiser.query.filter_by(email=email).first():
                    flash('Dit e-mailadres is al geregistreerd als organisator.', 'danger')
                    return render_template('register.html')
                    
                new_organiser = Organiser(name=name, email=email, created_at=datetime.now())
                db.session.add(new_organiser)
                db.session.commit()
                flash('Organisator account aangemaakt! Je kunt nu inloggen.', 'success')
                return redirect(url_for('login'))
            
            else:
                flash('Ongeldige rol geselecteerd.', 'danger')
        
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            
            user = User.query.filter_by(email=email).first()
            if user:
                session['user_id'] = user.id
                session['name'] = user.name
                session['role'] = 'traveller'
                flash(f'Welkom terug, {user.name}!', 'success')
                return redirect(url_for('home'))
                
            organiser = Organiser.query.filter_by(email=email).first()
            if organiser:
                session['user_id'] = organiser.id
                session['name'] = organiser.name
                session['role'] = 'organizer'
                flash(f'Welkom, organisator {organiser.name}!', 'success')
                return redirect(url_for('organizer_dashboard'))

            flash('Ongeldig e-mailadres.', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Uitgelogd.', 'info')
        return redirect(url_for('login'))