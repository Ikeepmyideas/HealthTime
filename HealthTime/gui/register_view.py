import tkinter as tk
from tkinter import messagebox
from dao.user_dao import UserDAO

ROLE_OPTIONS = ["patient"]

class RegisterView:
    def __init__(self, root, theme="light"):
        self.root = root
        self.root.title("HealthTime - Register")
        self.root.geometry("420x420")

        if theme == "dark":
            bg_color = "#16212A"
            card_color = "#253747"
            text_color = "#EAEAEA"
            entry_bg = "#3A3A3A"
            entry_fg = "#FFFFFF"
            accent = "#4FC3F7"
        else:
            bg_color = "#f0f2f5"
            card_color = "#FFFFFF"
            text_color = "#000000"
            entry_bg = "#C4C4C4"
            entry_fg = "#000000"
            accent = "#4CAF50"

        self.root.configure(bg=bg_color)

        card = tk.Frame(root, bg=card_color, padx=25, pady=25)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text="Create Account",
            font=("Helvetica", 20, "bold"),
            bg=card_color,
            fg=accent
        ).pack(pady=(0, 25))

        def field(label):
            tk.Label(card, text=label, bg=card_color, fg=text_color,
                     font=("Helvetica", 11)).pack(anchor="w")
            entry = tk.Entry(card, bg=entry_bg, fg=entry_fg,
                             insertbackground=entry_fg,
                             relief="flat", font=("Helvetica", 11))
            entry.pack(fill="x", pady=(4, 14), ipady=6)
            return entry

        self.name_entry = field("Full Name")
        self.username_entry = field("Username")
        self.password_entry = field("Password")
        self.password_entry.config(show="*")

        tk.Label(card, text="Role", bg=card_color, fg=text_color,
                 font=("Helvetica", 11)).pack(anchor="w")

        self.role_var = tk.StringVar(value=ROLE_OPTIONS[0])
        role_menu = tk.OptionMenu(card, self.role_var, *ROLE_OPTIONS)
        role_menu.config(
            bg=entry_bg,
            fg=entry_fg,
            activebackground=accent,
            relief="flat"
        )
        role_menu["menu"].config(bg=entry_bg, fg=entry_fg)
        role_menu.pack(fill="x", pady=(4, 25))

        tk.Button(
            card,
            text="Register",
            bg=accent,
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            pady=10,
            command=self.register
        ).pack(fill="x")

    def register(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not name or not username or not password:
            messagebox.showwarning("Validation Error", "All fields are required.")
            return

        success, msg = UserDAO.register_user(name, username, password, role)
        if success:
            messagebox.showinfo("Success", msg)
            self.root.destroy()
        else:
            messagebox.showerror("Error", msg)
