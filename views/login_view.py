import tkinter as tk
from tkinter import messagebox


class LoginWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Logowanie")
        self.root.geometry("300x150")
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        # Etykieta
        label = tk.Label(self.root, text="Login:")
        label.pack(pady=(20, 5))

        # Pole tekstowe (textbox)
        self.login_entry = tk.Entry(self.root, width=30)
        self.login_entry.pack()

        # Przycisk
        login_button = tk.Button(
            self.root,
            text="Zaloguj",
            command=self._on_login_clicked
        )
        login_button.pack(pady=15)

    def _on_login_clicked(self):
        login = self.login_entry.get().strip()

        if not login:
            messagebox.showwarning("Błąd", "Pole login nie może być puste.")
            return

        # Na tym etapie tylko demonstracja działania
        messagebox.showinfo("Info", f"Próba logowania użytkownika: {login}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
