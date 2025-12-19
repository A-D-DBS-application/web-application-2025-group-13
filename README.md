[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DxqGQVx4)
Web Application 2025 – Group 13

Overzicht

Deze repository bevat een webapplicatie ontwikkeld in het kader van het vak Web Application 2025. De applicatie is een platform waar gebruikers zich kunnen registreren als reiziger of organisator en waar reizen, groepen en profielen beheerd worden.

De focus van dit project ligt op het prototype en de kernfunctionaliteiten. Sommige keuzes (zoals vrije registratie als organisator) zijn bewust eenvoudig gehouden en kunnen in de toekomst verder verfijnd worden.

1. Vereisten (installaties)

Om de applicatie lokaal te kunnen runnen, heb je het volgende nodig:
	•	Python (bij voorkeur versie 3.10 of hoger)
	•	pip (Python package manager)

Alle nodige Python libraries staan opgelijst in het bestand:

requirements.txt

👉 Het is mogelijk dat sommige of alle packages reeds geïnstalleerd zijn. In dat geval kan deze stap overgeslagen worden.

⸻

2. Installatie

Installeer alle vereiste packages via het volgende commando in de terminal:

pip install -r requirements.txt

Wacht tot alle dependencies correct geïnstalleerd zijn.

⸻

3. Applicatie lokaal starten

Volg deze stappen om de website lokaal te runnen:
	1.	Open het project in je code-editor (bijvoorbeeld VS Code)
	2.	Ga naar het bestand:

run.py


	3.	Klik bovenaan op het Run-icoon (de schuine driehoek ▶️)
	4.	In de terminal zal de applicatie starten
	5.	Je ziet een lokale link verschijnen die eindigt op:

:5000


	6.	Ctrl + klik op deze link

➡️ De website opent nu automatisch in je browser.

⸻

4. Gebruik van de applicatie

Bij het starten van de website krijgt de gebruiker de keuze om zich te registreren als:
	•	Reiziger
	•	Organisator

⚠️ Opmerking:
Het is momenteel mogelijk dat elke gebruiker zich als organisator registreert. Dit is niet de bedoeling in een productieomgeving, maar werd voor dit prototype bewust zo gelaten omdat dit voldeed aan de doelstellingen van het project.

⸻

5. Online versies (Render)

!!!!LET OP GEBRUIK DE LAATSTE RENDER LINK OM DE FINALE VERSIE TE ZIEN!!!!
DIT IS DE LAATSTE FINALE VERSIE: https://web-application-2025-group-13-8.onrender.com/ 

De applicatie is ook online beschikbaar via Render:
	•	Eerste versie:
https://web-application-2025-group-13-2.onrender.com
	•	Tweede versie:
https://web-application-2025-group-13-3.onrender.com
	•	Finale versie:
https://web-application-2025-group-13-8.onrender.com/

⸻

6. Prototype (Lovable)

Het initiële app-prototype werd uitgewerkt via Lovable:

https://lovable.dev/projects/51ca8f5e-67dd-4f38-b5bf-bab8bfd5ed94

⸻

7. Feedback opnames

Tijdens het ontwikkelproces werden feedbackmomenten opgenomen:
	•	https://www.kapwing.com/w/oqHk9SxT_x
	•	https://youtu.be/u1UgIJUXfa4


8. Database structuur (DDL)

Onderstaande tabellen geven een overzicht van de gebruikte database-structuur.

User

Table user {
  id integer [pk, increment]
  created_at datetime [default: `now()`]
  name varchar(100)
  email varchar(150) [unique, not null]
}

Notification

Table notification {
  id integer [pk, increment]
  user_id integer [not null, ref: > user.id]
  message varchar(255) [not null]
  is_read boolean [default: false]
  created_at datetime [default: `now()`]
}

Organiser

Table organiser {
  id integer [pk, increment]
  name varchar(100)
  email varchar(150)
  created_at datetime
}

Trip

Table trip {
  id integer [pk, increment]
  travel_org_id integer [not null, ref: > organiser.id]
  match_id integer
  destination varchar(100) [not null]
  start_date date
  end_date date
  price float
  description text
  activities text
  max_spots integer
  deposit_amount float
}

Group

Table group {
  id integer [pk, increment]
  trip_id integer [unique, ref: - trip.id]
  name varchar(100)
  match_id integer
  created_at datetime [default: `now()`]
}

Traveler Profile

Table traveler_profile {
  id integer [pk, increment]
  user_id integer [not null, unique, ref: - user.id]
  group_id integer [ref: > group.id]
  is_active boolean [default: true]
  created_at datetime

  age integer
  budget_min integer
  budget_max integer
  travel_period varchar(100)

  linked_buddy_id integer [ref: - user.id]

  adventure_level integer [not null]
  beach_person integer [not null]
  culture_interest integer [not null]
  party_animal integer [not null]
  nature_lover integer [not null]
  luxury_comfort integer [not null]
  morning_person integer [not null]
  planning_freak integer [not null]
  foodie_level integer [not null]
  sporty_spice integer [not null]
  chaos_tolerance integer [not null]
  city_trip integer [not null]
  road_trip integer [not null]
  backpacking integer [not null]
  local_contact integer [not null]
  digital_detox integer [not null]

  social_battery integer [not null, default: 3]
  leader_role integer [not null, default: 3]
  talkative integer [not null, default: 3]
  sustainability integer [not null, default: 3]
}

Demo is te vinden in de Powerpoint.

