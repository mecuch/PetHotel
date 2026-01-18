import mysql.connector


class SettlementItemRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel",
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def insert_item(
        self,
        settlement_id: int,
        item_name: str,
        qty: int,
        unit_price: float,
        discount_percent: float,
        line_total: float,
    ) -> int:
        sql = """
            INSERT INTO settlements_items
              (settlement_id, item_name, qty, unit_price, discount_percent, line_total)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(
            sql,
            (settlement_id, item_name, qty, unit_price, discount_percent, line_total),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def list_items_for_settlement(self, settlement_id: int):
        sql = """
            SELECT *
            FROM settlements_items
            WHERE settlement_id = %s
            ORDER BY id
        """
        self.cursor.execute(sql, (settlement_id,))
        return self.cursor.fetchall()

    def delete_items_for_settlement(self, settlement_id: int) -> None:
        sql = "DELETE FROM settlements_items WHERE settlement_id = %s"
        self.cursor.execute(sql, (settlement_id,))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
