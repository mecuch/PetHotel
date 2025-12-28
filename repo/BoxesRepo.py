import mysql.connector


class BoksRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel",
        )
        # zostawiam zwykły cursor jak miałeś; jeśli wolisz dict-y, ustaw dictionary=True
        self.cursor = self.connection.cursor()

    def get_all_boxes(self):
        self.cursor.execute("SELECT id, number, status FROM boxes")
        return self.cursor.fetchall()

    def get_available_boxes(self):
        self.cursor.execute("SELECT id, number, status FROM boxes WHERE status = 'AVAILABLE'")
        return self.cursor.fetchall()

    # ---------------- WYMAGANE POD UC2 ----------------

    def get_box(self, box_id: int):
        """
        Pobiera pojedynczy boks po ID.
        Zwraca tuple (id, number, status) albo None.
        """
        self.cursor.execute("SELECT id, number, status FROM boxes WHERE id = %s LIMIT 1", (box_id,))
        return self.cursor.fetchone()

    def is_available(self, box_id: int) -> bool:
        """
        True jeśli boks ma status AVAILABLE.
        """
        row = self.get_box(box_id)
        if not row:
            return False
        # row = (id, number, status)
        return row[2] == "AVAILABLE"

    def set_status(self, box_id: int, status: str) -> None:
        """
        Ustawia status boksu (AVAILABLE / OCCUPIED).
        """
        self.cursor.execute("UPDATE boxes SET status = %s WHERE id = %s", (status, box_id))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()