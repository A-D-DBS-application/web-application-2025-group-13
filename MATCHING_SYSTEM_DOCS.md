# 🎯 TrailTribe Matching Systeem - Implementatie Samenvatting

## Wat is er geïmplementeerd?

### 1. **Nieuwe Database Tabel: `TravelerProfile`** 
Een nieuw model toegevoegd in `app/models.py` dat de uitgebreide vragenlijst data opslaat:

**Velden:**
- `age` - Leeftijd van de reiziger
- `budget_min` & `budget_max` - Budget range in euros
- `travel_period` - Reisperiodes (Winter, Lente, Zomer, Herfst, Flexibel)
- **Interesse scores (1-5 schaal):**
  - `adventure_level` - Hoe avontuurlijk (1=rustig, 5=zeer avontuurlijk)
  - `party_level` - Feestgehalte (1=rustig, 5=feestbeest)
  - `culture_level` - Culturele interesse (1=weinig, 5=heel cultureel)
  - `food_level` - Foodie niveau (1=normaal, 5=echte foodie)
  - `nature_level` - Natuur interesse (1=stad, 5=natuur lover)

### 2. **Vereenvoudigde Intake Vragenlijst** (`app/templates/intake.html`)

**Veranderingen:**
- ✅ **Kalender verwijderd** - Vervangen door seizoenen/periodes
- ✅ **Simpele rating sliders** - Alle interesses op schaal 1-5
- ✅ **Budget min/max** - In plaats van vaste categorieën
- ✅ **Moderne UI** - Mooie sliders met real-time waardes

**8 Vragen:**
1. Leeftijd (nummer)
2. Budget range (min & max in euros)
3. Reisperiode (Winter/Lente/Zomer/Herfst/Flexibel - meerdere keuzes)
4. Avontuurlijkheid (1-5 slider)
5. Feesten (1-5 slider)
6. Cultuur (1-5 slider)
7. Eten (1-5 slider)
8. Natuur (1-5 slider)

### 3. **Intake Submit Route** (`app/routes.py`)

**Route:** `/submit-intake` (POST)

**Functionaliteit:**
- Haalt alle form data op
- Combineert meerdere reisperiodes in één string
- Check of profiel al bestaat → Update of Create
- Slaat op in Supabase via SQLAlchemy (exact zoals bij Trip)
- Redirect naar match pagina na succes

### 4. **Matching Algoritme** 

**Functie:** `calculate_match_score(profile1, profile2)`

**Hoe werkt het?**
Het algoritme geeft een **match percentage (0-100%)** gebaseerd op:

| Factor | Max Punten | Berekening |
|--------|-----------|------------|
| **Leeftijd** | 10 | Verschil ≤3 jaar = 10pt, ≤5 jaar = 7pt, ≤8 jaar = 4pt |
| **Budget overlap** | 15 | Meer overlap = betere score |
| **Reisperiode** | 15 | Overlappende periodes of "Flexibel" = punten |
| **Avontuur niveau** | 10 | Verschil 0 = 10pt, 1 = 7pt, 2 = 4pt |
| **Party niveau** | 10 | Verschil 0 = 10pt, 1 = 7pt, 2 = 4pt |
| **Cultuur niveau** | 10 | Verschil 0 = 10pt, 1 = 7pt, 2 = 4pt |
| **Food niveau** | 10 | Verschil 0 = 10pt, 1 = 7pt, 2 = 4pt |
| **Natuur niveau** | 10 | Verschil 0 = 10pt, 1 = 7pt, 2 = 4pt |
| **TOTAAL** | **90** | Omgezet naar percentage |

**Voorbeeld:**
- Jij: Avontuur=5, Party=3, Cultuur=4
- Match: Avontuur=5, Party=2, Cultuur=4
- Score: Perfect match op avontuur (10pt) + 1 verschil party (7pt) + perfect cultuur (10pt) = hoge match!

### 5. **Match Weergave Route** (`/match`)

**Functionaliteit:**
- Check of gebruiker een profiel heeft
- Haal alle andere profielen op (niet van jezelf)
- Bereken match score voor elke persoon
- Sorteer op score (hoogste eerst)
- Toon alleen matches ≥50%

### 6. **Match Display Template** (`app/templates/match.html`)

**Features:**
- ✅ Jouw profiel overzicht (kaart bovenaan)
- ✅ Match cards met percentage score
- ✅ Kleurcode: Groen (70%+), Oranje (50-69%)
- ✅ Gedetailleerde vergelijking per interesse
- ✅ Budget & reisperiode weergave
- ✅ Actie knoppen (Contact/Profiel bekijken - voor later)

## Database Schema (Supabase)

De nieuwe tabel wordt automatisch aangemaakt via SQLAlchemy:

```sql
CREATE TABLE traveler_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) UNIQUE,
    created_at TIMESTAMP,
    age INTEGER NOT NULL,
    budget_min INTEGER NOT NULL,
    budget_max INTEGER NOT NULL,
    travel_period VARCHAR(200),
    adventure_level INTEGER NOT NULL,
    party_level INTEGER NOT NULL,
    culture_level INTEGER NOT NULL,
    food_level INTEGER NOT NULL,
    nature_level INTEGER NOT NULL
);
```

## Hoe te gebruiken?

### Voor Reizigers:
1. **Registreer/Login** als reiziger
2. **Ga naar Intake** (navigatie of `/intake`)
3. **Vul vragenlijst in** (8 vragen met sliders)
4. **Klik "Profiel Opslaan"**
5. **Zie je matches** - Automatisch doorgestuurd naar match pagina
6. **Bekijk compatibiliteit** - Zie wie het beste bij je past!

### Database Connectie:
De code gebruikt **exact dezelfde Supabase connectie** als je bestaande code:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.xrmsmxtxmguqwgopzhwi:Team2025!?,,@aws-1-eu-central-1.pooler.supabase.com:6543/postgres'
```

## Voordelen van dit Simpele Systeem

✅ **Makkelijk te begrijpen** - Gewoon punten optellen
✅ **Makkelijk uit te breiden** - Voeg gewoon nieuwe velden toe in `calculate_match_score()`
✅ **Transparant** - Je kunt precies zien waarom twee mensen matchen
✅ **Snel** - Geen complexe AI, gewoon simpele wiskunde
✅ **Schaalbaar** - Werkt met 10 of 1000 gebruikers

## Mogelijke Uitbreidingen (Later)

1. **Gewichten aanpassen** - Maak bepaalde factoren belangrijker
2. **Filter opties** - Filter op leeftijd/budget voor je matcht
3. **Match verzoeken** - Stuur een match verzoek naar iemand
4. **Chat functie** - Praat met je matches
5. **Trip koppeling** - Match mensen met specifieke trips van organisatoren
6. **Groepen vormen** - Automatisch groepen van 4-6 mensen maken
7. **Machine Learning** - Later vervangen door slimmer algoritme als je data hebt

## Testen

1. **Start de app:**
   ```bash
   python app.py
   ```

2. **Maak 2-3 test accounts** als reiziger

3. **Vul voor elk verschillende profielen in**

4. **Check de match pagina** - Je zou matches moeten zien!

## Troubleshooting

**Probleem:** Tabel bestaat niet
- **Oplossing:** `db.create_all()` wordt automatisch aangeroepen in `__init__.py`

**Probleem:** Geen matches
- **Oplossing:** Zorg dat je minstens 2 profielen hebt ingevuld

**Probleem:** Error bij opslaan
- **Oplossing:** Check de terminal voor de exacte foutmelding (print statements zijn toegevoegd)

## Code Overzicht

**Nieuwe/Gewijzigde Bestanden:**
- ✅ `app/models.py` - TravelerProfile model toegevoegd
- ✅ `app/routes.py` - submit_intake, match route + matching algoritme
- ✅ `app/templates/intake.html` - Volledig nieuwe vragenlijst
- ✅ `app/templates/match.html` - Volledig nieuwe match weergave

**Ongewijzigd:**
- `app/config.py` - Database connectie blijft hetzelfde
- `app/__init__.py` - Database setup blijft hetzelfde
- Andere templates en routes - Blijven werken zoals voorheen

---

**Gemaakt op:** 14 November 2025
**Versie:** 1.0 - Simpel Matching Systeem
