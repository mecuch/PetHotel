import mysql.connector
from mysql.connector import Error

def main():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",          # jeśli masz innego usera, zmień
            password="12345",     # <-- WPISZ SWOJE HASŁO
            database="pet_hotel"
        )

        if connection.is_connected():
            print("✅ Połączono z MySQL")

            cursor = connection.cursor()
            cursor.execute("SELECT id, number, status FROM boxes")

            rows = cursor.fetchall()

            print("📦 Boksy w bazie:")
            for row in rows:
                print(row)

            cursor.close()

    except Error as e:
        print("❌ Błąd połączenia lub zapytania:")
        print(e)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔌 Połączenie zamknięte")

if __name__ == "__main__":
    main()
