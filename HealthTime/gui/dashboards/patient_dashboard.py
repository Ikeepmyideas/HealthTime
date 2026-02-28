import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from dao.appointment_dao import AppointmentDAO
from dao.admin_dao import AdminDAO
from dao.user_dao import UserDAO
from datetime import timedelta

class PatientDashboard:
    def __init__(self, root, user, theme="light"):
        self.root = root
        self.user = user
        self.theme = theme
        self.dao = AppointmentDAO()
        self.week_offset = 0

        self.root.title("HealthTime - Patient")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 600)

        self.apply_theme()
        self.build_layout()
        self.show_dashboard()
        self.check_appointment_reminder()

    def apply_theme(self):
        if self.theme == "dark":
            self.colors = {
                "bg": "#1E1E1E",
                "card": "#2C2C2C",
                "sidebar": "#252526",
                "text": "#EAEAEA",
                "accent": "#4FC3F7",
                "disabled": "#555555",
                "urgent": "#FF5252" 
            }
        else:
            self.colors = {
                "bg": "#F0F2F5",
                "card": "#FFFFFF",
                "sidebar": "#E0E0E0",
                "text": "#000000",
                "accent": "#4CAF50",
                "disabled": "#C0C0C0",
                "urgent": "#D32F2F" 
            }
        self.root.configure(bg=self.colors["bg"])


    def next_week(self):
        self.week_offset += 1
        self.show_weekly_calendar()

    def previous_week(self):
        self.week_offset -= 1
        self.show_weekly_calendar()

    def build_layout(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.main = tk.Frame(self.root, bg=self.colors["bg"])
        self.main.pack(side="right", fill="both", expand=True)
        self.build_sidebar()

    def build_sidebar(self):
        def nav_btn(text, cmd):
            return tk.Button(
                self.sidebar, text=text, bg=self.colors["sidebar"], fg=self.colors["text"],
                font=("Helvetica", 12), relief="flat", anchor="w", padx=20, command=cmd
            )
        tk.Label(self.sidebar, text=f"👤 {self.user['name']}", bg=self.colors["sidebar"],
                 fg=self.colors["accent"], font=("Helvetica", 14, "bold")).pack(pady=25)
        nav_btn(" Dashboard", self.show_dashboard).pack(fill="x", pady=5)
        nav_btn(" Prendre Rendez-vous", self.show_booking).pack(fill="x", pady=5)
        nav_btn(" Mes Rendez-vous", self.show_appointments).pack(fill="x", pady=5)
        nav_btn(" Calendrier Hebdo", self.show_weekly_calendar).pack(fill="x", pady=5)
        tk.Frame(self.sidebar, height=2, bg=self.colors["bg"]).pack(fill="x", pady=20)
        nav_btn(" Changer Thème", self.toggle_theme).pack(fill="x", pady=5)
        nav_btn(" Déconnexion", self.logout).pack(fill="x", pady=5)

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def show_dashboard(self):
        self.clear_main()
        card = tk.Frame(self.main, bg=self.colors["card"], padx=40, pady=40)
        card.pack(padx=50, pady=50)
        tk.Label(card, text=f"Bienvenue, {self.user['name']}", font=("Helvetica", 22, "bold"),
                 bg=self.colors["card"], fg=self.colors["accent"]).pack(pady=10)
        tk.Label(card, text="Gérez vos rendez-vous médicaux en toute simplicité.\nSélectionnez une option dans le menu de gauche.",
                 font=("Helvetica", 13), bg=self.colors["card"], fg=self.colors["text"], justify="center").pack()

    def show_booking(self, appointment=None):
        self.clear_main()
        card = tk.Frame(self.main, bg=self.colors["card"], padx=25, pady=25)
        card.pack(fill="both", expand=True, padx=40, pady=20)

        title = "Modifier mon rendez-vous" if appointment else "Prendre un nouveau rendez-vous"
        tk.Label(card, text=title, font=("Helvetica", 18, "bold"), bg=self.colors["card"], fg=self.colors["accent"]).pack(pady=(0, 20))

        tk.Label(card, text="1. Quelle spécialité recherchez-vous ?", bg=self.colors["card"], fg=self.colors["text"], font=("Helvetica", 11, "bold")).pack(anchor="w")
        specialties = AdminDAO.get_specialties()
        self.spec_map = {s["name"]: s["id"] for s in specialties}
        
        self.spec_combo = ttk.Combobox(card, state="readonly", values=list(self.spec_map.keys()), font=("Helvetica", 10))
        self.spec_combo.pack(fill="x", pady=(5, 15))
        self.spec_combo.bind("<<ComboboxSelected>>", self.on_specialty_selected)

        tk.Label(card, text="2. Choisissez un praticien spécifique", bg=self.colors["card"], fg=self.colors["text"], font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.doc_combo = ttk.Combobox(card, state="disabled", font=("Helvetica", 10))
        self.doc_combo.pack(fill="x", pady=(5, 15))
        self.doc_combo.set("Sélectionnez d'abord une spécialité")

        config_frame = tk.Frame(card, bg=self.colors["card"])
        config_frame.pack(fill="x", pady=10)
        
        cal_container = tk.Frame(config_frame, bg=self.colors["card"])
        cal_container.pack(side="left")
        tk.Label(cal_container, text="3. Choisissez une date", bg=self.colors["card"], font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.cal = Calendar(cal_container, selectmode="day", date_pattern="yyyy-mm-dd", mindate=datetime.today())
        self.cal.pack(pady=5)

        opt_container = tk.Frame(config_frame, bg=self.colors["card"], padx=30)
        opt_container.pack(side="left", fill="y", pady=20)
        
        self.urgent_var = tk.BooleanVar(value=False)
        tk.Checkbutton(opt_container, text="⚡ C'est une urgence", variable=self.urgent_var, 
                       bg=self.colors["card"], fg=self.colors["urgent"], font=("Helvetica", 12, "bold"),
                       activebackground=self.colors["card"]).pack(anchor="w")
        tk.Label(opt_container, text="Les rendez-vous urgents sont prioritaires\ndans l'agenda du médecin.", 
                 bg=self.colors["card"], fg="gray", font=("Helvetica", 9, "italic"), justify="left").pack(anchor="w", pady=5)

        tk.Button(card, text="Rechercher des créneaux disponibles", bg=self.colors["accent"], fg="white",
                  command=lambda: self.show_slots(card, appointment), font=("Helvetica", 11, "bold"), pady=10).pack(pady=20)

        self.slots_container = tk.Frame(card, bg=self.colors["card"])
        self.slots_container.pack(fill="both", expand=True)


    def on_specialty_selected(self, event):
        spec_name = self.spec_combo.get()
        spec_id = self.spec_map[spec_name]
        
        doctors = UserDAO.search_doctors_by_specialty(spec_id)
        self.doctor_map = {d["name"]: d["id"] for d in doctors}
        
        doc_options = ["Peu importe (Premier disponible)"] + list(self.doctor_map.keys())
        self.doc_combo.config(state="readonly", values=doc_options)
        self.doc_combo.current(0)

    def show_slots(self, parent, appointment):
        for w in self.slots_container.winfo_children():
            w.destroy()

        spec_name = self.spec_combo.get()
        if not spec_name:
            messagebox.showwarning("Attention", "Veuillez choisir une spécialité")
            return

        doc_choice = self.doc_combo.get()
        date_str = self.cal.get_date()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        spec_id = self.spec_map[spec_name]

        if doc_choice == "Peu importe (Premier disponible)":
            available_slots = self.dao.get_available_slots_by_specialty(spec_id, date_obj)
            doctor_id = "any"
        else:
            doctor_id = self.doctor_map.get(doc_choice)
            available_slots = self.dao.get_available_slots_for_doctor(doctor_id, date_obj)

        now = datetime.now()
        if date_obj == now.date():
            current_time = now.strftime("%H:%M")
            available_slots = [
                s for s in available_slots 
                if (s["time"] if isinstance(s, dict) else s) > current_time
            ]

        if not available_slots:
            tk.Label(self.slots_container, text="Aucun créneau disponible pour cette sélection.", 
                     bg=self.colors["card"], fg=self.colors["urgent"], font=("Helvetica", 11, "bold")).pack(pady=10)
            return

        tk.Label(self.slots_container, text="Sélectionnez un horaire :", bg=self.colors["card"], font=("Helvetica", 10, "bold")).pack(anchor="w")
        
        grid_frame = tk.Frame(self.slots_container, bg=self.colors["card"])
        grid_frame.pack(pady=10, fill="x")

        for i, slot_data in enumerate(available_slots):
            if isinstance(slot_data, dict):
                slot_time = slot_data["time"]
                current_doc_id = slot_data["doctor_id"]
                btn_text = f"{slot_time}\n(Dr {slot_data['doctor_name']})"
            else:
                slot_time = slot_data
                current_doc_id = doctor_id
                btn_text = slot_time

            tk.Button(grid_frame, text=btn_text, width=15, height=2, bg=self.colors["accent"], fg="white", relief="flat",
                      font=("Helvetica", 9), command=lambda t=slot_time, d=current_doc_id: self.book_slot(d, date_obj, t, appointment)).grid(row=i//4, column=i%4, padx=5, pady=5)

    def book_slot(self, doctor_id, date, time, appointment):
        now = datetime.now()
        if date < now.date() or (date == now.date() and time <= now.strftime("%H:%M")):
            messagebox.showerror("Erreur", "Vous ne pouvez pas réserver un créneau déjà passé.")
            return

        is_urgent = self.urgent_var.get()
        if appointment:
            success, msg = self.dao.modify_appointment(appointment["id"], doctor_id, date, time, urgent=is_urgent)
        else:
            success, msg = self.dao.create_appointment(self.user["id"], doctor_id, date, time, urgent=is_urgent)

        if success:
            messagebox.showinfo("Succès", "Rendez-vous enregistré !")
            self.show_appointments()
        else:
            messagebox.showerror("Erreur", msg)


    def show_appointments(self):
        self.clear_main()

        self.filter_doctor = tk.StringVar(value="All")
        self.filter_status = tk.StringVar(value="All")
        self.filter_order = tk.StringVar(value="Newest")

        appointments = self.dao.get_patient_appointments(self.user["id"])
        doctor_list = sorted({a["doctor_name"] for a in appointments}) if appointments else []
        
        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(
            container,
            text="My Appointments",
            font=("Helvetica", 20, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        ).pack(anchor="w", pady=(0, 15))

        filter_bar = tk.Frame(container, bg=self.colors["card"], padx=15, pady=10)
        filter_bar.pack(fill="x", pady=(0, 20))

        tk.Label(filter_bar, text="Doctor", bg=self.colors["card"]).pack(side="left", padx=5)
        self.doctor_filter_combo = ttk.Combobox(
                filter_bar,
                state="readonly",
                width=18,
                textvariable=self.filter_doctor,
                values=["All"] + doctor_list 
            )
        self.doctor_filter_combo.pack(side="left", padx=5)
            
        self.doctor_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_appointments())

        tk.Label(filter_bar, text="Status", bg=self.colors["card"]).pack(side="left", padx=(20, 5))

        self.status_combo = ttk.Combobox(
            filter_bar,
            state="readonly",
            width=15,
            values=["All", "Upcoming", "Past", "Canceled"],
            textvariable=self.filter_status
        )
        self.status_combo.pack(side="left")
        self.status_combo.current(0)
        self.status_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.refresh_appointments()
        )

        tk.Label(filter_bar, text="Order", bg=self.colors["card"]).pack(side="left", padx=(20, 5))

        self.order_combo = ttk.Combobox(
            filter_bar,
            state="readonly",
            width=15,
            values=["Newest", "Oldest"],
            textvariable=self.filter_order
        )
        self.order_combo.pack(side="left")
        self.order_combo.current(0)
        self.order_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.refresh_appointments()
        )

        ttk.Button(
            filter_bar,
            text="🔄 Reset",
            command=self.show_appointments
        ).pack(side="right")

        self.cards_container = tk.Frame(container, bg=self.colors["bg"])
        self.cards_container.pack(fill="both", expand=True)

        self.refresh_appointments()


    def cancel_appointment(self, appt_id):
        if not messagebox.askyesno("Confirm", "Cancel this appointment?"):
            return
        self.dao.cancel_appointment(appt_id, self.user["id"])
        self.show_appointments()

    def check_appointment_reminder(self):
        upcoming = self.dao.get_upcoming_appointments(self.user["id"], hours=24)
        if upcoming:
            msg = "Appointment Reminder\n\n"
            for a in upcoming:
                msg += f"Tomorrow at {a['time']} with Dr {a['doctor_name']}\n"
            messagebox.showinfo("Reminder", msg)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()
        self.build_layout()
        self.show_dashboard()

    def refresh_appointments(self, event=None):  
        for w in self.cards_container.winfo_children():
            w.destroy()

        appointments = self.dao.get_patient_appointments(self.user["id"])
        if not appointments:
            self._show_empty_message("No appointments found")
            return

        now = datetime.now()
        
        target_doctor = self.filter_doctor.get()
        target_status = self.filter_status.get()
        target_order = self.filter_order.get()

        filtered = []

        for a in appointments:
            try:
                date_str = str(a["date"]).strip()
                time_str = str(a["time"]).strip()
                if len(time_str) > 5: 
                    time_str = time_str[:5]
                
                appt_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except Exception as e:
                print(f"DEBUG: Error parsing date for appt {a.get('id')}: {e}")
                continue

            status_db = str(a.get("status", "")).lower().strip()
            is_canceled = status_db in ("canceled", "cancelled", "cancel")
            is_past = appt_dt < now and not is_canceled
            is_upcoming = appt_dt >= now and not is_canceled

            if target_doctor != "All" and a["doctor_name"] != target_doctor:
                continue

            if target_status == "Canceled" and not is_canceled:
                continue
            elif target_status == "Past" and not is_past:
                continue
            elif target_status == "Upcoming" and not is_upcoming:
                continue

            a["_datetime"] = appt_dt
            a["_is_future"] = (appt_dt >= now)
            a["_is_canceled"] = is_canceled
            filtered.append(a)

        reverse_sort = (target_order == "Newest")
        filtered.sort(key=lambda x: x["_datetime"], reverse=reverse_sort)

        if not filtered:
            self._show_empty_message(f"No {target_status.lower()} appointments found")
        else:
            for a in filtered:
                self.render_appointment_card(a)

    def _show_empty_message(self, message):
        tk.Label(
            self.cards_container, text=message, bg=self.colors["bg"],
            fg="#888", font=("Helvetica", 12, "italic")
        ).pack(pady=40)

    def _update_doctor_filter_options(self, appointments):
        doctors = sorted({a["doctor_name"] for a in appointments})
        self.doctor_filter_combo["values"] = ["All"] + doctors
        if self.filter_doctor.get() not in self.doctor_filter_combo["values"]:
            self.filter_doctor.set("All")

    def render_appointment_card(self, a):
        card = tk.Frame(
            self.cards_container,
            bg=self.colors["card"],
            padx=20,
            pady=15,
            highlightthickness=1,
            highlightbackground=self.colors["accent"]
        )
        card.pack(fill="x", pady=8)

        left = tk.Frame(card, bg=self.colors["card"])
        left.pack(side="left", fill="both", expand=True)

        tk.Label(
            left,
            text=f"Dr {a['doctor_name']}",
            font=("Helvetica", 14, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(anchor="w")

        tk.Label(
            left,
            text=f"{a['date']} at {a['time']}",
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(anchor="w", pady=(2, 5))

        if a["_is_canceled"]:
            status_text = "Canceled"
            status_color = "#E53935"
        elif a["_is_future"]:
            status_text = "Upcoming"
            status_color = "#4CAF50"
        else:
            status_text = "Past"
            status_color = "#888888"

        tk.Label(
            left,
            text=status_text,
            fg=status_color,
            bg=self.colors["card"],
            font=("Helvetica", 10, "bold")
        ).pack(anchor="w")

        right = tk.Frame(card, bg=self.colors["card"])
        right.pack(side="right")

        if a["_is_future"] and not a["_is_canceled"]:
            tk.Button(
                right,
                text="✏ Modify",
                bg=self.colors["accent"],
                fg="white",
                relief="flat",
                command=lambda appt=a: self.show_booking(appt)
            ).pack(pady=2)

            tk.Button(
                right,
                text=" Cancel",
                bg="#E53935",
                fg="white",
                relief="flat",
                command=lambda appt_id=a["id"]: self.cancel_appointment(appt_id)
            ).pack(pady=2)



    def show_weekly_calendar(self):
        self.clear_main()

        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=30, pady=20)

        header = tk.Frame(container, bg=self.colors["bg"])
        header.pack(fill="x", pady=(0, 10))

        tk.Button(
            header,
            text="⬅",
            font=("Helvetica", 14),
            command=self.previous_week
        ).pack(side="left")

        tk.Label(
            header,
            text="My Weekly Calendar",
            font=("Helvetica", 20, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        ).pack(side="left", expand=True)

        tk.Button(
            header,
            text="➡",
            font=("Helvetica", 14),
            command=self.next_week
        ).pack(side="right")

        today = datetime.today().date()
        monday = today - timedelta(days=today.weekday())
        monday += timedelta(weeks=self.week_offset)

        week_dates = [monday + timedelta(days=i) for i in range(7)]

        tk.Label(
            container,
            text=f"{week_dates[0]}  →  {week_dates[-1]}",
            bg=self.colors["bg"],
            fg=self.colors["text"]
        ).pack(pady=(0, 15))

        appointments = self.dao.get_patient_appointments(self.user["id"])

        appt_map = {}
        for a in appointments:
            date_obj = datetime.strptime(a["date"], "%Y-%m-%d").date()
            hour = int(a["time"][:2])
            appt_map[(date_obj, hour)] = a

        table = tk.Frame(container, bg=self.colors["card"])
        table.pack()

        tk.Label(table, text="Time", width=10, bg=self.colors["card"]).grid(row=0, column=0)

        for i, d in enumerate(week_dates):
            tk.Label(
                table,
                text=d.strftime("%a\n%d %b"),
                width=12,
                bg=self.colors["card"]
            ).grid(row=0, column=i+1)

        for hour in range(8, 19):
            tk.Label(
                table,
                text=f"{hour:02d}:00",
                bg=self.colors["card"]
            ).grid(row=hour-7, column=0)

            for col, date in enumerate(week_dates):
                key = (date, hour)

                if key in appt_map:
                    a = appt_map[key]
                    status = a["status"].lower()

                    if "cancel" in status:
                        color = "#E53935"
                    else:
                        color = "#4CAF50"

                    cell = tk.Frame(
                        table,
                        width=100,
                        height=40,
                        bg=color,
                        relief="solid",
                        borderwidth=1
                    )
                    cell.grid(row=hour-7, column=col+1, padx=2, pady=2)

                    cell.bind(
                        "<Button-1>",
                        lambda e, appt=a: self.show_patient_appointment_details(appt)
                    )

                    cell.config(cursor="hand2")

                else:
                    cell = tk.Frame(
                        table,
                        width=100,
                        height=40,
                        bg="white",
                        relief="solid",
                        borderwidth=1
                    )
                    cell.grid(row=hour-7, column=col+1, padx=2, pady=2)

    def show_patient_appointment_details(self, appointment):

        popup = tk.Toplevel(self.root)
        popup.title("Appointment Details")
        popup.geometry("350x250")

        tk.Label(
            popup,
            text="Appointment Details",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        tk.Label(
            popup,
            text=f"Doctor: Dr {appointment['doctor_name']}"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Date: {appointment['date']}"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Time: {appointment['time']}"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Status: {appointment['status']}"
        ).pack(pady=5)

    def logout(self):
        self.root.destroy()


