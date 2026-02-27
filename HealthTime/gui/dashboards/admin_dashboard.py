import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

from dao.admin_dao import AdminDAO


class AdminDashboard:
    def __init__(self, root, user, theme="light"):
        self.root = root
        self.user = user
        self.theme = theme

        self.root.title("HealthTime - Admin")
        self.root.geometry("1100x650")
        self.root.minsize(1000, 600)

        self.apply_theme()
        self.build_layout()
        self.show_dashboard()

    def apply_theme(self):
        if self.theme == "dark":
            self.colors = {
                "bg": "#1E1E1E",
                "card": "#2C2C2C",
                "sidebar": "#252526",
                "text": "#EAEAEA",
                "accent": "#4FC3F7"
            }
        else:
            self.colors = {
                "bg": "#F0F2F5",
                "card": "#FFFFFF",
                "sidebar": "#E0E0E0",
                "text": "#000000",
                "accent": "#4CAF50"
            }

        self.root.configure(bg=self.colors["bg"])

    def build_layout(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], width=230)
        self.sidebar.pack(side="left", fill="y")

        self.main = tk.Frame(self.root, bg=self.colors["bg"])
        self.main.pack(side="right", fill="both", expand=True)

        self.build_sidebar()

    def build_sidebar(self):
        def nav_btn(text, cmd):
            return tk.Button(
                self.sidebar,
                text=text,
                bg=self.colors["sidebar"],
                fg=self.colors["text"],
                font=("Helvetica", 12),
                relief="flat",
                anchor="w",
                padx=20,
                command=cmd
            )

        tk.Label(
            self.sidebar,
            text=f"👑 {self.user['name']}",
            bg=self.colors["sidebar"],
            fg=self.colors["accent"],
            font=("Helvetica", 14, "bold")
        ).pack(pady=25)

        nav_btn("Dashboard", self.show_dashboard).pack(fill="x", pady=5)
        nav_btn("Add Doctor", self.show_add_doctor).pack(fill="x", pady=5)
        nav_btn("View Doctors", self.show_doctors).pack(fill="x", pady=5)

        tk.Button(
            self.sidebar,
            text="Toggle Theme",
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            relief="flat",
            command=self.toggle_theme
        ).pack(fill="x", pady=20)

        nav_btn("Logout", self.logout).pack(fill="x", pady=5)

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def generate_password(self, length=8):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def show_dashboard(self):
        self.clear_main()

        card = tk.Frame(self.main, bg=self.colors["card"], padx=40, pady=40)
        card.pack(padx=60, pady=60)

        tk.Label(
            card,
            text="Administrator Dashboard",
            font=("Helvetica", 22, "bold"),
            bg=self.colors["card"],
            fg=self.colors["accent"]
        ).pack(pady=10)

        tk.Label(
            card,
            text="Manage doctors and system data.",
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Helvetica", 13)
        ).pack()

    def show_add_doctor(self):
        self.clear_main()

        card = tk.Frame(
            self.main,
            bg=self.colors["card"],
            padx=60,
            pady=40
        )
        card.pack(padx=120, pady=60, fill="x")

        tk.Label(
            card,
            text=" Add New Doctor",
            font=("Helvetica", 22, "bold"),
            bg=self.colors["card"],
            fg=self.colors["accent"]
        ).pack(pady=(0, 30))

        tk.Label(card, text="Full Name",
                bg=self.colors["card"],
                fg=self.colors["text"],
                anchor="w").pack(fill="x")

        name_entry = tk.Entry(card, font=("Helvetica", 12))
        name_entry.pack(fill="x", pady=5)

        tk.Label(card, text="Username",
                bg=self.colors["card"],
                fg=self.colors["text"],
                anchor="w").pack(fill="x")

        username_entry = tk.Entry(card, font=("Helvetica", 12))
        username_entry.pack(fill="x", pady=5)

        tk.Label(card, text="License Number",
                bg=self.colors["card"],
                fg=self.colors["text"],
                anchor="w").pack(fill="x")

        license_entry = tk.Entry(card, font=("Helvetica", 12))
        license_entry.pack(fill="x", pady=5)

        tk.Label(card, text="Specialties",
                bg=self.colors["card"],
                fg=self.colors["text"],
                anchor="w").pack(fill="x", pady=(15, 5))

        specialties = AdminDAO.get_specialties()

        specialty_names = [f"{s['id']} - {s['name']}" for s in specialties]

        specialty_var = tk.StringVar()

        combo = ttk.Combobox(
            card,
            textvariable=specialty_var,
            values=specialty_names,
            state="readonly",
            font=("Helvetica", 11)
        )

        combo.pack(fill="x", pady=5)
        combo.set("Select Specialty")

        selected_specialties = []

        selected_frame = tk.Frame(card, bg=self.colors["card"])
        selected_frame.pack(fill="x", pady=10)

        def add_specialty():
            value = specialty_var.get()
            if value == "Select Specialty":
                return

            specialty_id = int(value.split(" - ")[0])

            if specialty_id not in selected_specialties:
                selected_specialties.append(specialty_id)

                badge = tk.Label(
                    selected_frame,
                    text=value.split(" - ")[1],
                    bg=self.colors["accent"],
                    fg="white",
                    padx=10,
                    pady=5
                )
                badge.pack(side="left", padx=5)

        tk.Button(
            card,
            text="Add Specialty ",
            bg=self.colors["accent"],
            fg="white",
            command=add_specialty
        ).pack(pady=5)

        def create_doctor():
            name = name_entry.get()
            username = username_entry.get()
            license_number = license_entry.get()

            if not name or not username:
                messagebox.showwarning("Error", "All fields required")
                return

            password = self.generate_password()

            success, msg = AdminDAO.add_doctor(
                name,
                username,
                password,
                license_number,
                selected_specialties
            )

            if success:
                messagebox.showinfo(
                    "Doctor Created",
                    f"Doctor created successfully\n\nUsername: {username}\nPassword: {password}"
                )
                self.show_doctors()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            card,
            text=" Create Doctor",
            bg="#2E7D32",
            fg="white",
            font=("Helvetica", 13, "bold"),
            command=create_doctor
        ).pack(pady=20, fill="x")

    def reactivate_doctor(self, doctor_id):
        if messagebox.askyesno("Confirm", "Reactivate this doctor?"):
            success, msg = AdminDAO.reactivate_doctor(doctor_id)

            if success:
                self.show_doctors()
            else:
                messagebox.showerror("Error", msg)
    def show_doctors(self):
        self.clear_main()

        search_var = tk.StringVar()

        search_frame = tk.Frame(self.main, bg=self.colors["bg"])
        search_frame.pack(fill="x", padx=40, pady=10)

        tk.Label(
            search_frame,
            text="Search Doctor:",
            bg=self.colors["bg"],
            fg=self.colors["text"]
        ).pack(side="left")

        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=10)

        def apply_search():
            load_doctors()

        tk.Button(
            search_frame,
            text=" Search",
            bg=self.colors["accent"],
            fg="white",
            command=apply_search
        ).pack(side="left", padx=5)

        def reset_search():
            search_var.set("")
            load_doctors()

        tk.Button(
            search_frame,
            text="♻ Reset",
            bg="gray",
            fg="white",
            command=reset_search
        ).pack(side="left", padx=5)

        doctors_container = tk.Frame(self.main, bg=self.colors["bg"])
        doctors_container.pack(fill="both", expand=True)

        all_doctors = AdminDAO.get_doctors()

        def load_doctors():
            for w in doctors_container.winfo_children():
                w.destroy()

            keyword = search_var.get().strip().lower()

            if keyword == "":
                filtered = all_doctors
            else:
                filtered = [
                    doc for doc in all_doctors
                    if keyword in doc["name"].lower()
                    or keyword in doc["username"].lower()
                    or keyword == str(doc["id"])
                ]

            if not filtered:
                tk.Label(
                    doctors_container,
                    text="No doctors found",
                    bg=self.colors["bg"],
                    fg="gray",
                    font=("Helvetica", 12)
                ).pack(pady=20)
                return

            for doc in filtered:
                row = tk.Frame(
                    doctors_container,
                    bg=self.colors["card"],
                    pady=10,
                    padx=10
                )
                row.pack(fill="x", padx=40, pady=5)

                status_color = "green" if doc["status"] == "active" else "red"

                tk.Label(
                    row,
                    text=f"Dr {doc['name']} ({doc['username']})",
                    bg=self.colors["card"],
                    fg=self.colors["text"],
                    font=("Helvetica", 12, "bold")
                ).pack(side="left")

                tk.Label(
                    row,
                    text=doc["status"],
                    bg=self.colors["card"],
                    fg=status_color
                ).pack(side="left", padx=20)

                if doc["status"] == "active":
                    tk.Button(
                        row,
                        text="Deactivate",
                        bg="#E53935",
                        fg="white",
                        command=lambda d_id=doc["id"]: self.deactivate_doctor(d_id)
                    ).pack(side="right", padx=5)
                else:
                    tk.Button(
                        row,
                        text="Reactivate",
                        bg="#2E7D32",
                        fg="white",
                        command=lambda d_id=doc["id"]: self.reactivate_doctor(d_id)
                    ).pack(side="right", padx=5)

        load_doctors()
    def deactivate_doctor(self, doctor_id):
        if messagebox.askyesno("Confirm", "Deactivate this doctor?"):
            success, msg = AdminDAO.deactivate_doctor(doctor_id)
            if success:
                self.show_doctors()
            else:
                messagebox.showerror("Error", msg)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()
        self.build_layout()
        self.show_dashboard()

    def logout(self):
        self.root.destroy()