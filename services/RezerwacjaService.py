from datetime import date

from repo.OwnerRepo import OwnerRepo
from repo.AnimalRepo import AnimalRepo
from repo.ReservationRepo import ReservationRepo
from repo.BookingItemRepo import BookingItemRepo


class ReservationService:
    def __init__(self):
        self.owner_repo = OwnerRepo()
        self.animal_repo = AnimalRepo()
        self.reservation_repo = ReservationRepo()
        self.booking_item_repo = BookingItemRepo()

    # --- WALIDACJA WEJŚCIA ---
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

        # Daty: zakładamy string 'YYYY-MM-DD' i porównujemy jako date
        df = date.fromisoformat(booking_data["date_from"])
        dt = date.fromisoformat(booking_data["date_to"])
        if df >= dt:
            raise ValueError("Booking: date_from musi być wcześniejsze niż date_to.")

    # --- FIND OR CREATE OWNER ---
    def _find_or_create_owner(self, owner_data: dict) -> int:
        email = owner_data.get("email")
        phone = owner_data.get("phone")

        owner_id = None
        if email:
            owner_id = self.owner_repo.find_by_email(email)

        if owner_id is None and phone:
            owner_id = self.owner_repo.find_by_phone(phone)

        if owner_id is not None:
            return owner_id

        # Nie ma w bazie -> tworzymy
        return self.owner_repo.create_owner(
            first_name=owner_data["first_name"],
            last_name=owner_data["last_name"],
            phone=owner_data.get("phone"),
            email=owner_data.get("email"),
            adress=owner_data.get("adress", ""),
            nip=owner_data.get("nip")
        )

    # --- GŁÓWNA METODA UC1 ---
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
            notes=animal_data.get("notes", "")
        )

        booking_id = self.reservation_repo.create_booking(
            owner_id=owner_id,
            box_id=booking_data["box_id"],
            date_from=booking_data["date_from"],
            date_to=booking_data["date_to"],
            notes=booking_data.get("notes", "")
        )

        # days: najprościej liczyć w Pythonie
        df = date.fromisoformat(booking_data["date_from"])
        dt = date.fromisoformat(booking_data["date_to"])
        days = (dt - df).days

        self.booking_item_repo.create_item(
            booking_id=booking_id,
            animal_id=animal_id,
            daily_price=booking_data.get("daily_price", 0.0),
            days=days,
            discount_percent=booking_data.get("discount_percent", 0.0)
        )

        return booking_id

    def close(self):
        self.owner_repo.close()
        self.animal_repo.close()
        self.reservation_repo.close()
        self.booking_item_repo.close()
