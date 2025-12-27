import tkinter as tk
from tkinter import ttk, messagebox

from services.RezerwacjaService import ReservationService


class UC1_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PetHotel – UC1 Rezerwacja pobytu")
        self.geometry("820x620")
        self.resizable(False, False)

        self.service = ReservationService()

        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        self._build_owner_section(container)
        self._build_animal_section(container)
        self._build_booking_section(container)
        self._build_actions(container)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- UI SECTIONS ----------------

    def _build_owner_section(self, parent: ttk.Frame) -> None:
        frm = ttk.LabelFrame(parent, text="Właściciel (Owner)", padding=10)
        frm.pack(fill="x", pady=(0, 10))

        self.owner_first_name = self._labeled_entry(frm, "Imię*", 0, 0)
        self.owner_last_name = self._labeled_entry(frm, "Nazwisko*", 0, 2)
        self.owner_phone = self._labeled_entry(frm, "Telefon", 1, 0)
        self.owner_email = self._labeled_entry(frm, "Email", 1, 2)
        self.owner_address = self._labeled_entry(frm, "Adres", 2, 0, colspan=3)
        self.owner_nip = self._labeled_entry(frm, "NIP (opcjonalnie)", 3, 0)

        ttk.Label(frm, text="* pola wymagane (min. email lub telefon)").grid(
            row=3, column=2, columnspan=2, sticky="w", padx=8
        )

    def _build_animal_section(self, parent: ttk.Frame) -> None:
        frm = ttk.LabelFrame(parent, text="Zwierzę (Animal)", padding=10)
        frm.pack(fill="x", pady=(0, 10))

        self.animal_name = self._labeled_entry(frm, "Imię zwierzęcia*", 0, 0)
        self.animal_species = self._labeled_combo(frm, "Gatunek*", 0, 2, values=["DOG", "CAT"])
        self.animal_breed = self._labeled_entry(frm, "Rasa", 1, 0)
        self.animal_birth_date = self._labeled_entry(frm, "Data ur. (YYYY-MM-DD)", 1, 2)
        self.animal_weight = self._labeled_entry(frm, "Waga (kg)", 2, 0)
        self.animal_notes = self._labeled_entry(frm, "Uwagi", 2, 2, colspan=1)

    def _build_booking_section(self, parent: ttk.Frame) -> None:
        frm = ttk.LabelFrame(parent, text="Rezerwacja (Booking)", padding=10)
        frm.pack(fill="x", pady=(0, 10))

        self.booking_box_id = self._labeled_entry(frm, "Box ID*", 0, 0)
        self.booking_date_from = self._labeled_entry(frm, "Data od* (YYYY-MM-DD)", 0, 2)
        self.booking_date_to = self._labeled_entry(frm, "Data do* (YYYY-MM-DD)", 1, 2)
        self.booking_daily_price = self._labeled_entry(frm, "Cena dzienna", 1, 0)
        self.booking_discount = self._labeled_entry(frm, "Rabat %", 2, 0)
        self.booking_notes = self._labeled_entry(frm, "Uwagi", 2, 2, colspan=1)

        ttk.Label(frm, text="* pola wymagane").grid(row=3, column=0, columnspan=4, sticky="w", padx=8)

    def _build_actions(self, parent: ttk.Frame) -> None:
        frm = ttk.Frame(parent)
        frm.pack(fill="x", pady=(8, 0))

        ttk.Button(frm, text="Utwórz rezerwację (UC1)", command=self.on_create_reservation).pack(side="left")

        ttk.Button(frm, text="Pokaż rezerwacje", command=self.open_reservations_window).pack(side="left", padx=8)

        self.result_lbl = ttk.Label(frm, text="")
        self.result_lbl.pack(side="left", padx=12)

    # ---------------- HELPERS ----------------

    def _labeled_entry(self, parent: ttk.Frame, label: str, row: int, col: int, colspan: int = 1) -> ttk.Entry:
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", padx=6, pady=4)
        ent = ttk.Entry(parent, width=34)
        ent.grid(row=row, column=col + 1, columnspan=colspan, sticky="we", padx=6, pady=4)
        return ent

    def _labeled_combo(self, parent: ttk.Frame, label: str, row: int, col: int, values: list[str]) -> ttk.Combobox:
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", padx=6, pady=4)
        cmb = ttk.Combobox(parent, width=31, values=values, state="readonly")
        cmb.grid(row=row, column=col + 1, sticky="we", padx=6, pady=4)
        cmb.set(values[0])
        return cmb

    @staticmethod
    def _get_str(entry: ttk.Entry) -> str:
        return entry.get().strip()

    @staticmethod
    def _opt_int(text: str) -> int | None:
        text = text.strip()
        if not text:
            return None
        return int(text)

    @staticmethod
    def _opt_float(text: str) -> float | None:
        text = text.strip().replace(",", ".")
        if not text:
            return None
        return float(text)

    # ---------------- ACTIONS ----------------

    def on_create_reservation(self) -> None:
        try:
            owner_data = {
                "first_name": self._get_str(self.owner_first_name),
                "last_name": self._get_str(self.owner_last_name),
                "phone": self._get_str(self.owner_phone) or None,
                "email": self._get_str(self.owner_email) or None,
                "address": self._get_str(self.owner_address),
                "nip": self._opt_int(self._get_str(self.owner_nip)),
            }

            animal_data = {
                "name": self._get_str(self.animal_name),
                "species": self.animal_species.get().strip(),
                "breed": self._get_str(self.animal_breed) or None,
                "birth_date": self._get_str(self.animal_birth_date) or None,
                "weight": self._opt_float(self._get_str(self.animal_weight)),
                "notes": self._get_str(self.animal_notes) or "",
            }

            booking_data = {
                "box_id": self._opt_int(self._get_str(self.booking_box_id)),
                "date_from": self._get_str(self.booking_date_from),
                "date_to": self._get_str(self.booking_date_to),
                "daily_price": self._opt_float(self._get_str(self.booking_daily_price)) or 0.0,
                "discount_percent": self._opt_float(self._get_str(self.booking_discount)) or 0.0,
                "notes": self._get_str(self.booking_notes) or "",
            }

            booking_id = self.service.create_reservation(owner_data, animal_data, booking_data)

            self.result_lbl.config(text=f"OK: booking_id={booking_id}")
            messagebox.showinfo("Sukces", f"Utworzono rezerwację (ID={booking_id}).")

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się utworzyć rezerwacji:\n{e}")

    # ---------------- RESERVATIONS WINDOW (NO SQL IN GUI) ----------------

    def open_reservations_window(self) -> None:
        win = tk.Toplevel(self)
        win.title("Lista rezerwacji")
        win.geometry("760x360")
        win.resizable(True, True)

        top = ttk.Frame(win, padding=10)
        top.pack(fill="both", expand=True)

        info_lbl = ttk.Label(top, text="")
        info_lbl.pack(anchor="w", pady=(0, 6))

        columns = ("id", "owner_id", "box_id", "date_from", "date_to", "status", "created_at", "notes")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=12)

        headers = {
            "id": "ID",
            "owner_id": "Owner ID",
            "box_id": "Box ID",
            "date_from": "Od",
            "date_to": "Do",
            "status": "Status",
            "created_at": "Utworzono",
            "notes": "Uwagi",
        }
        for c in columns:
            tree.heading(c, text=headers[c])

        tree.column("id", width=60, anchor="center")
        tree.column("owner_id", width=80, anchor="center")
        tree.column("box_id", width=70, anchor="center")
        tree.column("date_from", width=100, anchor="center")
        tree.column("date_to", width=100, anchor="center")
        tree.column("status", width=80, anchor="center")
        tree.column("created_at", width=150, anchor="center")
        tree.column("notes", width=220, anchor="w")

        tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill="y", side="right")

        btn_bar = ttk.Frame(win, padding=(10, 0, 10, 10))
        btn_bar.pack(fill="x")

        ttk.Button(btn_bar, text="Odśwież", command=lambda: self._load_reservations(tree, info_lbl)).pack(side="left")
        ttk.Button(btn_bar, text="Zamknij", command=win.destroy).pack(side="right")

        self._load_reservations(tree, info_lbl)

    def _load_reservations(self, tree: ttk.Treeview, info_lbl: ttk.Label) -> None:
        for item in tree.get_children():
            tree.delete(item)

        try:
            rows = self.service.reservation_repo.list_reservations()  # lista dictów
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać rezerwacji:\n{e}")
            return

        if not rows:
            info_lbl.config(text="Brak rezerwacji w bazie.")
            return

        info_lbl.config(text=f"Liczba rezerwacji: {len(rows)}")

        def fmt(v):
            # datetime/date -> string, reszta bez zmian
            try:
                return v.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    return v.strftime("%Y-%m-%d")
                except Exception:
                    return "" if v is None else str(v)

        for r in rows:
            tree.insert(
                "",
                "end",
                values=(
                    r.get("id"),
                    r.get("owner_id"),
                    r.get("box_id"),
                    fmt(r.get("date_from")),
                    fmt(r.get("date_to")),
                    r.get("status"),
                    fmt(r.get("created_at")),
                    r.get("notes", ""),
                ),
            )

    # ---------------- CLOSE ----------------

    def on_close(self) -> None:
        try:
            self.service.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = UC1_GUI()
    app.mainloop()
