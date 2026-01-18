import mysql.connector

class OwnerRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel"
        )
        self.cursor = self.connection.cursor()

    def create_owner(self,
                     first_name: str,
                     last_name: str,
                     phone: int,
                     email: str,
                     adress: str,
                     nip: int = None) -> int:
        sql = """
                    INSERT INTO owners (first_name, last_name, phone, email, adress, nip)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
        self.cursor.execute(sql, (first_name, last_name, phone, email, adress, nip))
        self.connection.commit()
        return self.cursor.lastrowid

    def find_by_email(self, email: str) -> int | None:
        sql = """ SELECT id FROM owners WHERE email = %s LIMIT 1"""
        self.cursor.execute(sql, (email,))
        record = self.cursor.fetchone()
        if record is None:
            return None
        else:
            return record[0]


    def close(self):
        self.cursor.close()
        self.connection.close()
