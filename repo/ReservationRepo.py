import mysql.connector

class ReservationRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel"
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def insert_reservation (self,
                            owner_id: int,
                            box_id: int,
                            date_from: str,
                            date_to: str,
                            notes: str = "") -> int:
        sql = """
            INSERT INTO bookings (owner_id, box_id, created_at, date_from, date_to, status, notes)
            VALUES (%s, %s, NOW(), %s, %s, 'NEW', %s)
        """
        self.cursor.execute(sql, (owner_id, box_id, date_from, date_to, notes))
        self.connection.commit()
        return self.cursor.lastrowid

    def list_reservations(self):
        sql = """SELECT * FROM bookings ORDER BY created_at DESC"""
        self.cursor.execute(sql)
        records = self.cursor.fetchall()
        return records

    def close(self):
        self.cursor.close()
        self.connection.close()

test_reservation = ReservationRepo()
test_listning = test_reservation.list_reservations()
print(test_listning)