# Rent a boat

Studentski projekt iz kolegija Programiranje za web (SIT UNIZD).

Charter tvrtka iznajmljuje brodove. Klijent rezervira brod za razdoblje i vidi
samo svoje rezervacije, a zaposlenik upravlja flotom i potvrđuje rezervacije.

Repozitorij ima dva dijela: `api/` je backend (FastAPI, SQLAlchemy, PostgreSQL),
a `web/` frontend koji dolazi u drugom dijelu projekta.

## Pokretanje

Potrebno: Docker, Python 3.11 ili noviji i [uv](https://docs.astral.sh/uv/)
(može i obični `pip`).

Iz korijena repozitorija:

```bash
cp .env.example .env            # PowerShell: Copy-Item .env.example .env
docker compose up -d db         # PostgreSQL 16 na vratima 5433
```

Zatim iz mape `api/`:

```bash
cd api
uv venv
source .venv/bin/activate       # PowerShell: .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
alembic upgrade head            # stvara tablice
python -m app.seed              # početni podatci, smije se pokrenuti više puta
uvicorn app.main:app --reload
```

API je na `http://127.0.0.1:8000`, a dokumentacija na `http://127.0.0.1:8000/docs`.

### Testovi

Iz mape `api/`, dok baza radi:

```bash
pytest
ruff check .
```

Testovi rade na zasebnoj bazi `boat_rental_test`, koja se sama stvori pri prvom
pokretanju, pa ne diraju razvojne podatke.

### Demo računi (iz seeda)

| Uloga | Korisničko ime | Lozinka |
|-------|----------------|---------|
| admin | `admin@rentaboat.hr` | `admin123` |
| customer | `ana@rentaboat.hr` | `ana12345` |
| customer | `ivan@rentaboat.hr` | `ivan1234` |

## Model podataka

| Tablica | Što čuva | Veza |
|---------|----------|------|
| `users` | račun, bcrypt hash lozinke, uloga | 1:N prema `reservations` |
| `marinas` | marina u kojoj brod stoji | 1:N prema `boats` |
| `boats` | naziv, vrsta, kapacitet, cijena po danu | 1:N prema `reservations` |
| `reservations` | korisnik, brod, razdoblje, broj osoba, cijena, status | pripada korisniku i brodu |

Sve promjene sheme idu kroz Alembic migracije u `api/migrations/`.

## Uloge

- `admin`: upravlja marinama i brodovima, vidi sve rezervacije, potvrđuje ih i otkazuje
- `customer`: registrira se, pregledava brodove, stvara i otkazuje vlastite rezervacije

## Poslovna pravila

- Isti brod ne može imati dvije rezervacije koje se preklapaju. Pravilo provodi
  baza (`EXCLUDE` ograničenje nad rasponom datuma); otkazane rezervacije ne
  zauzimaju termin.
- Klijent smije otkazati rezervaciju najkasnije 48 sati prije početka (početak je
  ponoć UTC na dan `start_date`). Admin smije otkazati uvijek.
- Potvrditi se može samo rezervacija `pending`; otkazana se ne može ni potvrditi
  ni ponovno otkazati.
- Broj osoba ne smije prijeći kapacitet broda, a brod koji nije u ponudi ne može
  se rezervirati.
- Cijena se računa pri stvaranju (broj dana × cijena po danu) i zapisuje u
  rezervaciju, pa je kasnija promjena cijene broda ne mijenja.

## API

Popisi primaju `limit` (1–100, zadano 20) i `offset`.

| Metoda | Putanja | Tko smije |
|--------|---------|-----------|
| POST | `/auth/register` | javno, stvara račun `customer` |
| POST | `/auth/login` | javno |
| POST | `/auth/refresh` | refresh token |
| GET | `/auth/me` | prijavljen |
| GET | `/marinas` | javno |
| POST | `/marinas` | admin |
| GET | `/marinas/{id}` | javno |
| PATCH | `/marinas/{id}` | admin |
| GET | `/boats` | javno, filtri `type` i `marina_id` |
| POST | `/boats` | admin |
| GET | `/boats/{id}` | javno |
| GET | `/reservations` | admin: sve, customer: samo svoje; filtar `status` |
| POST | `/reservations` | customer |
| GET | `/reservations/{id}` | vlasnik ili admin |
| POST | `/reservations/{id}/confirm` | admin |
| POST | `/reservations/{id}/cancel` | vlasnik do 48 h prije početka, admin uvijek |

## Pogreške

Svaki neuspjeh vraća tijelo istoga oblika: `{"code": "...", "message": "..."}`.

| `code` | HTTP | Kada |
|--------|------|------|
| `validation_error` | 422 | tijelo ili parametri ne odgovaraju shemi |
| `invalid_credentials` | 401 | prijava ili token ne vrijede |
| `token_expired` | 401 | access token je istekao |
| `forbidden` | 403 | uloga ili vlasništvo ne dopuštaju radnju |
| `not_found` | 404 | zapis ne postoji |
| `duplicate` | 409 | naziv ili korisničko ime već postoji |
| `boat_unavailable` | 409 | brod je u tom razdoblju već rezerviran |
| `capacity_exceeded` | 400 | više osoba nego što brod prima |
| `boat_inactive` | 400 | brod nije u ponudi |
| `invalid_status` | 400 | radnja nije moguća u ovom statusu |
| `cancellation_deadline_passed` | 400 | prošao je rok za otkaz |
