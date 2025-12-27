import mysql.connector

class AnimalRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel"
        )
        self.cursor = self.connection.cursor()

    def create_animal(self,
                      owner_id: int,
                      name: str,
                      species: str,
                      breed: str,
                      birth_date: str,
                      weight: int,
                      notes: str) -> int:
        sql = """
                            INSERT INTO animals (owner_id, name, species, breed, birth_date, weight, notes)
                            VALUES (%s, %s,  %s, %s, %s, %s, %s)
                        """
        self.cursor.execute(sql, (owner_id, name, species, breed, birth_date, weight, notes))
        self.connection.commit()
        return self.cursor.lastrowid

    def close(self):
        self.cursor.close()
        self.connection.close()
