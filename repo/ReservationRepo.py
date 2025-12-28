import mysql.connector

class ReservationRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel",
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def insert_reservation(
        self,
        owner_id: int,
        box_id: int,
        date_from: str,
        date_to: str,
        notes: str = "",
    ) -> int:
        sql = """
            INSERT INTO bookings (owner_id, box_id, created_at, date_from, date_to, status, notes)
            VALUES (%s, %s, NOW(), %s, %s, 'NEW', %s)
        """
        self.cursor.execute(sql, (owner_id, box_id, date_from, date_to, notes))
        self.connection.commit()
        return self.cursor.lastrowid

    def list_reservations(self):
        sql = "SELECT * FROM bookings ORDER BY created_at DESC"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # ---------------- WYMAGANE POD UC2 ----------------

    def get_reservation(self, booking_id: int) -> dict | None:
        """
        Pobiera pojedynczą rezerwację po ID (UC2: wyszukaj istniejącą rezerwację).
        """
        sql = "SELECT * FROM bookings WHERE id = %s LIMIT 1"
        self.cursor.execute(sql, (booking_id,))
        return self.cursor.fetchone()

    def set_status(self, booking_id: int, status: str) -> None:
        """
        Ustawia status rezerwacji (NEW / CHECKED_IN / FINISHED).
        """
        sql = "UPDATE bookings SET status = %s WHERE id = %s"
        self.cursor.execute(sql, (status, booking_id))
        self.connection.commit()

    # (opcjonalne, ale przydatne) - jeśli chcesz zmienić boks przy meldunku
    def set_box(self, booking_id: int, box_id: int) -> None:
        """
        Podmienia box_id w rezerwacji (gdy recepcjonista robi relokację).
        """
        sql = "UPDATE bookings SET box_id = %s WHERE id = %s"
        self.cursor.execute(sql, (box_id, booking_id))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()