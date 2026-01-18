import mysql.connector


class BookingItemRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel",
        )
        self.cursor = self.connection.cursor(dictionary=True)

    # ---------------- UC1 ----------------

    def create_item(
        self,
        booking_id: int,
        animal_id: int,
        daily_price: float,
        days: int,
        discount_percent: float,
    ) -> int:
        sql = """
            INSERT INTO bookings_items (booking_id, animal_id, daily_price, days, discount_percent)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(
            sql, (booking_id, animal_id, daily_price, days, discount_percent)
        )
        self.connection.commit()
        return self.cursor.lastrowid

    # ---------------- UC2 ----------------

    def list_items_for_booking(self, booking_id: int) -> list[dict]:
        """
        Zwraca wszystkie pozycje rezerwacji (booking_items) dla danej rezerwacji.
        """
        sql = """
            SELECT id, booking_id, animal_id, daily_price, days, discount_percent
            FROM bookings_items
            WHERE booking_id = %s
            ORDER BY id
        """
        self.cursor.execute(sql, (booking_id,))
        return self.cursor.fetchall()

    def list_animals_for_booking(self, booking_id: int) -> list[int]:
        """
        Zwraca listę animal_id przypisanych do rezerwacji.
        """
        sql = """
            SELECT animal_id
            FROM bookings_items
            WHERE booking_id = %s
            ORDER BY id
        """
        self.cursor.execute(sql, (booking_id,))
        rows = self.cursor.fetchall()
        return [row["animal_id"] for row in rows]

    def get_item(self, booking_id: int, animal_id: int) -> dict | None:
        """
        Zwraca konkretną pozycję rezerwacji
        """
        sql = """
            SELECT id, booking_id, animal_id, daily_price, days, discount_percent
            FROM bookings_items
            WHERE booking_id = %s AND animal_id = %s
            LIMIT 1
        """
        self.cursor.execute(sql, (booking_id, animal_id))
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.connection.close()