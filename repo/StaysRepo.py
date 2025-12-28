import mysql.connector


class StaysRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel",
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def create_stay(self, booking_id: int, owner_id: int, animal_id: int, box_id: int) -> int:
        sql = """
            INSERT INTO stays (booking_id, owner_id, animal_id, box_id, check_in_at, check_out_at, status)
            VALUES (%s, %s, %s, %s, NOW(), NULL, 'ACTIVE')
        """
        self.cursor.execute(sql, (booking_id, owner_id, animal_id, box_id))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_active_by_booking(self, booking_id: int) -> dict | None:
        sql = """
            SELECT id, booking_id, owner_id, animal_id, box_id, check_in_at, check_out_at, status
            FROM stays
            WHERE booking_id = %s AND status = 'ACTIVE' AND check_out_at IS NULL
            LIMIT 1
        """
        self.cursor.execute(sql, (booking_id,))
        return self.cursor.fetchone()

    def get_active_by_animal(self, animal_id: int) -> dict | None:
        sql = """
            SELECT id, booking_id, owner_id, animal_id, box_id, check_in_at, check_out_at, status
            FROM stays
            WHERE animal_id = %s AND status = 'ACTIVE' AND check_out_at IS NULL
            LIMIT 1
        """
        self.cursor.execute(sql, (animal_id,))
        return self.cursor.fetchone()

    def get_active_by_box(self, box_id: int) -> dict | None:
        sql = """
            SELECT id, booking_id, owner_id, animal_id, box_id, check_in_at, check_out_at, status
            FROM stays
            WHERE box_id = %s AND status = 'ACTIVE' AND check_out_at IS NULL
            LIMIT 1
        """
        self.cursor.execute(sql, (box_id,))
        return self.cursor.fetchone()

    def close_stay(self, stay_id: int) -> None:
        sql = """
            UPDATE stays
            SET check_out_at = NOW(), status = 'FINISHED'
            WHERE id = %s AND status = 'ACTIVE' AND check_out_at IS NULL
        """
        self.cursor.execute(sql, (stay_id,))
        self.connection.commit()

    def list_stays(self, active_only: bool = False) -> list[dict]:
        if active_only:
            sql = """
                SELECT id, booking_id, owner_id, animal_id, box_id, check_in_at, check_out_at, status
                FROM stays
                WHERE status = 'ACTIVE' AND check_out_at IS NULL
                ORDER BY check_in_at DESC
            """
            self.cursor.execute(sql)
            return self.cursor.fetchall()

        sql = """
            SELECT id, booking_id, owner_id, animal_id, box_id, check_in_at, check_out_at, status
            FROM stays
            ORDER BY check_in_at DESC
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()