[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DxqGQVx4)


LOVABLE APP PROTOTYPE:
https://lovable.dev/projects/51ca8f5e-67dd-4f38-b5bf-bab8bfd5ed94

render link app: https://web-application-2025-group-13-2.onrender.com
https://web-application-2025-group-13-3.onrender.com (2e)
https://web-application-2025-group-13-8.onrender.com/ (finale versie)


feedback opnames: 

https://www.kapwing.com/w/oqHk9SxT_x
https://youtu.be/u1UgIJUXfa4

DDL: 

Table "user" {
    id integer [pk, increment]
    created_at datetime
    name varchar(100)
    email varchar(120) [not null, unique]
}

Table "Organiser" {
    id integer [pk, increment]
    created_at datetime
    name varchar(100)
    email varchar(120) [not null, unique]
}

Table trip {
    id integer [pk, increment]
    match_id integer
    travel_org_id integer [not null, ref: > "Organiser".id]
    destination varchar(100) [not null]
    start_date date [not null]
    end_date date [not null]
    price float [not null]
    description text
    activities text
    max_spots integer [default: 20]
    deposit_amount float [default: 0.0]
}

Table traveler_profile {
    id integer [pk, increment]
    user_id integer [not null, unique, ref: <> "user".id]
    created_at datetime
    age integer [not null]
    budget_min integer [not null]
    budget_max integer [not null]
    travel_period varchar(200)
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
    linked_buddy_id integer [ref: > "user".id]
    is_active boolean [default: true]
    group_id integer [ref: > "group".id] // NIEUW: Elke profiel hoort bij 1 groep
}

Table "group" {
    id integer [pk, increment]
    match_id integer
}

Table notification {
    id integer [pk, increment]
    user_id integer [not null, ref: > "user".id]
    message varchar(255) [not null]
    is_read boolean [default: false]
    created_at datetime [default: 'NOW()'] // Gecorrigeerde syntax
