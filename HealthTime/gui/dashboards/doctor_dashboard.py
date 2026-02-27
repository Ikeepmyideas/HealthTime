import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from dao.doctor_dao import DoctorDAO
from datetime import datetime, timedelta
from dao.appointment_dao import AppointmentDAO


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
            text=f"👨‍⚕️ Dr {self.user['name']}",
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
        self.clear_main()

        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(
            container,
            text=" Create Availability (Calendar Mode)",
            font=("Helvetica", 18, "bold"),
            bg=self.colors["bg"]
        ).pack(pady=10)

        top_frame = tk.Frame(container, bg=self.colors["bg"])
        top_frame.pack(pady=10)

        month_var = tk.IntVar(value=datetime.today().month)
        year_var = tk.IntVar(value=datetime.today().year)

        tk.Label(top_frame, text="Month", bg=self.colors["bg"]).pack(side="left")

        month_combo = ttk.Combobox(
            top_frame,
            textvariable=month_var,
            values=list(range(1, 13)),
            width=5,
            state="readonly"
        )
        month_combo.pack(side="left", padx=5)

        tk.Label(top_frame, text="Year", bg=self.colors["bg"]).pack(side="left")

        year_combo = ttk.Combobox(
            top_frame,
            textvariable=year_var,
            values=list(range(2024, 2035)),
            width=7,
            state="readonly"
        )
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
            for widget in days_frame.winfo_children():
                widget.destroy()

            selected_days.clear()

            year = year_var.get()
            month = month_var.get()

            cal = calendar.monthcalendar(year, month)
            week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

            for col, name in enumerate(week_days):
                tk.Label(
                    days_frame,
                    text=name,
                    bg=self.colors["accent"],
                    fg="white",
                    width=5
                ).grid(row=0, column=col, padx=3, pady=3)

            for row_index, week in enumerate(cal):
                for col_index, day in enumerate(week):

                    if day == 0:
                        tk.Label(
                            days_frame,
                            text="",
                            width=5,
                            bg=self.colors["bg"]
                        ).grid(row=row_index + 1, column=col_index)
                    else:
                        btn = tk.Button(
                            days_frame,
                            text=str(day),
                            width=5,
                            bg="white"
                        )
                        btn.grid(row=row_index + 1,
                                column=col_index,
                                padx=3,
                                pady=3)

                        btn.config(
                            command=lambda d=day, b=btn: toggle_day(d, b)
                        )

        month_combo.bind("<<ComboboxSelected>>", render_calendar)
        year_combo.bind("<<ComboboxSelected>>", render_calendar)

        render_calendar()

        tk.Label(
            container,
            text="Select Hours (7h → 22h)",
            font=("Helvetica", 14, "bold"),
            bg=self.colors["bg"]
        ).pack(pady=10)

        hours_frame = tk.Frame(container, bg=self.colors["bg"])
        hours_frame.pack()

        selected_hours = set()

        def toggle_hour(hour, btn):
            if hour in selected_hours:
                selected_hours.remove(hour)
                btn.config(bg="white")
            else:
                selected_hours.add(hour)
                btn.config(bg="#4CAF50")

        for hour in range(7, 23):
            btn = tk.Button(
                hours_frame,
                text=f"{hour}:00",
                width=6,
                bg="white"
            )
            btn.pack(side="left", padx=4, pady=4)

            btn.config(
                command=lambda h=hour, b=btn: toggle_hour(h, b)
            )

        def save_slots():

            if not selected_days or not selected_hours:
                messagebox.showwarning("Warning", "Select days and hours")
                return

            year = year_var.get()
            month = month_var.get()

            for day in selected_days:
                for hour in selected_hours:

                    date_str = f"{year}-{month:02d}-{day:02d}"

                    DoctorDAO.create_time_slot_day_hour(
                        self.user["id"],
                        date_str,
                        hour
                    )

            messagebox.showinfo("Success", "Availability saved!")

        tk.Button(
            container,
            text=" Save Availability",
            bg="#2196F3",
            fg="white",
            command=save_slots
        ).pack(pady=20)

        legend_frame = tk.Frame(container, bg=self.colors["bg"])
        legend_frame.pack(pady=10, anchor="w")

        tk.Label(
            legend_frame,
            text="Legend :",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["bg"]
        ).pack(anchor="w")

        legend_data = [
            ("🟢", "Available"),
            ("🔴", "Booked with patient"),
            ("⚫", "Outside working hours")
        ]

        for icon, text in legend_data:
            row = tk.Frame(legend_frame, bg=self.colors["bg"])
            row.pack(anchor="w", pady=2)

            tk.Label(
                row,
                text=icon,
                bg=self.colors["bg"],
                font=("Helvetica", 12)
            ).pack(side="left", padx=5)

            tk.Label(
                row,
                text=text,
                bg=self.colors["bg"]
            ).pack(side="left")


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
        self.clear_main()

        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(
            container,
            text="📋 My Appointments (List View)",
            font=("Helvetica", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"]
        ).pack(pady=(10, 20), anchor="w")

        appointments = AppointmentDAO.get_doctor_appointments(self.user["id"])

        if not appointments:
            tk.Label(
                container,
                text="No appointments found.",
                bg=self.colors["bg"],
                fg="gray",
                font=("Helvetica", 12)
            ).pack(pady=20)
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

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for appt in appointments:
            row = tk.Frame(list_frame, bg=self.colors["card"], pady=10)
            row.pack(fill="x", pady=5, padx=(0, 5))

            appt_dt = appt["appointment_date"]
            if isinstance(appt_dt, str):
                appt_dt = datetime.strptime(appt_dt, "%Y-%m-%d %H:%M:%S")
            
            date_str = appt_dt.strftime("%Y-%m-%d")
            time_str = appt_dt.strftime("%H:%M")
            status = appt["status"]

            status_color = "#2ecc71" if status.lower() in ["scheduled", "confirmé"] else "#e74c3c"

            tk.Label(row, text=appt["patient_name"], bg=self.colors["card"], font=("Helvetica", 11), width=20, anchor="w").pack(side="left", padx=10)
            tk.Label(row, text=f"🗓️ {date_str} at 🕒 {time_str}", bg=self.colors["card"], width=25, anchor="w").pack(side="left")
            tk.Label(row, text=status.capitalize(), bg=self.colors["card"], fg=status_color, font=("Helvetica", 10, "bold"), width=15, anchor="w").pack(side="left")

            is_future = appt_dt >= datetime.now()
            is_canceled = status.lower() in ["canceled", "canceled_by_doctor", "annulé"]

            if is_future and not is_canceled:
                tk.Button(
                    row,
                    text="Cancel",
                    bg="#e74c3c",
                    fg="white",
                    relief="flat",
                    padx=10,
                    command=lambda a_id=appt["id"]: self.cancel_appointment_from_list(a_id)
                ).pack(side="right", padx=20)
                
            elif not is_future and not is_canceled:
                tk.Label(
                    row,
                    text="✅ Terminé",
                    bg=self.colors["card"],
                    fg="gray",
                    font=("Helvetica", 10, "italic")
                ).pack(side="right", padx=20)
                

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

        self.clear_main()

        container = tk.Frame(self.main, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        slots = DoctorDAO.get_doctor_slots(self.user["id"])

        slot_map = {}
        all_dates = []

        for s in slots:
            slot_date = s["slot_date"]

            if isinstance(slot_date, str):
                slot_date = datetime.strptime(slot_date, "%Y-%m-%d").date()

            slot_hour = int(s["slot_hour"])

            slot_map[(slot_date, slot_hour)] = s["status"]
            all_dates.append(slot_date)

        base_date = datetime.today().date()

        monday = base_date - timedelta(days=base_date.weekday())
        monday += timedelta(weeks=week_offset)

        week_dates = [monday + timedelta(days=i) for i in range(7)]

        header_frame = tk.Frame(container, bg=self.colors["bg"])
        header_frame.pack(pady=10)

        tk.Button(
            header_frame,
            text="⬅ Previous",
            command=lambda: self.show_weekly_planner(week_offset - 1)
        ).pack(side="left", padx=10)

        tk.Label(
            header_frame,
            text=f"Week of {monday.strftime('%d %B %Y')}",
            font=("Helvetica", 18, "bold"),
            bg=self.colors["bg"]
        ).pack(side="left", padx=20)

        tk.Button(
            header_frame,
            text="Next ➡",
            command=lambda: self.show_weekly_planner(week_offset + 1)
        ).pack(side="left", padx=10)

        days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        table = tk.Frame(container, bg=self.colors["bg"])
        table.pack()

        for col, day in enumerate(days_names):
            tk.Label(
                table,
                text=f"{day}\n{week_dates[col].strftime('%d-%m')}",
                bg=self.colors["accent"],
                fg="white",
                width=14,
                height=2
            ).grid(row=0, column=col + 1)

        for row_index, hour in enumerate(range(7, 23)):

            tk.Label(
                table,
                text=f"{hour}:00",
                bg=self.colors["card"],
                width=8
            ).grid(row=row_index + 1, column=0)

            for col, current_date in enumerate(week_dates):

                key = (current_date, hour)

                if key in slot_map:
                    status = slot_map[key]

                    if status == "available":
                        color = "#2ecc71"  
                    elif status == "booked":
                        color = "#e74c3c"  
                    else:
                        color = "#f39c12"  
                else:
                    color = "#2c3e50"  

                cell = tk.Frame(
                    table,
                    width=100,
                    height=40,
                    bg=color,
                    relief="solid",
                    borderwidth=1
                )

                cell.grid(row=row_index + 1,
                column=col + 1,
                padx=2,
                pady=2)

                if key in slot_map and status == "booked":
                    cell.bind(
                        "<Button-1>",
                        lambda e, d=current_date, h=hour:
                            self.show_appointment_details(d, h)
                    )

        legend_frame = tk.Frame(container, bg=self.colors["bg"])
        legend_frame.pack(pady=20, anchor="w")

        tk.Label(
            legend_frame,
            text="Legend :",
            font=("Helvetica", 12, "bold"),
            bg=self.colors["bg"]
        ).pack(anchor="w")

        legend_items = [
            ("🟢", "Available"),
            ("🔴", "Booked with patient"),
            ("⚫", "Outside working hours")
        ]

        for icon, text in legend_items:
            row = tk.Frame(legend_frame, bg=self.colors["bg"])
            row.pack(anchor="w", pady=2)

            tk.Label(row,
                    text=icon,
                    bg=self.colors["bg"]).pack(side="left", padx=5)

            tk.Label(row,
                    text=text,
                    bg=self.colors["bg"]).pack(side="left")
            

    def show_appointment_details(self, date, hour):

        appointment = AppointmentDAO.get_appointment_by_doctor_date_hour(
            self.user["id"],
            date,
            hour
        )

        if not appointment:
            messagebox.showinfo("Info", "No appointment found.")
            return

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
            text=f"Patient: {appointment['patient_name']}"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Date: {appointment['datetime'].strftime('%Y-%m-%d')}"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Time: {appointment['datetime'].strftime('%H:%M')}"
        ).pack(pady=5)

        tk.Label(
            popup,
            text=f"Status: {appointment['status']}"
        ).pack(pady=5)

        tk.Button(
            popup,
            text="Cancel Appointment",
            bg="red",
            fg="white",
            command=lambda: self.cancel_appointment_from_popup(
                appointment["id"],
                popup
            )
        ).pack(pady=15)



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