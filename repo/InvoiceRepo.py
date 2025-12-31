# repo/InvoiceRepo.py
import mysql.connector


class InvoiceRepo:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="12345",
            database="pet_hotel",
        )
        self.cursor = self.connection.cursor(dictionary=True)

    # ---------------- CREATE ----------------

    def create_invoice(
        self,
        settlement_id: int,
        invoice_no: str,
        buyer_name: str,
        buyer_address: str,
        buyer_nip: str | None,
        gross_total: float,
        status: str = "ISSUED",
    ) -> int:
        sql = """
            INSERT INTO invoices
              (settlement_id, invoice_no, buyer_name, buyer_address, buyer_nip, gross_total, status)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(
            sql,
            (settlement_id, invoice_no, buyer_name, buyer_address, buyer_nip, gross_total, status),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    # ---------------- READ ----------------

    def get_by_id(self, invoice_id: int) -> dict | None:
        sql = "SELECT * FROM invoices WHERE id = %s LIMIT 1"
        self.cursor.execute(sql, (invoice_id,))
        return self.cursor.fetchone()

    def get_by_settlement_id(self, settlement_id: int) -> dict | None:
        sql = "SELECT * FROM invoices WHERE settlement_id = %s LIMIT 1"
        self.cursor.execute(sql, (settlement_id,))
        return self.cursor.fetchone()

    def get_by_invoice_no(self, invoice_no: str) -> dict | None:
        sql = "SELECT * FROM invoices WHERE invoice_no = %s LIMIT 1"
        self.cursor.execute(sql, (invoice_no,))
        return self.cursor.fetchone()

    def list_invoices(self):
        sql = "SELECT * FROM invoices ORDER BY issued_at DESC"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # ---------------- UPDATE ----------------

    def set_status(self, invoice_id: int, status: str) -> None:
        sql = "UPDATE invoices SET status = %s WHERE id = %s"
        self.cursor.execute(sql, (status, invoice_id))
        self.connection.commit()

    # ---------------- HELPERS ----------------

    def get_next_invoice_number_for_year(self, year: int) -> str:
        """
        LIGHT generator:
        - wyszukuje ostatni numer dla danego roku w formacie FV/YYYY/NNNN
        - zwraca następny
        """
        prefix = f"FV/{year}/"
        sql = """
            SELECT invoice_no
            FROM invoices
            WHERE invoice_no LIKE %s
            ORDER BY id DESC
            LIMIT 1
        """
        self.cursor.execute(sql, (prefix + "%",))
        row = self.cursor.fetchone()
        if not row:
            return f"{prefix}0001"

        last_no = row["invoice_no"]
        try:
            last_seq = int(last_no.split("/")[-1])
        except Exception:
            last_seq = 0

        return f"{prefix}{last_seq + 1:04d}"

    # ---------------- CLOSE ----------------

    def close(self):
        self.cursor.close()
        self.connection.close()
