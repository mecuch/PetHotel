import mysql.connector

class BoksRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel"
        )
        self.cursor = self.connection.cursor()

    def get_all_boxes(self):
        self.cursor.execute("SELECT id, number, status FROM boxes")
        return self.cursor.fetchall()



    def get_available_boxes(self):
        self.cursor.execute("SELECT id, number, status FROM boxes WHERE status = 'AVAILABLE'")
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()

test = BoksRepo()
testall = test.get_all_boxes()
testavail = test.get_available_boxes()
print(testall)
print(testavail)