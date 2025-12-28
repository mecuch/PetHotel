# services/RezerwacjaService.py
from datetime import date

from repo.OwnerRepo import OwnerRepo
from repo.AnimalRepo import AnimalRepo
from repo.ReservationRepo import ReservationRepo
from repo.BookingItemRepo import BookingItemRepo
from repo.BoxesRepo import BoksRepo
from repo.StaysRepo import StaysRepo


class ReservationService:
    def __init__(self):
        self.owner_repo = OwnerRepo()
        self.animal_repo = AnimalRepo()
        self.reservation_repo = ReservationRepo()
        self.booking_item_repo = BookingItemRepo()
        self.boks_repo = BoksRepo()
        self.stay_repo = StaysRepo()

    # ---------------- UC1 ----------------

    def _validate_input(self, owner_data: dict, animal_data: dict, booking_data: dict) -> None:
        # Owner
        if not owner_data.get("first_name") or not owner_data.get("last_name"):
            raise ValueError("Owner: first_name i last_name są wymagane.")
        if not owner_data.get("email") and not owner_data.get("phone"):
            raise ValueError("Owner: podaj email lub phone (do identyfikacji w bazie).")

        # Animal
        if not animal_data.get("name") or not animal_data.get("species"):
            raise ValueError("Animal: name i species są wymagane.")

        # Booking
        if not booking_data.get("box_id"):
            raise ValueError("Booking: box_id jest wymagane.")
        if not booking_data.get("date_from") or not booking_data.get("date_to"):
            raise ValueError("Booking: date_from i date_to są wymagane.")

        df = date.fromisoformat(booking_data["date_from"])
        dt = date.fromisoformat(booking_data["date_to"])
        if df >= dt:
            raise ValueError("Booking: date_from musi być wcześniejsze niż date_to.")

    def _find_or_create_owner(self, owner_data: dict) -> int:
        # OwnerRepo: masz find_by_email; jeśli wolisz także po telefonie, dopisz analogicznie w OwnerRepo
        email = owner_data.get("email")

        owner_id = None
        if email:
            owner_id = self.owner_repo.find_by_email(email)

        if owner_id is not None:
            return owner_id

        # Nie ma w bazie -> tworzymy
        return self.owner_repo.create_owner(
            first_name=owner_data["first_name"],
            last_name=owner_data["last_name"],
            phone=owner_data.get("phone"),
            email=owner_data.get("email"),
            adress=owner_data.get("adress", ""),  # u Ciebie jest "adress"
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

    # ---------------- UC2: CHECK-IN / CHECK-OUT ----------------

    def check_in(self, booking_id: int, box_id_override: int | None = None) -> int:
        """
        UC2 - Meldowanie (light, bez medycyny):
        - pobierz rezerwację po ID
        - status musi być NEW
        - pobierz animal_id z bookings_items (pierwsze)
        - sprawdź boks AVAILABLE
        - sprawdź czy zwierzę nie ma ACTIVE stay
        - utwórz stay
        - ustaw booking.status = CHECKED_IN
        - ustaw box.status = UNAVAILABLE
        Zwraca: stay_id
        """
        if not isinstance(booking_id, int) or booking_id <= 0:
            raise ValueError("booking_id musi być dodatnią liczbą całkowitą.")

        booking = self.reservation_repo.get_reservation(booking_id)
        if not booking:
            raise ValueError("Nie znaleziono rezerwacji o podanym booking_id.")

        if booking["status"] != "NEW":
            raise ValueError(
                f"Nie można zameldować: status rezerwacji = {booking['status']} (wymagane NEW)."
            )

        owner_id = booking["owner_id"]
        box_id = booking["box_id"] if box_id_override is None else box_id_override

        animal_ids = self.booking_item_repo.list_animals_for_booking(booking_id)
        if not animal_ids:
            raise ValueError("Brak zwierzęcia przypisanego do rezerwacji (bookings_items).")
        animal_id = animal_ids[0]  # wersja light: 1 zwierzę

        # Zwierzę nie może mieć aktywnego pobytu
        if self.stay_repo.get_active_by_animal(animal_id) is not None:
            raise ValueError("To zwierzę ma już aktywny pobyt (ACTIVE).")

        # Boks musi być dostępny
        if not self.boks_repo.is_available(box_id):
            raise ValueError("Wybrany boks nie jest dostępny (AVAILABLE).")

        # Utwórz stay
        stay_id = self.stay_repo.create_stay(
            booking_id=booking_id,
            owner_id=owner_id,
            animal_id=animal_id,
            box_id=box_id,
        )

        # Zmień statusy
        self.reservation_repo.set_status(booking_id, "CHECKED_IN")
        self.boks_repo.set_status(box_id, "UNAVAILABLE")

        # (opcjonalnie) jeśli użyłeś override i chcesz, aby rezerwacja wskazywała faktyczny boks:
        # self.reservation_repo.set_box(booking_id, box_id)

        return stay_id

    def check_out(self, booking_id: int) -> None:
        """
        UC2 - Wymeldowanie (light):
        - znajdź aktywny stay po booking_id
        - zamknij stay
        - ustaw booking.status = FINISHED
        - ustaw box.status = AVAILABLE
        """
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

    def close(self):
        self.owner_repo.close()
        self.animal_repo.close()
        self.reservation_repo.close()
        self.booking_item_repo.close()
        self.boks_repo.close()
        self.stay_repo.close()
