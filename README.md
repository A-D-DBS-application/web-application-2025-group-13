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


Table user {
  id integer [pk, increment]
  created_at datetime [default: `now()`]
  name varchar(100)
  email varchar(150) [unique, not null]
}

Table notification {
  id integer [pk, increment]
  user_id integer [not null, ref: > user.id] 
  message varchar(255) [not null]
  is_read boolean [default: false]
  created_at datetime [default: `now()`]
}


Table organiser {
  id integer [pk, increment]
  name varchar(100)
  email varchar(150)
  created_at datetime
}

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


Table group {
  id integer [pk, increment]

  trip_id integer [unique, ref: - trip.id] 
  name varchar(100)
  match_id integer 
  created_at datetime [default: `now()`]
}

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