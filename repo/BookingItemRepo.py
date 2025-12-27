# booking_item_repo.py
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
        self.cursor = self.connection.cursor()

    def create_item(
        self,
        booking_id: int,
        animal_id: int,
        daily_price: float,
        days: int,
        discount_percent: float) -> int:
        sql = """
            INSERT INTO bookings_items (booking_id, animal_id, daily_price, days, discount_percent)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (booking_id, animal_id, daily_price, days, discount_percent))
        self.connection.commit()
        return self.cursor.lastrowid

    def close(self):
        self.cursor.close()
        self.connection.close()
