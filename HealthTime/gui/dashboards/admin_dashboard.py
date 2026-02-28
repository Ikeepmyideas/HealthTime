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
        self.root.geometry("1100x700")
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
                font=("Helvetica", 11),
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

        nav_btn("Dashboard", self.show_dashboard).pack(fill="x", pady=2)
        nav_btn("Utilisateurs", self.show_users).pack(fill="x", pady=2)
        nav_btn("Docteurs", self.show_doctors).pack(fill="x", pady=2)
        nav_btn("Ajout Docteur", self.show_add_doctor).pack(fill="x", pady=2)
        nav_btn("Specialites", self.show_specialties).pack(fill="x", pady=2)

        tk.Frame(self.sidebar, height=2, bg=self.colors["bg"]).pack(fill="x", pady=15)

        tk.Button(
            self.sidebar,
            text="Dark Mode",
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            relief="flat",
            command=self.toggle_theme
        ).pack(fill="x", pady=5)

        nav_btn("Déconnexion", self.logout).pack(fill="x", pady=5)

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def generate_password(self, length=8):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def _on_mousewheel(self, event, canvas):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def show_dashboard(self):
        self.clear_main()
        
        users = AdminDAO.get_all_users()
        total_users = len(users)
        total_docs = len([u for u in users if u['role'] == 'doctor'])
        total_pats = len([u for u in users if u['role'] == 'patient'])

        tk.Label(
            self.main,
            text="Administrator Overview",
            font=("Helvetica", 22, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        ).pack(pady=30)

        stats_frame = tk.Frame(self.main, bg=self.colors["bg"])
        stats_frame.pack(pady=20)

        def create_stat_card(parent, label, value):
            card = tk.Frame(parent, bg=self.colors["card"], padx=30, pady=20, relief="flat")
            card.pack(side="left", padx=15)
            tk.Label(card, text=value, font=("Helvetica", 24, "bold"), bg=self.colors["card"], fg=self.colors["accent"]).pack()
            tk.Label(card, text=label, font=("Helvetica", 10), bg=self.colors["card"], fg="gray").pack()

        create_stat_card(stats_frame, "Total Registered", total_users)
        create_stat_card(stats_frame, "Active Doctors", total_docs)
        create_stat_card(stats_frame, "Active Patients", total_pats)

    def show_users(self):
        self.clear_main()
        tk.Label(self.main, text="System Users Management", font=("Helvetica", 18, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=20)

        users = AdminDAO.get_all_users()
        
        list_outer = tk.Frame(self.main, bg=self.colors["bg"])
        list_outer.pack(fill="both", expand=True, padx=40, pady=10)

        canvas = tk.Canvas(list_outer, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        def update_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", update_width)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))

        for u in users:
            row = tk.Frame(scroll_frame, bg=self.colors["card"], pady=10, padx=15)
            row.pack(fill="x", pady=5)

            role_color = "#2196F3" if u['role'] == 'patient' else "#9C27B0" if u['role'] == 'doctor' else "#FF9800"
            
            tk.Label(row, text=u['role'].upper(), font=("Helvetica", 8, "bold"), bg=role_color, fg="white", padx=5).pack(side="left")
            tk.Label(row, text=f"{u['name']} (@{u['username']})", font=("Helvetica", 11), 
                     bg=self.colors["card"], fg=self.colors["text"]).pack(side="left", padx=15)

            status_btn_text = "Deactivate" if u['status'] == 'active' else "Activate"
            status_btn_bg = "#E53935" if u['status'] == 'active' else "#2E7D32"
            
            if u['id'] != self.user['id']:
                tk.Button(row, text=status_btn_text, bg=status_btn_bg, fg="white", relief="flat", padx=10,
                          command=lambda uid=u['id'], st=u['status']: self.toggle_user_status(uid, st)).pack(side="right")
            
            tk.Label(row, text=u['status'], fg=status_btn_bg, bg=self.colors["card"], padx=10).pack(side="right")

    def toggle_user_status(self, user_id, current_status):
        success, msg = AdminDAO.toggle_user_status(user_id, current_status)
        if success:
            self.show_users()
        else:
            messagebox.showerror("Error", msg)

    def show_specialties(self):
        self.clear_main()
        tk.Label(self.main, text="Medical Specialties Management", font=("Helvetica", 18, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=20)

        add_frame = tk.Frame(self.main, bg=self.colors["card"], padx=20, pady=20)
        add_frame.pack(fill="x", padx=40, pady=10)

        tk.Label(add_frame, text="New Specialty:", bg=self.colors["card"], fg=self.colors["text"]).pack(side="left")
        name_entry = tk.Entry(add_frame, font=("Helvetica", 12))
        name_entry.pack(side="left", padx=10, fill="x", expand=True)

        def add_spec():
            name = name_entry.get().strip()
            if not name: return
            success, msg = AdminDAO.add_specialty(name)
            if success:
                self.show_specialties()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(add_frame, text="Add Specialty", bg=self.colors["accent"], fg="white", command=add_spec).pack(side="left")

        list_outer = tk.Frame(self.main, bg=self.colors["bg"])
        list_outer.pack(fill="both", expand=True, padx=40, pady=10)

        canvas = tk.Canvas(list_outer, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        def update_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", update_width)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))

        specs = AdminDAO.get_specialties()
        for s in specs:
            row = tk.Frame(scroll_frame, bg=self.colors["card"], pady=10, padx=15)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=s['name'], bg=self.colors["card"], fg=self.colors["text"], font=("Helvetica", 11)).pack(side="left")
            tk.Button(row, text="Delete", bg="#FFCDD2", fg="#B71C1C", relief="flat", padx=10,
                      command=lambda sid=s['id']: self.delete_specialty(sid)).pack(side="right")

    def delete_specialty(self, sid):
        if messagebox.askyesno("Confirm", "Delete this specialty? It might be linked to doctors."):
            success, msg = AdminDAO.delete_specialty(sid)
            if not success:
                messagebox.showwarning("Warning", msg)
            self.show_specialties()

    def show_add_doctor(self):
        self.clear_main()

        card = tk.Frame(self.main, bg=self.colors["card"], padx=60, pady=40)
        card.pack(padx=120, pady=40, fill="x")

        tk.Label(card, text="Register New Professional", font=("Helvetica", 22, "bold"), 
                 bg=self.colors["card"], fg=self.colors["accent"]).pack(pady=(0, 30))

        def create_field(parent, label):
            tk.Label(parent, text=label, bg=self.colors["card"], fg=self.colors["text"], anchor="w").pack(fill="x")
            entry = tk.Entry(parent, font=("Helvetica", 12))
            entry.pack(fill="x", pady=(5, 15))
            return entry

        name_entry = create_field(card, "Nom Complet")
        username_entry = create_field(card, "Username")
        license_entry = create_field(card, "License Number")

        tk.Label(card, text="Specialites", bg=self.colors["card"], fg=self.colors["text"], anchor="w").pack(fill="x")
        
        specialties = AdminDAO.get_specialties()
        specialty_names = [f"{s['id']} - {s['name']}" for s in specialties]
        specialty_var = tk.StringVar()
        
        combo_frame = tk.Frame(card, bg=self.colors["card"])
        combo_frame.pack(fill="x", pady=5)

        combo = ttk.Combobox(combo_frame, textvariable=specialty_var, values=specialty_names, state="readonly")
        combo.pack(side="left", fill="x", expand=True)
        combo.set("Select to add")

        selected_specialties = []
        badge_frame = tk.Frame(card, bg=self.colors["card"])
        badge_frame.pack(fill="x", pady=10)

        def add_spec_to_list():
            val = specialty_var.get()
            if val == "Select to add": return
            s_id = int(val.split(" - ")[0])
            if s_id not in selected_specialties:
                selected_specialties.append(s_id)
                tk.Label(badge_frame, text=val.split(" - ")[1], bg=self.colors["accent"], fg="white", 
                         padx=8, pady=3, font=("Helvetica", 9)).pack(side="left", padx=3)

        tk.Button(combo_frame, text="Add", command=add_spec_to_list, bg="gray", fg="white").pack(side="right", padx=5)

        def create_doctor():
            name, user, lic = name_entry.get(), username_entry.get(), license_entry.get()
            if not name or not user or not lic:
                messagebox.showwarning("Error", "All fields are mandatory")
                return

            password = self.generate_password()
            success, msg = AdminDAO.add_doctor(name, user, password, lic, selected_specialties)

            if success:
                messagebox.showinfo("Success", f"Doctor Created!\n\nUser: {user}\nPass: {password}")
                self.show_doctors()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(card, text="Save Doctor Account", bg="#2E7D32", fg="white", font=("Helvetica", 12, "bold"), 
                  command=create_doctor).pack(pady=20, fill="x")

    def show_doctors(self):
        self.clear_main()
        
        header = tk.Frame(self.main, bg=self.colors["bg"], padx=40, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="Search Professionals:", bg=self.colors["bg"], fg=self.colors["text"]).pack(side="left")
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(header, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=10)

        list_outer = tk.Frame(self.main, bg=self.colors["bg"])
        list_outer.pack(fill="both", expand=True, padx=40, pady=10)

        canvas = tk.Canvas(list_outer, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        def update_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", update_width)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))

        all_doctors = AdminDAO.get_doctors()

        def render_list():
            for w in scroll_frame.winfo_children(): w.destroy()
            query = search_var.get().lower()
            
            for doc in all_doctors:
                if query and query not in doc['name'].lower() and query not in doc['username'].lower():
                    continue

                row = tk.Frame(scroll_frame, bg=self.colors["card"], pady=10, padx=15)
                row.pack(fill="x", pady=5)

                status_color = "green" if doc["status"] == "active" else "red"
                
                tk.Label(row, text=f"Dr. {doc['name']}", font=("Helvetica", 12, "bold"), bg=self.colors["card"]).pack(side="left")
                tk.Label(row, text=f"(@{doc['username']})", bg=self.colors["card"], fg="gray").pack(side="left", padx=5)
                
                for s in doc.get('specialties', []):
                    tk.Label(row, text=s['name'], font=("Helvetica", 8), bg="#E1F5FE", fg="#0288D1", padx=4).pack(side="left", padx=2)

                btn_text = "Deactivate" if doc["status"] == "active" else "Activate"
                btn_bg = "#E53935" if doc["status"] == "active" else "#2E7D32"
                
                tk.Button(row, text=btn_text, bg=btn_bg, fg="white", relief="flat", padx=10,
                          command=lambda d_id=doc["id"], st=doc["status"]: self.toggle_user_status(d_id, st)).pack(side="right")
                
                tk.Label(row, text=doc["status"], fg=btn_bg, bg=self.colors["card"], padx=15).pack(side="right")

        tk.Button(header, text="Search", bg=self.colors["accent"], fg="white", command=render_list).pack(side="left")
        search_entry.bind("<Return>", lambda e: render_list())
        render_list()

    def deactivate_doctor(self, doctor_id):
        if messagebox.askyesno("Confirm", "Deactivate this doctor?"):
            success, msg = AdminDAO.deactivate_doctor(doctor_id)
            if success:
                self.show_doctors()
            else:
                messagebox.showerror("Error", msg)
    
    def reactivate_doctor(self, doctor_id):
        if messagebox.askyesno("Confirm", "Reactivate this doctor?"):
            success, msg = AdminDAO.reactivate_doctor(doctor_id)

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
