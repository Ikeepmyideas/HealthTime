import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from dao.doctor_dao import DoctorDAO
from datetime import datetime, timedelta
from dao.appointment_dao import AppointmentDAO
calendar.setfirstweekday(calendar.MONDAY)


class DoctorDashboard:
    def __init__(self, root, user, theme="light"):
        self.root = root
        self.user = user
        self.theme = theme

        self.root.title("HealthTime - Doctor")
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
                "accent": "#4FC3F7",
                "urgent": "#f1c40f", 
                "canceled": "#95a5a6"  
            }
        else:
            self.colors = {
                "bg": "#F0F2F5",
                "card": "#FFFFFF",
                "sidebar": "#E0E0E0",
                "text": "#000000",
                "accent": "#4CAF50",
                "urgent": "#f1c40f",
                "canceled": "#95a5a6"
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
            text=f" Dr {self.user['name']}",
            bg=self.colors["sidebar"],
            fg=self.colors["accent"],
            font=("Helvetica", 14, "bold")
        ).pack(pady=25)

        nav_btn("Dashboard", self.show_dashboard).pack(fill="x", pady=5)
        nav_btn("Weekly Planner", self.show_weekly_planner).pack(fill="x", pady=5)
        nav_btn("Ajout de créneaux", self.show_calendar_planner).pack(fill="x", pady=5)
        nav_btn("My Schedule", self.show_schedule).pack(fill="x", pady=5)
        nav_btn("Appointments", self.show_appointments).pack(fill="x", pady=5)

        tk.Button(
            self.sidebar,
            text="Logout",
            bg="red",
            fg="white",
            command=self.logout
        ).pack(fill="x", pady=20)

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def show_dashboard(self):
        self.clear_main()

        card = tk.Frame(self.main, bg=self.colors["card"], padx=50, pady=50)
        card.pack(padx=100, pady=100)

        tk.Label(
            card,
            text="Doctor Dashboard",
            font=("Helvetica", 22, "bold"),
            bg=self.colors["card"],
            fg=self.colors["accent"]
        ).pack()

    def show_create_slot(self):
        self.clear_main()

        card = tk.Frame(self.main, bg=self.colors["card"], padx=60, pady=40)
        card.pack(padx=100, pady=60, fill="x")

        tk.Label(card,
                 text="Create Available Time Slot",
                 font=("Helvetica", 18, "bold"),
                 bg=self.colors["card"]).pack(pady=10)

        tk.Label(card, text="Start (YYYY-MM-DD HH:MM)",
                 bg=self.colors["card"]).pack(anchor="w")

        start_entry = tk.Entry(card, width=40)
        start_entry.pack(pady=5)

        tk.Label(card, text="End (YYYY-MM-DD HH:MM)",
                 bg=self.colors["card"]).pack(anchor="w")

        end_entry = tk.Entry(card, width=40)
        end_entry.pack(pady=5)

        def create_slot():
            start = start_entry.get()
            end = end_entry.get()

            if not start or not end:
                messagebox.showwarning("Error", "All fields required")
                return

            success, msg = DoctorDAO.create_time_slot(
                self.user["id"], start, end
            )

            if success:
                messagebox.showinfo("Success", msg)
                start_entry.delete(0, tk.END)
                end_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", msg)

        tk.Button(
            card,
            text="Create Slot",
            bg=self.colors["accent"],
            fg="white",
            command=create_slot
        ).pack(pady=15)

    def show_calendar_planner(self):
        """Vue permettant de créer massivement des créneaux de disponibilité jusqu'à 22h"""
        self.clear_main()
        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(container, text="Créer des Disponibilités", font=("Helvetica", 18, "bold"), bg=self.colors["bg"]).pack(pady=10)

        top_frame = tk.Frame(container, bg=self.colors["bg"])
        top_frame.pack(pady=10)

        month_var = tk.StringVar(value=str(datetime.today().month))
        year_var = tk.StringVar(value=str(datetime.today().year))

        tk.Label(top_frame, text="Month", bg=self.colors["bg"]).pack(side="left")
        month_combo = ttk.Combobox(top_frame, textvariable=month_var, values=list(range(1, 13)), width=5, state="readonly")
        month_combo.pack(side="left", padx=5)

        tk.Label(top_frame, text="Year", bg=self.colors["bg"]).pack(side="left")
        year_combo = ttk.Combobox(top_frame, textvariable=year_var, values=list(range(2024, 2035)), width=7, state="readonly")
        year_combo.pack(side="left", padx=5)

        days_frame = tk.Frame(container, bg=self.colors["bg"])
        days_frame.pack(pady=20)

        selected_days = set()

        def toggle_day(day, btn):
            if day in selected_days:
                selected_days.remove(day)
                btn.config(bg="white")
            else:
                selected_days.add(day)
                btn.config(bg="#4CAF50")

        def render_calendar(event=None):
            """Rend le calendrier de manière fiable en lisant directement les widgets"""
            for widget in days_frame.winfo_children(): 
                widget.destroy()
            selected_days.clear()
            
            try:
                year = int(year_combo.get())
                month = int(month_combo.get())
            except (ValueError, tk.TclError):
                return

            today_date = datetime.today().date()
            cal = calendar.monthcalendar(year, month)
            days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

            # En-têtes de colonnes
            for col, name in enumerate(days_names):
                tk.Label(days_frame, text=name, bg=self.colors["accent"], fg="white", width=6, height=2).grid(row=0, column=col, padx=2, pady=2)

            # Rendu des boutons de jours
            for r, week in enumerate(cal):
                for c, day in enumerate(week):
                    if day == 0:
                        tk.Label(days_frame, text="", width=6, height=2, bg=self.colors["bg"]).grid(row=r+1, column=c)
                        continue
                    
                    # Vérifier si le jour est passé
                    current_date = datetime(year, month, day).date()
                    is_past = current_date < today_date
                    
                    bg_color = "white"
                    fg_color = "black"
                    if current_date == today_date: bg_color = "#BBDEFB"
                    if is_past: 
                        bg_color = "#E0E0E0"
                        fg_color = "#9E9E9E"

                    btn = tk.Button(days_frame, text=str(day), width=6, height=2, bg=bg_color, fg=fg_color, 
                                   state="disabled" if is_past else "normal")
                    btn.grid(row=r+1, column=c, padx=2, pady=2)
                    
                    if not is_past:
                        btn.config(command=lambda d=day, b=btn: toggle_day(d, b))

        month_combo.bind("<<ComboboxSelected>>", render_calendar)
        year_combo.bind("<<ComboboxSelected>>", render_calendar)
        render_calendar()

        hours_frame = tk.Frame(container, bg=self.colors["bg"])
        hours_frame.pack(pady=10)
        selected_hours = set()

        def toggle_hour(h, b):
            if h in selected_hours:
                selected_hours.remove(h)
                b.config(bg="white")
            else:
                selected_hours.add(h)
                b.config(bg="#4CAF50")

        for hour in range(7, 23):
            btn = tk.Button(hours_frame, text=f"{hour}h", width=6, bg="white")
            btn.pack(side="left", padx=2)
            btn.config(command=lambda h=hour, b=btn: toggle_hour(h, b))

        def save():
            if not selected_days or not selected_hours:
                messagebox.showwarning("Attention", "Sélectionnez au moins un jour et une heure.")
                return

            errors = []

            for d in selected_days:
                for h in selected_hours:
                    year = int(year_combo.get())
                    month = int(month_combo.get())

                    date_str = f"{year}-{month:02d}-{d:02d}"
                    success, msg = DoctorDAO.create_time_slot_day_hour(
                        self.user["id"], date_str, h
                    )

                    if not success:
                        errors.append(f"{date_str} {h}h → {msg}")

            if errors:
                messagebox.showerror("Erreur", "\n".join(errors))
            else:
                messagebox.showinfo("Succès", "Disponibilités enregistrées !")

            self.show_weekly_planner()

        tk.Button(
            container,
            text=" Enregistrer les disponibilités",
            bg="#2196F3",
            fg="white",
            font=("Helvetica", 11, "bold"),
            command=save
        ).pack(pady=20)

   


    def show_schedule(self):
        self.clear_main()

        slots = DoctorDAO.get_doctor_slots(self.user["id"])

        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(
            container,
            text="My Schedule",
            font=("Helvetica", 18, "bold"),
            bg=self.colors["bg"]
        ).pack(pady=10)

        if not slots:
            tk.Label(container,
                     text="No time slots created",
                     bg=self.colors["bg"]).pack()
            return

        for slot in slots:

            if slot["status"] == "available":
                color = "green"
            elif slot["status"] == "booked":
                color = "red"
            else:
                color = "gray"

            row = tk.Frame(container, bg=self.colors["card"], pady=10)
            row.pack(fill="x", pady=5)

            tk.Label(
                row,
                text=f"{slot['slot_date']} - {slot['slot_hour']}:00",
                bg=self.colors["card"]
            ).pack(side="left", padx=10)

            tk.Label(
                row,
                text=slot["status"],
                fg=color,
                bg=self.colors["card"]
            ).pack(side="right", padx=20)

    def show_appointments(self):
        """Liste défilante des rendez-vous avec badges d'état"""
        self.clear_main()
        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=20)
        tk.Label(container, text=" My Appointments (List View)", font=("Helvetica", 18, "bold"), bg=self.colors["bg"], fg=self.colors["accent"]).pack(pady=(10, 20), anchor="w")

        appointments = AppointmentDAO.get_doctor_appointments(self.user["id"])

        if not appointments:
            tk.Label(container, text="Aucun rendez-vous trouvé.", bg=self.colors["bg"], fg="gray", font=("Helvetica", 12)).pack(pady=20)
            return

        header_frame = tk.Frame(container, bg=self.colors["sidebar"])
        header_frame.pack(fill="x", pady=5)
        
        tk.Label(header_frame, text="Patient Name", bg=self.colors["sidebar"], fg=self.colors["text"], font=("Helvetica", 11, "bold"), width=20, anchor="w").pack(side="left", padx=10, pady=5)
        tk.Label(header_frame, text="Date & Time", bg=self.colors["sidebar"], fg=self.colors["text"], font=("Helvetica", 11, "bold"), width=25, anchor="w").pack(side="left")
        tk.Label(header_frame, text="Status", bg=self.colors["sidebar"], fg=self.colors["text"], font=("Helvetica", 11, "bold"), width=15, anchor="w").pack(side="left")

        canvas_container = tk.Frame(container, bg=self.colors["bg"])
        canvas_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_container, bg=self.colors["bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        list_frame = tk.Frame(canvas, bg=self.colors["bg"])
        canvas_frame_window = canvas.create_window((0, 0), window=list_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        list_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_frame_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        for appt in appointments:
            row = tk.Frame(list_frame, bg=self.colors["card"], pady=10)
            row.pack(fill="x", pady=5, padx=(0, 5))

            appt_dt = appt["appointment_date"]
            if isinstance(appt_dt, str): appt_dt = datetime.strptime(appt_dt, "%Y-%m-%d %H:%M:%S")
            
            date_str, time_str = appt_dt.strftime("%Y-%m-%d"), appt_dt.strftime("%H:%M")
            status = appt["status"]
            status_color = "#2ecc71" if status.lower() in ["scheduled", "confirmé"] else "#e74c3c"

            tk.Label(row, text=appt["patient_name"], bg=self.colors["card"], font=("Helvetica", 11), width=20, anchor="w").pack(side="left", padx=10)
            tk.Label(row, text=f"🗓️ {date_str} at 🕒 {time_str}", bg=self.colors["card"], width=25, anchor="w").pack(side="left")
            tk.Label(row, text=status.capitalize(), bg=self.colors["card"], fg=status_color, font=("Helvetica", 10, "bold"), width=15, anchor="w").pack(side="left")

            is_future = appt_dt >= datetime.now()
            is_canceled = status.lower() in ["canceled", "canceled_by_doctor", "annulé"]

            if is_future and not is_canceled:
                tk.Button(
                    row, text="Cancel", bg="#e74c3c", fg="white", relief="flat", padx=10,
                    command=lambda a_id=appt["id"]: self.cancel_appointment_from_list(a_id)
                ).pack(side="right", padx=20)
            elif not is_future and not is_canceled:
                tk.Label(row, text="✅ Terminé", bg=self.colors["card"], fg="gray", font=("Helvetica", 10, "italic")).pack(side="right", padx=20)

    def cancel_appointment_from_list(self, appointment_id):
            confirm = messagebox.askyesno(
                "Confirm",
                "Are you sure you want to cancel this appointment?"
            )

            if not confirm:
                return

            success, message = AppointmentDAO.cancel_appointment_by_doctor(appointment_id)

            if success:
                messagebox.showinfo("Success", "Appointment successfully canceled.")
                self.show_appointments()  
            else:
                messagebox.showerror("Error", message)


    def show_weekly_planner(self, week_offset=0):
        """Vue calendrier hebdomadaire corrigée"""
        self.clear_main()

        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        slots = DoctorDAO.get_doctor_slots(self.user["id"])
        appointments = AppointmentDAO.get_doctor_appointments(self.user["id"])

        slot_map = {}
        for s in slots:
            d = s["slot_date"]
            if isinstance(d, str):
                d = datetime.strptime(d, "%Y-%m-%d").date()
            slot_map[(d, int(s["slot_hour"]))] = s["status"]

        urgent_map = {}
        for a in appointments:
            dt = a["appointment_date"]
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            urgent_map[(dt.date(), dt.hour)] = a.get("urgent", False)

        base_date = datetime.today().date()
        monday = base_date - timedelta(days=base_date.weekday()) + timedelta(weeks=week_offset)
        week_dates = [monday + timedelta(days=i) for i in range(7)]

        header = tk.Frame(scroll_frame, bg=self.colors["bg"])
        header.pack(pady=10, fill="x")

        tk.Button(header, text="⬅ Previous",
                command=lambda: self.show_weekly_planner(week_offset - 1)).pack(side="left")

        tk.Label(header,
                text=f"Week of {monday.strftime('%d %B %Y')}",
                font=("Helvetica", 16, "bold"),
                bg=self.colors["bg"]).pack(side="left", expand=True)

        tk.Button(header, text="Next ➡",
                command=lambda: self.show_weekly_planner(week_offset + 1)).pack(side="right")

        # === TABLE ===
        table_container = tk.Frame(scroll_frame, bg=self.colors["bg"])
        table_container.pack(pady=20)

        table = tk.Frame(table_container, bg=self.colors["bg"])
        table.pack(anchor="center")

        days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for col, name in enumerate(days_names):
            tk.Label(
                table,
                text=f"{name}\n{week_dates[col].strftime('%d-%m')}",
                bg=self.colors["accent"],
                fg="white",
                width=14,
                height=2
            ).grid(row=0, column=col + 1, padx=1, pady=1)

        for row_idx, hour in enumerate(range(7, 23)):
            tk.Label(
                table,
                text=f"{hour}:00",
                bg=self.colors["card"],
                width=8
            ).grid(row=row_idx + 1, column=0, padx=1, pady=1)

            for col, current_date in enumerate(week_dates):

                key = (current_date, hour)
                status = slot_map.get(key)   
                is_urgent_val = urgent_map.get(key, False)

                color = "#2c3e50"
                cursor = ""

                if status == "available":
                    color = "#2ecc71"

                elif status == "booked":
                    if is_urgent_val:
                        color = self.colors["urgent"]
                    else:
                        color = "#e74c3c"
                    cursor = "hand2"

                cell = tk.Frame(
                    table,
                    width=90,
                    height=35,
                    bg=color,
                    relief="raised",
                    borderwidth=1
                )
                cell.grid(row=row_idx + 1, column=col + 1, padx=2, pady=2)
                cell.grid_propagate(False)

                if status == "booked":
                    cell.bind(
                        "<Button-1>",
                        lambda e, d=current_date, h=hour, u=is_urgent_val:
                        self.show_appointment_details(d, h, u)
                    )
                    cell.config(cursor=cursor)

        legend = tk.Frame(scroll_frame, bg=self.colors["bg"])
        legend.pack(pady=20, anchor="w")

        tk.Label(legend,
                text="Legend :",
                font=("Helvetica", 12, "bold"),
                bg=self.colors["bg"]).pack(anchor="w")

        legend_items = [
            ("🟢", "Available", "#2ecc71"),
            ("🔴", "Booked", "#e74c3c"),
            ("🟡", "Urgent", "#f1c40f"),
            ("⚫", "Not working", "#2c3e50")
        ]

        for ic, txt, cl in legend_items:
            row = tk.Frame(legend, bg=self.colors["bg"])
            row.pack(anchor="w")
            tk.Label(row, text=ic, bg=self.colors["bg"]).pack(side="left", padx=5)
            tk.Label(row, text=txt, bg=self.colors["bg"]).pack(side="left")

    def show_appointment_details(self, date, hour, is_urgent_from_map=False):
            """Fenêtre de détails avec correction du bug d'urgence et sécurité passé"""
            appointment = AppointmentDAO.get_appointment_by_doctor_date_hour(self.user["id"], date, hour)
            if not appointment: return

            popup = tk.Toplevel(self.root)
            popup.title("Appointment Details")
            popup.geometry("380x350")
            popup.configure(padx=20, pady=20)

            appt_dt = appointment['datetime']
            if isinstance(appt_dt, str): appt_dt = datetime.strptime(appt_dt, "%Y-%m-%d %H:%M:%S")
            
            is_past = appt_dt < datetime.now()
            is_urgent = is_urgent_from_map or appointment.get('urgent', False)

            tk.Label(popup, text="Appointment Details", font=("Helvetica", 14, "bold")).pack(pady=(0, 15))
            
            details = [
                ("Patient", appointment['patient_name']),
                ("Date", appt_dt.strftime('%d/%m/%Y')),
                ("Time", appt_dt.strftime('%H:%M')),
                ("Status", appointment['status']),
                ("Urgence", "⚡ OUI (Prioritaire)" if is_urgent else "Non")
            ]

            for label, val in details:
                row = tk.Frame(popup)
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"{label} :", font=("Helvetica", 10, "bold")).pack(side="left")
                label_color = "black"
                if label == "Urgence" and is_urgent: label_color = "#d35400"
                tk.Label(row, text=val, fg=label_color).pack(side="left", padx=5)

            tk.Frame(popup, height=1, bg="#ddd").pack(fill="x", pady=15)

            if is_past:
                tk.Label(popup, text=" Consultation terminée (Passée)", fg="gray", font=("Helvetica", 10, "italic")).pack()
                tk.Label(popup, text="L'annulation n'est plus possible.", fg="gray", font=("Helvetica", 8)).pack()
            else:
                tk.Button(
                    popup, text="Cancel Appointment", bg="red", fg="white", 
                    relief="flat", pady=8, command=lambda: self.cancel_appointment_from_popup(appointment["id"], popup)
                ).pack(fill="x", pady=10)

    def cancel_appointment_from_popup(self, appointment_id, popup):

        confirm = messagebox.askyesno(
            "Confirm",
            "Are you sure you want to cancel this appointment?"
        )

        if not confirm:
            return

        success, message = AppointmentDAO.cancel_appointment_by_doctor(appointment_id)

        if success:
            messagebox.showinfo("Success", message)
            popup.destroy()
            self.show_weekly_planner()  
        else:
            messagebox.showerror("Error", message)

    def logout(self):
        self.root.destroy()
