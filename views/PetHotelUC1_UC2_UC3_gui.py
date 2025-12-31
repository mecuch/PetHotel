import tkinter as tk
from tkinter import ttk, messagebox

from services.RezerwacjaService import ReservationService
from services.BillingService import BillingService


class PetHotel_GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PetHotel – Moduł podstawowy (UC1 + UC2)")
        self.geometry("860x680")
        self.resizable(False, False)

        self.service = ReservationService()
        self.billing = BillingService()

        # --- Notebook (zakładki) ---
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_uc1 = ttk.Frame(self.nb)
        self.tab_uc2 = ttk.Frame(self.nb)
        self.tab_uc3 = ttk.Frame(self.nb)
        self.tab_uc4 = ttk.Frame(self.nb)

        self.nb.add(self.tab_uc1, text="UC1 – Rezerwacja")
        self.nb.add(self.tab_uc2, text="UC2 – Meldunek/Wymeldowanie")
        self.nb.add(self.tab_uc3, text="UC3 – Rozliczenie")
        self.nb.add(self.tab_uc4, text="UC4 – Fakturowanie")

        # UC1
        self._build_uc1(self.tab_uc1)

        # UC2
        self._build_uc2(self.tab_uc2)

        # UC3
        self._build_uc3(self.tab_uc3)

        # UC4
        self._build_uc4(self.tab_uc4)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # =========================================================
    # UC1
    # =========================================================

    def _build_uc1(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent, padding=12)
        container.pack(fill="both", expand=True)

        self._build_owner_section(container)
        self._build_animal_section(container)
        self._build_booking_section(container)
        self._build_uc1_actions(container)

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

    def _build_uc1_actions(self, parent: ttk.Frame) -> None:
        frm = ttk.Frame(parent)
        frm.pack(fill="x", pady=(8, 0))

        ttk.Button(frm, text="Utwórz rezerwację (UC1)", command=self.on_create_reservation).pack(side="left")
        ttk.Button(frm, text="Pokaż rezerwacje", command=self.open_reservations_window).pack(side="left", padx=8)

        self.uc1_result_lbl = ttk.Label(frm, text="")
        self.uc1_result_lbl.pack(side="left", padx=12)

    def on_create_reservation(self) -> None:
        try:
            owner_data = {
                "first_name": self._get_str(self.owner_first_name),
                "last_name": self._get_str(self.owner_last_name),
                "phone": self._get_str(self.owner_phone) or None,
                "email": self._get_str(self.owner_email) or None,
                # UWAGA: w OwnerRepo masz "adress" – tu mapujemy z pola GUI "address"
                "adress": self._get_str(self.owner_address),
                "nip": self._opt_int(self._get_str(self.owner_nip)),
            }

            animal_data = {
                "name": self._get_str(self.animal_name),
                "species": self.animal_species.get().strip(),
                "breed": self._get_str(self.animal_breed) or "",
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

            self.uc1_result_lbl.config(text=f"OK: booking_id={booking_id}")
            messagebox.showinfo("Sukces", f"Utworzono rezerwację (ID={booking_id}).")

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się utworzyć rezerwacji:\n{e}")

    # =========================================================
    # UC2
    # =========================================================

    def _build_uc2(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent, padding=12)
        container.pack(fill="both", expand=True)

        # --- Panel akcji UC2 ---
        top = ttk.LabelFrame(container, text="UC2 – Meldowanie / Wymeldowywanie", padding=10)
        top.pack(fill="x", pady=(0, 10))

        self.uc2_booking_id = self._labeled_entry(top, "Booking ID*", 0, 0)
        self.uc2_box_override = self._labeled_entry(top, "Box ID (opcjonalnie)", 0, 2)

        btn_row = ttk.Frame(top)
        btn_row.grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

        ttk.Button(btn_row, text="Zamelduj (Check-in)", command=self.on_check_in).pack(side="left")
        ttk.Button(btn_row, text="Wymelduj (Check-out)", command=self.on_check_out).pack(side="left", padx=8)
        ttk.Button(btn_row, text="Odśwież listę pobytów", command=self._refresh_stays).pack(side="left", padx=8)

        self.uc2_result_lbl = ttk.Label(top, text="")
        self.uc2_result_lbl.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))

        # --- Lista pobytów (stays) ---
        stays_box = ttk.LabelFrame(container, text="Pobyty (stays)", padding=10)
        stays_box.pack(fill="both", expand=True)

        info = ttk.Label(stays_box, text="")
        info.pack(anchor="w", pady=(0, 6))
        self.stays_info_lbl = info

        columns = ("id", "booking_id", "owner_id", "animal_id", "box_id", "check_in_at", "check_out_at", "status")
        tree = ttk.Treeview(stays_box, columns=columns, show="headings", height=14)
        self.stays_tree = tree

        headers = {
            "id": "Stay ID",
            "booking_id": "Booking ID",
            "owner_id": "Owner ID",
            "animal_id": "Animal ID",
            "box_id": "Box ID",
            "check_in_at": "Check-in",
            "check_out_at": "Check-out",
            "status": "Status",
        }
        for c in columns:
            tree.heading(c, text=headers[c])

        tree.column("id", width=70, anchor="center")
        tree.column("booking_id", width=90, anchor="center")
        tree.column("owner_id", width=80, anchor="center")
        tree.column("animal_id", width=80, anchor="center")
        tree.column("box_id", width=70, anchor="center")
        tree.column("check_in_at", width=150, anchor="center")
        tree.column("check_out_at", width=150, anchor="center")
        tree.column("status", width=90, anchor="center")

        tree.pack(fill="both", expand=True, side="left")

        sb = ttk.Scrollbar(stays_box, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(fill="y", side="right")

        self._refresh_stays()

    def on_check_in(self) -> None:
        try:
            booking_id = self._opt_int(self._get_str(self.uc2_booking_id))
            if not booking_id:
                raise ValueError("Podaj Booking ID.")

            box_override_txt = self._get_str(self.uc2_box_override)
            box_override = self._opt_int(box_override_txt) if box_override_txt else None

            stay_id = self.service.check_in(booking_id, box_id_override=box_override)

            self.uc2_result_lbl.config(text=f"OK: stay_id={stay_id}")
            messagebox.showinfo("Sukces", f"Zameldowano zwierzę. stay_id={stay_id}")
            self._refresh_stays()

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zameldować:\n{e}")

    def on_check_out(self) -> None:
        try:
            booking_id = self._opt_int(self._get_str(self.uc2_booking_id))
            if not booking_id:
                raise ValueError("Podaj Booking ID.")

            self.service.check_out(booking_id)

            self.uc2_result_lbl.config(text=f"OK: booking_id={booking_id} -> FINISHED")
            messagebox.showinfo("Sukces", f"Wymeldowano zwierzę (booking_id={booking_id}).")
            self._refresh_stays()

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wymeldować:\n{e}")

    def _refresh_stays(self) -> None:
        # wyczyść
        for item in self.stays_tree.get_children():
            self.stays_tree.delete(item)

        try:
            rows = self.service.stay_repo.list_stays(active_only=False)  # list[dict]
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać pobytów:\n{e}")
            return

        if not rows:
            self.stays_info_lbl.config(text="Brak pobytów (stays) w bazie.")
            return

        self.stays_info_lbl.config(text=f"Liczba pobytów: {len(rows)}")

        def fmt(v):
            try:
                return v.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    return v.strftime("%Y-%m-%d")
                except Exception:
                    return "" if v is None else str(v)

        for r in rows:
            self.stays_tree.insert(
                "",
                "end",
                values=(
                    r.get("id"),
                    r.get("booking_id"),
                    r.get("owner_id"),
                    r.get("animal_id"),
                    r.get("box_id"),
                    fmt(r.get("check_in_at")),
                    fmt(r.get("check_out_at")),
                    r.get("status"),
                ),
            )

    # =========================================================
    # Okno rezerwacji
    # =========================================================

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
        tree.column("status", width=90, anchor="center")
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
            rows = self.service.reservation_repo.list_reservations()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać rezerwacji:\n{e}")
            return

        if not rows:
            info_lbl.config(text="Brak rezerwacji w bazie.")
            return

        info_lbl.config(text=f"Liczba rezerwacji: {len(rows)}")

        def fmt(v):
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

    # =========================================================
    # Helpers + close
    # =========================================================

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

    # =========================================================
    # UC3 – ROZLICZENIE
    # =========================================================

    def _build_uc3(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent, padding=12)
        container.pack(fill="both", expand=True)

        # --- Panel wejścia ---
        top = ttk.LabelFrame(container, text="UC3 – Rozliczenie rezerwacji", padding=10)
        top.pack(fill="x", pady=(0, 10))

        self.uc3_booking_id = self._labeled_entry(top, "Booking ID*", 0, 0)

        btns = ttk.Frame(top)
        btns.grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

        ttk.Button(btns, text="Podgląd rozliczenia", command=self.on_uc3_preview).pack(side="left")
        ttk.Button(btns, text="Zapisz rozliczenie", command=self.on_uc3_create).pack(side="left", padx=8)

        self.uc3_result_lbl = ttk.Label(top, text="")
        self.uc3_result_lbl.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))

        # --- Tabela pozycji ---
        items_box = ttk.LabelFrame(container, text="Pozycje rozliczenia", padding=10)
        items_box.pack(fill="both", expand=True)

        columns = ("item_name", "qty", "unit_price", "discount", "line_total")
        tree = ttk.Treeview(items_box, columns=columns, show="headings", height=14)
        self.uc3_tree = tree

        headers = {
            "item_name": "Pozycja",
            "qty": "Ilość",
            "unit_price": "Cena jedn.",
            "discount": "Rabat %",
            "line_total": "Wartość",
        }
        for c in columns:
            tree.heading(c, text=headers[c])

        tree.column("item_name", width=260, anchor="w")
        tree.column("qty", width=80, anchor="center")
        tree.column("unit_price", width=120, anchor="e")
        tree.column("discount", width=100, anchor="center")
        tree.column("line_total", width=120, anchor="e")

        tree.pack(fill="both", expand=True, side="left")

        sb = ttk.Scrollbar(items_box, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(fill="y", side="right")

        self.uc3_total_lbl = ttk.Label(container, text="Suma brutto: 0.00")
        self.uc3_total_lbl.pack(anchor="e", pady=(6, 0))

    def on_uc3_preview(self) -> None:
        # wyczyść tabelę
        for item in self.uc3_tree.get_children():
            self.uc3_tree.delete(item)

        try:
            booking_id = self._opt_int(self._get_str(self.uc3_booking_id))
            if not booking_id:
                raise ValueError("Podaj Booking ID.")

            preview = self.service.calculate_settlement_preview(booking_id)

            total = preview["gross_total"]

            for it in preview["items"]:
                self.uc3_tree.insert(
                    "",
                    "end",
                    values=(
                        it["item_name"],
                        it["qty"],
                        f"{it['unit_price']:.2f}",
                        f"{it['discount_percent']:.2f}",
                        f"{it['line_total']:.2f}",
                    ),
                )

            self.uc3_total_lbl.config(text=f"Suma brutto: {total:.2f}")
            self.uc3_result_lbl.config(text="Podgląd wygenerowany.")

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wygenerować podglądu:\n{e}")

    def on_uc3_create(self) -> None:
        try:
            booking_id = self._opt_int(self._get_str(self.uc3_booking_id))
            if not booking_id:
                raise ValueError("Podaj Booking ID.")

            settlement_id = self.service.create_settlement(booking_id)

            self.uc3_result_lbl.config(text=f"OK: settlement_id={settlement_id}")
            messagebox.showinfo(
                "Sukces",
                f"Utworzono rozliczenie (settlement_id={settlement_id})."
            )

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się utworzyć rozliczenia:\n{e}")

    # =========================================================
    # UC4 – FAKTUROWANIE
    # =========================================================

    def _build_uc4(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent, padding=12)
        container.pack(fill="both", expand=True)

        # --- Panel danych wejściowych ---
        top = ttk.LabelFrame(container, text="UC4 – Wystawianie faktury", padding=10)
        top.pack(fill="x", pady=(0, 10))

        self.uc4_settlement_id = self._labeled_entry(top, "Settlement ID*", 0, 0)

        self.uc4_buyer_name = self._labeled_entry(top, "Nabywca – nazwa / imię i nazwisko*", 1, 0, colspan=3)
        self.uc4_buyer_address = self._labeled_entry(top, "Nabywca – adres*", 2, 0, colspan=3)
        self.uc4_buyer_nip = self._labeled_entry(top, "NIP (opcjonalnie)", 3, 0)

        btns = ttk.Frame(top)
        btns.grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 0))

        ttk.Button(btns, text="Podgląd faktury", command=self.on_uc4_preview).pack(side="left")
        ttk.Button(btns, text="Wystaw fakturę", command=self.on_uc4_create).pack(side="left", padx=8)
        ttk.Button(btns, text="Odśwież listę faktur", command=self._refresh_invoices).pack(side="left", padx=8)

        self.uc4_result_lbl = ttk.Label(top, text="")
        self.uc4_result_lbl.grid(row=5, column=0, columnspan=4, sticky="w", pady=(8, 0))

        # --- Podgląd faktury (mini) ---
        preview = ttk.LabelFrame(container, text="Podgląd (light)", padding=10)
        preview.pack(fill="x", pady=(0, 10))

        self.uc4_preview_lbl = ttk.Label(preview, text="Numer: — | Kwota brutto: —")
        self.uc4_preview_lbl.pack(anchor="w")

        # --- Lista faktur ---
        box = ttk.LabelFrame(container, text="Wystawione faktury", padding=10)
        box.pack(fill="both", expand=True)

        self.uc4_info_lbl = ttk.Label(box, text="")
        self.uc4_info_lbl.pack(anchor="w", pady=(0, 6))

        columns = ("id", "invoice_no", "settlement_id", "issued_at", "buyer_name", "buyer_nip", "gross_total", "status")
        tree = ttk.Treeview(box, columns=columns, show="headings", height=14)
        self.uc4_tree = tree

        headers = {
            "id": "ID",
            "invoice_no": "Numer",
            "settlement_id": "Settlement ID",
            "issued_at": "Data",
            "buyer_name": "Nabywca",
            "buyer_nip": "NIP",
            "gross_total": "Brutto",
            "status": "Status",
        }
        for c in columns:
            tree.heading(c, text=headers[c])

        tree.column("id", width=60, anchor="center")
        tree.column("invoice_no", width=140, anchor="center")
        tree.column("settlement_id", width=100, anchor="center")
        tree.column("issued_at", width=150, anchor="center")
        tree.column("buyer_name", width=220, anchor="w")
        tree.column("buyer_nip", width=110, anchor="center")
        tree.column("gross_total", width=90, anchor="e")
        tree.column("status", width=90, anchor="center")

        tree.pack(fill="both", expand=True, side="left")

        sb = ttk.Scrollbar(box, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(fill="y", side="right")

        self._refresh_invoices()

    def on_uc4_preview(self) -> None:
        try:
            settlement_id = self._opt_int(self._get_str(self.uc4_settlement_id))
            if not settlement_id:
                raise ValueError("Podaj Settlement ID.")

            buyer_data = {
                "buyer_name": self._get_str(self.uc4_buyer_name),
                "buyer_address": self._get_str(self.uc4_buyer_address),
                "buyer_nip": self._get_str(self.uc4_buyer_nip) or None,
            }

            preview = self.billing.invoice_preview_for_settlement(settlement_id, buyer_data)

            no = preview["invoice_no"]
            gross = float(preview["gross_total"])
            self.uc4_preview_lbl.config(text=f"Numer: {no} | Kwota brutto: {gross:.2f}")
            self.uc4_result_lbl.config(text="Podgląd wygenerowany.")

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wygenerować podglądu:\n{e}")

    def on_uc4_create(self) -> None:
        try:
            settlement_id = self._opt_int(self._get_str(self.uc4_settlement_id))
            if not settlement_id:
                raise ValueError("Podaj Settlement ID.")

            buyer_data = {
                "buyer_name": self._get_str(self.uc4_buyer_name),
                "buyer_address": self._get_str(self.uc4_buyer_address),
                "buyer_nip": self._get_str(self.uc4_buyer_nip) or None,
            }

            invoice_id = self.billing.create_invoice_for_settlement(settlement_id, buyer_data)

            self.uc4_result_lbl.config(text=f"OK: invoice_id={invoice_id}")
            messagebox.showinfo("Sukces", f"Wystawiono fakturę (invoice_id={invoice_id}).")
            self._refresh_invoices()

        except ValueError as e:
            messagebox.showerror("Błąd walidacji", str(e))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wystawić faktury:\n{e}")

    def _refresh_invoices(self) -> None:
        for item in self.uc4_tree.get_children():
            self.uc4_tree.delete(item)

        try:
            rows = self.billing.list_invoices()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać faktur:\n{e}")
            return

        if not rows:
            self.uc4_info_lbl.config(text="Brak faktur w bazie.")
            return

        self.uc4_info_lbl.config(text=f"Liczba faktur: {len(rows)}")

        def fmt(v):
            try:
                return v.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return "" if v is None else str(v)

        for r in rows:
            self.uc4_tree.insert(
                "",
                "end",
                values=(
                    r.get("id"),
                    r.get("invoice_no"),
                    r.get("settlement_id"),
                    fmt(r.get("issued_at")),
                    r.get("buyer_name"),
                    r.get("buyer_nip") or "",
                    f"{float(r.get('gross_total')):.2f}",
                    r.get("status"),
                ),
            )

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

    def on_close(self) -> None:
        try:
            self.service.close()
        except Exception:
            pass
        try:
            self.billing.close()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = PetHotel_GUI()
    app.mainloop()
