import mysql.connector


class SettlementRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel",
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def create_settlement(
        self,
        booking_id: int,
        gross_total: float,
        status: str = "NEW",
        notes: str = "",
    ) -> int:
        sql = """
            INSERT INTO settlements (booking_id, status, gross_total, notes)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(sql, (booking_id, status, gross_total, notes))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_by_id(self, settlement_id: int) -> dict | None:
        sql = "SELECT * FROM settlements WHERE id = %s LIMIT 1"
        self.cursor.execute(sql, (settlement_id,))
        return self.cursor.fetchone()

    def get_by_booking_id(self, booking_id: int) -> dict | None:
        sql = "SELECT * FROM settlements WHERE booking_id = %s LIMIT 1"
        self.cursor.execute(sql, (booking_id,))
        return self.cursor.fetchone()

    def list_settlements(self):
        sql = "SELECT * FROM settlements ORDER BY created_at DESC"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def set_status(self, settlement_id: int, status: str) -> None:
        sql = "UPDATE settlements SET status = %s WHERE id = %s"
        self.cursor.execute(sql, (status, settlement_id))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
