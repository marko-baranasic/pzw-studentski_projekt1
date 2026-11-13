# Rent a boat

Studentski projekt iz kolegija Programiranje za web (SIT UNIZD).

Charter tvrtka iznajmljuje brodove. Klijent rezervira brod za razdoblje i vidi
samo svoje rezervacije, a zaposlenik upravlja flotom i potvrđuje rezervacije.

## Uloge

- `admin`: upravlja marinama i brodovima, vidi sve rezervacije, potvrđuje ih i otkazuje
- `customer`: registrira se, pregledava brodove, stvara i otkazuje vlastite rezervacije

## Poslovna pravila

- Isti brod ne može imati dvije rezervacije koje se preklapaju.
- Klijent smije otkazati rezervaciju najkasnije 48 sati prije početka.
- Rezervacija prolazi statuse `pending`, `confirmed` i `cancelled`.
- Broj osoba ne smije prijeći kapacitet broda.
- Brod s rezervacijama ne može se obrisati.

## API

Svi popisi primaju `limit` i `offset`.

| Metoda | Putanja | Tko smije |
|--------|---------|-----------|
| POST | `/auth/register` | javno, stvara račun `customer` |
| POST | `/auth/login` | javno |
| POST | `/auth/refresh` | refresh token |
| GET | `/auth/me` | prijavljen |
| GET | `/marinas/` | prijavljen |
| POST | `/marinas/` | admin |
| GET | `/marinas/{id}` | prijavljen |
| PATCH | `/marinas/{id}` | admin |
| GET | `/boats/` | prijavljen, filtri `type` i `marina_id` |
| POST | `/boats/` | admin |
| GET | `/boats/{id}` | prijavljen |
| PATCH | `/boats/{id}` | admin |
| DELETE | `/boats/{id}` | admin, samo ako nema rezervacija |
| GET | `/reservations/` | admin: sve, customer: samo svoje |
| POST | `/reservations/` | customer |
| GET | `/reservations/{id}` | vlasnik ili admin |
| PATCH | `/reservations/{id}` | vlasnik, samo dok je `pending` |
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
| `has_reservations` | 409 | brod s rezervacijama ne može se obrisati |
| `capacity_exceeded` | 400 | više osoba nego što brod prima |
| `boat_inactive` | 400 | brod nije u ponudi |
| `invalid_status` | 400 | radnja nije moguća u ovom statusu |
| `cancellation_deadline_passed` | 400 | prošao je rok za otkaz |