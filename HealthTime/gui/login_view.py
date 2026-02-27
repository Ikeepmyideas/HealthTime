import tkinter as tk
from tkinter import messagebox
from dao.user_dao import UserDAO
from gui.dashboards.patient_dashboard import PatientDashboard
from gui.dashboards.admin_dashboard import AdminDashboard
from gui.dashboards.doctor_dashboard import DoctorDashboard

class LoginView:
    def __init__(self, root, theme="light"):
        self.root = root
        self.root.title("HealthTime - Login")
        self.root.geometry("420x360")

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
            text="Welcome Back",
            font=("Helvetica", 20, "bold"),
            bg=card_color,
            fg=accent
        ).pack(pady=(0, 25))

        def field(label, show=None):
            tk.Label(
                card,
                text=label,
                bg=card_color,
                fg=text_color,
                font=("Helvetica", 11)
            ).pack(anchor="w")

            entry = tk.Entry(
                card,
                bg=entry_bg,
                fg=entry_fg,
                insertbackground=entry_fg,
                relief="flat",
                font=("Helvetica", 11),
                show=show
            )
            entry.pack(fill="x", pady=(4, 18), ipady=6)
            return entry

        self.username_entry = field("Username")
        self.password_entry = field("Password", show="*")

        tk.Button(
            card,
            text="Login",
            bg=accent,
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            pady=10,
            command=self.login
        ).pack(fill="x", pady=(10, 0))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Validation Error", "Please enter username and password.")
            return

        user = UserDAO.authenticate(username, password)

        if user is None:
            messagebox.showerror("Login Failed", "Invalid username or password")
        elif "error" in user:
            messagebox.showwarning("Login", user["error"])
        

        messagebox.showinfo("Login Success",f"Welcome {user['name']} ({user['role']})")
        self.root.destroy()

        dashboard_root = tk.Tk()
        if user["role"] == "patient":
            PatientDashboard(dashboard_root,user)
        elif user["role"] == "admin":
            AdminDashboard(dashboard_root, user)
        elif user["role"] == "doctor":
            DoctorDashboard(dashboard_root, user)
        dashboard_root.mainloop()
