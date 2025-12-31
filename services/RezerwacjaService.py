# services/RezerwacjaService.py
from datetime import date

from repo.OwnerRepo import OwnerRepo
from repo.AnimalRepo import AnimalRepo
from repo.ReservationRepo import ReservationRepo
from repo.BookingItemRepo import BookingItemRepo
from repo.BoxesRepo import BoksRepo
from repo.StaysRepo import StaysRepo
from repo.SettlementRepo import SettlementRepo
from repo.SettlementItemRepo import SettlementItemRepo


class ReservationService:
    def __init__(self):
        self.owner_repo = OwnerRepo()
        self.animal_repo = AnimalRepo()
        self.reservation_repo = ReservationRepo()
        self.booking_item_repo = BookingItemRepo()
        self.boks_repo = BoksRepo()
        self.stay_repo = StaysRepo()
        self.settlement_repo = SettlementRepo()
        self.settlement_item_repo = SettlementItemRepo()

    # =========================================================
    # UC1
    # =========================================================

    def _validate_input(self, owner_data: dict, animal_data: dict, booking_data: dict) -> None:
        if not owner_data.get("first_name") or not owner_data.get("last_name"):
            raise ValueError("Owner: first_name i last_name są wymagane.")
        if not owner_data.get("email") and not owner_data.get("phone"):
            raise ValueError("Owner: podaj email lub phone (do identyfikacji w bazie).")

        if not animal_data.get("name") or not animal_data.get("species"):
            raise ValueError("Animal: name i species są wymagane.")

        if not booking_data.get("box_id"):
            raise ValueError("Booking: box_id jest wymagane.")
        if not booking_data.get("date_from") or not booking_data.get("date_to"):
            raise ValueError("Booking: date_from i date_to są wymagane.")

        df = date.fromisoformat(booking_data["date_from"])
        dt = date.fromisoformat(booking_data["date_to"])
        if df >= dt:
            raise ValueError("Booking: date_from musi być wcześniejsze niż date_to.")

    def _find_or_create_owner(self, owner_data: dict) -> int:
        email = owner_data.get("email")
        owner_id = self.owner_repo.find_by_email(email) if email else None
        if owner_id is not None:
            return owner_id

        return self.owner_repo.create_owner(
            first_name=owner_data["first_name"],
            last_name=owner_data["last_name"],
            phone=owner_data.get("phone"),
            email=owner_data.get("email"),
            adress=owner_data.get("adress", ""),
            nip=owner_data.get("nip"),
        )

    def create_reservation(self, owner_data: dict, animal_data: dict, booking_data: dict) -> int:
        self._validate_input(owner_data, animal_data, booking_data)

        owner_id = self._find_or_create_owner(owner_data)

        animal_id = self.animal_repo.create_animal(
            owner_id=owner_id,
            name=animal_data["name"],
            species=animal_data["species"],
            breed=animal_data.get("breed", ""),
            birth_date=animal_data.get("birth_date"),
            weight=animal_data.get("weight"),
            notes=animal_data.get("notes", ""),
        )

        booking_id = self.reservation_repo.insert_reservation(
            owner_id=owner_id,
            box_id=booking_data["box_id"],
            date_from=booking_data["date_from"],
            date_to=booking_data["date_to"],
            notes=booking_data.get("notes", ""),
        )

        df = date.fromisoformat(booking_data["date_from"])
        dt = date.fromisoformat(booking_data["date_to"])
        days = (dt - df).days

        self.booking_item_repo.create_item(
            booking_id=booking_id,
            animal_id=animal_id,
            daily_price=booking_data.get("daily_price", 0.0),
            days=days,
            discount_percent=booking_data.get("discount_percent", 0.0),
        )

        return booking_id

    # =========================================================
    # UC2 (UNAVAILABLE)
    # =========================================================

    def check_in(self, booking_id: int, box_id_override: int | None = None) -> int:
        if not isinstance(booking_id, int) or booking_id <= 0:
            raise ValueError("booking_id musi być dodatnią liczbą całkowitą.")

        booking = self.reservation_repo.get_reservation(booking_id)
        if not booking:
            raise ValueError("Nie znaleziono rezerwacji o podanym booking_id.")
        if booking["status"] != "NEW":
            raise ValueError(f"Nie można zameldować: status rezerwacji = {booking['status']} (wymagane NEW).")

        owner_id = booking["owner_id"]
        box_id = booking["box_id"] if box_id_override is None else box_id_override

        animal_ids = self.booking_item_repo.list_animals_for_booking(booking_id)
        if not animal_ids:
            raise ValueError("Brak zwierzęcia przypisanego do rezerwacji (bookings_items).")
        animal_id = animal_ids[0]  # light: 1 zwierzę

        if self.stay_repo.get_active_by_animal(animal_id) is not None:
            raise ValueError("To zwierzę ma już aktywny pobyt (ACTIVE).")

        if not self.boks_repo.is_available(box_id):
            raise ValueError("Wybrany boks nie jest dostępny (AVAILABLE).")

        stay_id = self.stay_repo.create_stay(
            booking_id=booking_id,
            owner_id=owner_id,
            animal_id=animal_id,
            box_id=box_id,
        )

        self.reservation_repo.set_status(booking_id, "CHECKED_IN")
        self.boks_repo.set_status(box_id, "UNAVAILABLE")
        # opcjonalnie: self.reservation_repo.set_box(booking_id, box_id)

        return stay_id

    def check_out(self, booking_id: int) -> None:
        if not isinstance(booking_id, int) or booking_id <= 0:
            raise ValueError("booking_id musi być dodatnią liczbą całkowitą.")

        active = self.stay_repo.get_active_by_booking(booking_id)
        if not active:
            raise ValueError("Brak aktywnego pobytu (ACTIVE) dla tej rezerwacji.")

        stay_id = active["id"]
        box_id = active["box_id"]

        self.stay_repo.close_stay(stay_id)

        self.reservation_repo.set_status(booking_id, "FINISHED")
        self.boks_repo.set_status(box_id, "AVAILABLE")

    # =========================================================
    # UC3 - Rozliczenie klientów
    # =========================================================

    @staticmethod
    def _round2(x: float) -> float:
        return float(f"{x:.2f}")

    def _calc_line_total(self, qty: int, unit_price: float, discount_percent: float) -> float:
        if qty < 0:
            raise ValueError("qty nie może być ujemne.")
        if unit_price < 0:
            raise ValueError("unit_price nie może być ujemne.")
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("discount_percent musi być w zakresie 0..100.")

        gross = qty * unit_price
        gross_after = gross * (1.0 - (discount_percent / 100.0))
        return self._round2(gross_after)

    def calculate_settlement_preview(self, booking_id: int) -> dict:
        """
        Zwraca podgląd rozliczenia bez zapisu do DB.
        Zakres LIGHT: tylko pozycje z bookings_items (pobyt) => settlements_items.
        """
        if not isinstance(booking_id, int) or booking_id <= 0:
            raise ValueError("booking_id musi być dodatnią liczbą całkowitą.")

        booking = self.reservation_repo.get_reservation(booking_id)
        if not booking:
            raise ValueError("Nie znaleziono rezerwacji o podanym booking_id.")

        items = self.booking_item_repo.list_items_for_booking(booking_id)
        if not items:
            raise ValueError("Brak pozycji rezerwacji (bookings_items) – nie ma czego rozliczać.")

        preview_items = []
        gross_total = 0.0

        for it in items:
            # BookingItemRepo zwraca dict: id, booking_id, animal_id, daily_price, days, discount_percent
            animal_id = it["animal_id"]
            days = int(it["days"])
            daily_price = float(it["daily_price"])
            disc = float(it["discount_percent"])

            line_total = self._calc_line_total(days, daily_price, disc)

            name = f"Pobyt – animal_id={animal_id}"
            preview_items.append(
                {
                    "item_name": name,
                    "qty": days,
                    "unit_price": self._round2(daily_price),
                    "discount_percent": self._round2(disc),
                    "line_total": line_total,
                }
            )
            gross_total += line_total

        gross_total = self._round2(gross_total)

        return {
            "booking": booking,
            "items": preview_items,
            "gross_total": gross_total,
        }

    def create_settlement(self, booking_id: int, notes: str = "") -> int:
        """
        Tworzy rozliczenie w DB:
        - waliduje booking_id
        - blokuje ponowne rozliczenie (UNIQUE booking_id)
        - liczy podgląd
        - zapisuje settlements + settlements_items
        Zwraca: settlement_id
        """
        booking = self.reservation_repo.get_reservation(booking_id)
        if not booking:
            raise ValueError("Nie znaleziono rezerwacji o podanym booking_id.")

        # zalecane w projekcie: rozliczamy dopiero po zakończeniu pobytu
        if booking["status"] != "FINISHED":
            raise ValueError("Rozliczenie możliwe dopiero dla rezerwacji o statusie FINISHED.")

        existing = self.settlement_repo.get_by_booking_id(booking_id)
        if existing:
            raise ValueError(f"Rozliczenie już istnieje (settlement_id={existing['id']}).")

        preview = self.calculate_settlement_preview(booking_id)
        gross_total = preview["gross_total"]
        items = preview["items"]

        settlement_id = self.settlement_repo.create_settlement(
            booking_id=booking_id,
            gross_total=gross_total,
            status="NEW",
            notes=notes or "",
        )

        for it in items:
            self.settlement_item_repo.insert_item(
                settlement_id=settlement_id,
                item_name=it["item_name"],
                qty=int(it["qty"]),
                unit_price=float(it["unit_price"]),
                discount_percent=float(it["discount_percent"]),
                line_total=float(it["line_total"]),
            )

        return settlement_id

    def get_settlement_details(self, booking_id: int) -> dict | None:
        """
        Pomocnicze pod GUI UC3:
        - znajdź settlement po booking_id
        - pobierz pozycje
        """
        s = self.settlement_repo.get_by_booking_id(booking_id)
        if not s:
            return None
        items = self.settlement_item_repo.list_items_for_settlement(s["id"])
        return {"settlement": s, "items": items}

    def close(self):
        self.owner_repo.close()
        self.animal_repo.close()
        self.reservation_repo.close()
        self.booking_item_repo.close()
        self.boks_repo.close()
        self.stay_repo.close()
        self.settlement_repo.close()
        self.settlement_item_repo.close()
