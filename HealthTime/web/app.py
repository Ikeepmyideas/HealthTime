import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, render_template, request, redirect, session
from dao.user_dao import UserDAO
from dao.appointment_dao import AppointmentDAO
from dao.admin_dao import AdminDAO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = UserDAO.authenticate(username, password)

        if isinstance(user, dict) and "error" in user:
            return render_template("login.html", error=user["error"])

        if user:
            session["user"] = user

            if user["role"] == "patient":
                return redirect("/patient_dashboard")
            elif user["role"] == "doctor":
                return redirect("/doctor_dashboard")
            elif user["role"] == "admin":
                return redirect("/admin_dashboard")

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

from datetime import datetime, timedelta

from datetime import datetime, timedelta
from dao.appointment_dao import AppointmentDAO 

@app.route("/patient_dashboard")
def patient_dashboard():
    if "user" not in session or session["user"]["role"] != "patient":
        return redirect("/login")

    user = session["user"]
    tab = request.args.get("tab", "dashboard")
    upcoming_alerts = AppointmentDAO.get_upcoming_appointments(user["id"], user["role"], hours=24)
    dao = AppointmentDAO()
    appointments = dao.get_patient_appointments(user["id"])
    now = datetime.now()
    
    upcoming_appts = []
    past_appts = []
    appt_map = {}

    for a in appointments:
        try:
            date_str = str(a["date"]).strip()
            time_str = str(a["time"]).strip()[:5]
            appt_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            a["is_canceled"] = str(a.get("status", "")).lower() in ("canceled", "cancelled", "cancel")
            a["time_short"] = time_str
            
            if appt_dt >= now:
                upcoming_appts.append(a)
            else:
                past_appts.append(a)
                
            date_obj = appt_dt.date()
            hour = appt_dt.hour
            appt_map[(date_obj, hour)] = a
            
        except Exception as e:
            continue
            
    upcoming_appts.sort(key=lambda x: x["date"])
    past_appts.sort(key=lambda x: x["date"], reverse=True)

    doctors = dao.get_active_doctors()
    
    selected_doc = request.args.get("doc_id")
    selected_date = request.args.get("date")
    slots = []
    
    if selected_doc and selected_date:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        slots = dao.get_available_slots_for_doctor(selected_doc, date_obj)


    week_offset = int(request.args.get("week_offset", 0))
    today = datetime.today().date()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_dates = [monday + timedelta(days=i) for i in range(7)]

    return render_template(
        "patient/dashboard.html",
        user=user,
        tab=tab,
        upcoming=upcoming_appts,
        past=past_appts,
        doctors=doctors,
        selected_doc=selected_doc,
        selected_date=selected_date,
        slots=slots,
        week_dates=week_dates,
        week_offset=week_offset,
        appt_map=appt_map,
        upcoming_alerts=upcoming_alerts,
        now=now
    )

@app.route("/book_appointment", methods=["POST"])
def book_appointment():
    if "user" not in session: 
        return redirect("/login")
    
    user_id = session["user"]["id"]
    doc_id = request.form.get("doc_id")
    date = request.form.get("date")
    time = request.form.get("time")
    
    success, msg = AppointmentDAO().create_appointment(user_id, doc_id, date, time)
    
    return redirect("/patient_dashboard?tab=dashboard")

@app.route("/cancel_appointment/<int:appt_id>", methods=["POST"])
def cancel_appointment(appt_id):
    if "user" not in session: 
        return redirect("/login")
    
    user_id = session["user"]["id"]
    
    AppointmentDAO().cancel_appointment(appt_id, user_id)
    
    return redirect(request.referrer or "/patient_dashboard?tab=dashboard")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if not name or not username or not password or not role:
            return render_template("register.html", error="Tous les champs sont obligatoires.")

        success, msg = UserDAO.register_user(name, username, password, role)

        if success:
            return render_template("login.html", error="Compte créé avec succès ! Connectez-vous.")
        else:
            return render_template("register.html", error=msg)

    return render_template("register.html")

@app.route("/search")
def search():
    search_specialty_id = request.args.get("specialty", "")
    search_name = request.args.get("name", "")
    
    doctors = []
    has_searched = bool(search_specialty_id or search_name)

    if search_name:
        doctors = UserDAO.search_doctors_by_name(search_name)
    elif search_specialty_id:
        doctors = UserDAO.search_doctors_by_specialty(search_specialty_id)
        
    specialties_list = UserDAO.get_all_specialties()

    selected_spec_id = int(search_specialty_id) if search_specialty_id.isdigit() else None

    return render_template(
        "search.html", 
        doctors=doctors, 
        specialties=specialties_list,
        selected_spec_id=selected_spec_id,
        search_name=search_name,
        has_searched=has_searched
    )


import calendar
from dao.doctor_dao import DoctorDAO

@app.route("/doctor_dashboard")
def doctor_dashboard():

    # 🔐 Sécurité
    if "user" not in session or session["user"]["role"] != "doctor":
        return redirect("/login")

    user = session["user"]
    tab = request.args.get("tab", "dashboard")
    upcoming_appts = AppointmentDAO.get_upcoming_appointments(user["id"], user["role"], hours=24)
    year = int(request.args.get("year", datetime.today().year))
    month = int(request.args.get("month", datetime.today().month))

    cal = calendar.monthcalendar(year, month)


    week_offset = int(request.args.get("week_offset", 0))
    today = datetime.today().date()

    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    slots = DoctorDAO.get_doctor_slots(user["id"])
    slot_map = {}

    for s in slots:
        slot_date = s["slot_date"]
        if isinstance(slot_date, str):
            slot_date = datetime.strptime(slot_date, "%Y-%m-%d").date()
            
        slot_hour = int(s["slot_hour"])

        key = f"{slot_date.strftime('%Y-%m-%d')}-{slot_hour}"
        slot_map[key] = s["status"]

    appointments = AppointmentDAO.get_doctor_appointments(user["id"])
    appointment_map = {}

    for a in appointments:
        appt_dt = a.get("appointment_date")
        if not appt_dt:
            continue

        if isinstance(appt_dt, str):
            appt_dt = datetime.strptime(appt_dt, "%Y-%m-%d %H:%M:%S")

        date_obj = appt_dt.date()
        hour = appt_dt.hour

        key = f"{date_obj.strftime('%Y-%m-%d')}-{hour}"

        appointment_map[key] = {
            "id": a["id"],
            "patient_name": a["patient_name"], 
            "patient_email": a["patient_email"], 
            "patient_phone": a["patient_phone"],
            "date": date_obj.strftime("%Y-%m-%d"),
            "time_short": appt_dt.strftime("%H:%M"), 
            "status": a["status"]
        }


    return render_template(
        "doctor/dashboard.html",
        user=user,
        tab=tab,
        year=year,
        month=month,
        cal=cal,
        week_offset=week_offset,
        week_dates=week_dates,
        slot_map=slot_map,
        appt_map=appointment_map,
        upcoming_appts=upcoming_appts,
        now=datetime.now()
    )

@app.route("/doctor_create_slots", methods=["POST"])
def doctor_create_slots():
    if "user" not in session or session["user"]["role"] != "doctor":
        return redirect("/login")
    
    user_id = session["user"]["id"]
    year = request.form.get("year")
    month = request.form.get("month")
    
    selected_days = request.form.getlist("days")
    selected_hours = request.form.getlist("hours")
    
    if not selected_days or not selected_hours:
        return redirect(f"/doctor_dashboard?tab=calendar_planner&year={year}&month={month}")

    for day in selected_days:
        for hour in selected_hours:
            date_str = f"{year}-{int(month):02d}-{int(day):02d}"
            DoctorDAO.create_time_slot_day_hour(user_id, date_str, int(hour))
            
    return redirect(f"/doctor_dashboard?tab=calendar_planner&year={year}&month={month}")

@app.route("/doctor_cancel_appt/<int:appt_id>", methods=["POST"])
def doctor_cancel_appt(appt_id):
    if "user" not in session or session["user"]["role"] != "doctor":
        return redirect("/login")
    
    AppointmentDAO().cancel_appointment_by_doctor(appt_id)
    return redirect(request.referrer or "/doctor_dashboard?tab=weekly_planner")


import random
import string
from flask import request, redirect, session, render_template, flash

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/login")

    user = session["user"]
    tab = request.args.get("tab", "dashboard")
    
    specialties = []
    doctors = []
    search_query = request.args.get("search", "").strip().lower()

    if tab == "add_doctor":
        specialties = AdminDAO.get_specialties()
        
    elif tab == "view_doctors":
        all_doctors = AdminDAO.get_doctors()
        if search_query:
            doctors = [
                d for d in all_doctors 
                if search_query in d["name"].lower() 
                or search_query in d["username"].lower() 
                or search_query == str(d["id"])
            ]
        else:
            doctors = all_doctors

    return render_template(
        "admin/dashboard.html",
        user=user,
        tab=tab,
        specialties=specialties,
        doctors=doctors,
        search_query=search_query
    )

@app.route("/admin_add_doctor", methods=["POST"])
def admin_add_doctor():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/login")

    name = request.form.get("name")
    username = request.form.get("username")
    license_number = request.form.get("license_number")
    selected_specialties = request.form.getlist("specialties") 

    if not name or not username:
        flash("Les champs Nom et Nom d'utilisateur sont obligatoires.", "error")
        return redirect("/admin_dashboard?tab=add_doctor")

    password = generate_password()
    
    success, msg = AdminDAO.add_doctor(name, username, password, license_number, selected_specialties)
    
    if success:
        flash(f"Docteur créé avec succès ! Username : {username} | Mot de passe : {password}", "success")
        return redirect("/admin_dashboard?tab=view_doctors")
    else:
        flash(f"Erreur : {msg}", "error")
        return redirect("/admin_dashboard?tab=add_doctor")

@app.route("/admin_doctor_action/<action>/<int:doctor_id>", methods=["POST"])
def admin_doctor_action(action, doctor_id):
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/login")
        
    if action == "deactivate":
        AdminDAO.deactivate_doctor(doctor_id)
        flash("Le compte du docteur a été désactivé.", "success")
    elif action == "reactivate":
        AdminDAO.reactivate_doctor(doctor_id)
        flash("Le compte du docteur a été réactivé.", "success")
        
    return redirect("/admin_dashboard?tab=view_doctors")

from flask import jsonify, request 

@app.route("/api/toggle_slot", methods=["POST"])
def api_toggle_slot():
    if "user" not in session or session["user"]["role"] != "doctor":
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.json
    date_str = data.get("date")
    hour = int(data.get("hour"))
    doctor_id = session["user"]["id"]
    
    action = DoctorDAO.toggle_doctor_slot(doctor_id, date_str, hour)
    
    return jsonify({"status": "success", "action": action})


from flask import session, redirect, flash

@app.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)