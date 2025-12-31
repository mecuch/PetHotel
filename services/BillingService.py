# services/BillingService.py
from datetime import datetime

from repo.SettlementRepo import SettlementRepo
from repo.SettlementItemRepo import SettlementItemRepo
from repo.InvoiceRepo import InvoiceRepo


class BillingService:
    def __init__(self):
        self.settlement_repo = SettlementRepo()
        self.settlement_item_repo = SettlementItemRepo()
        self.invoice_repo = InvoiceRepo()

    # ---------------- WALIDACJA ----------------

    @staticmethod
    def _validate_buyer(buyer_data: dict) -> None:
        name = (buyer_data.get("buyer_name") or "").strip()
        address = (buyer_data.get("buyer_address") or "").strip()
        nip = buyer_data.get("buyer_nip")

        if not name:
            raise ValueError("Nabywca: buyer_name jest wymagane.")
        if not address:
            raise ValueError("Nabywca: buyer_address jest wymagane.")

        if nip is None:
            return

        nip = str(nip).strip()
        if nip == "":
            buyer_data["buyer_nip"] = None
            return

        # LIGHT: prosta walidacja NIP (10 cyfr)
        if not nip.isdigit() or len(nip) != 10:
            raise ValueError("Nabywca: NIP musi mieć 10 cyfr (albo zostaw puste).")

        buyer_data["buyer_nip"] = nip

    # ---------------- PODGLĄD ----------------

    def invoice_preview_for_settlement(self, settlement_id: int, buyer_data: dict) -> dict:
        if not isinstance(settlement_id, int) or settlement_id <= 0:
            raise ValueError("settlement_id musi być dodatnią liczbą całkowitą.")

        self._validate_buyer(buyer_data)

        settlement = self.settlement_repo.get_by_id(settlement_id)
        if not settlement:
            raise ValueError("Nie znaleziono rozliczenia o podanym settlement_id.")

        existing = self.invoice_repo.get_by_settlement_id(settlement_id)
        if existing:
            raise ValueError(f"Faktura już istnieje (invoice_id={existing['id']}, nr={existing['invoice_no']}).")

        year = datetime.now().year
        invoice_no = self.invoice_repo.get_next_invoice_number_for_year(year)

        items = self.settlement_item_repo.list_items_for_settlement(settlement_id)

        return {
            "invoice_no": invoice_no,
            "issued_at": datetime.now(),
            "buyer_name": buyer_data["buyer_name"].strip(),
            "buyer_address": buyer_data["buyer_address"].strip(),
            "buyer_nip": buyer_data.get("buyer_nip"),
            "gross_total": float(settlement["gross_total"]),
            "settlement": settlement,
            "items": items,  # light: do podglądu, nie zapisujemy osobno w invoices
        }

    # ---------------- UTWORZENIE FAKTURY ----------------

    def create_invoice_for_settlement(self, settlement_id: int, buyer_data: dict) -> int:
        """
        UC4 (LIGHT):
        - settlement istnieje
        - brak istniejącej faktury dla settlement
        - walidacja danych nabywcy
        - generacja numeru faktury
        - INSERT do invoices
        Zwraca: invoice_id
        """
        if not isinstance(settlement_id, int) or settlement_id <= 0:
            raise ValueError("settlement_id musi być dodatnią liczbą całkowitą.")

        self._validate_buyer(buyer_data)

        settlement = self.settlement_repo.get_by_id(settlement_id)
        if not settlement:
            raise ValueError("Nie znaleziono rozliczenia o podanym settlement_id.")

        existing = self.invoice_repo.get_by_settlement_id(settlement_id)
        if existing:
            raise ValueError(f"Faktura już istnieje (invoice_id={existing['id']}, nr={existing['invoice_no']}).")

        year = datetime.now().year
        invoice_no = self.invoice_repo.get_next_invoice_number_for_year(year)

        invoice_id = self.invoice_repo.create_invoice(
            settlement_id=settlement_id,
            invoice_no=invoice_no,
            buyer_name=buyer_data["buyer_name"].strip(),
            buyer_address=buyer_data["buyer_address"].strip(),
            buyer_nip=buyer_data.get("buyer_nip"),
            gross_total=float(settlement["gross_total"]),
            status="ISSUED",
        )

        return invoice_id

    # ---------------- HELPERY ----------------

    def get_invoice_by_settlement(self, settlement_id: int) -> dict | None:
        return self.invoice_repo.get_by_settlement_id(settlement_id)

    def list_invoices(self):
        return self.invoice_repo.list_invoices()

    def close(self):
        self.settlement_repo.close()
        self.settlement_item_repo.close()
        self.invoice_repo.close()
