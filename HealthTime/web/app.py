import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import render_template, request, redirect, url_for, flash, session
from flask import Flask, render_template, request, redirect, session
from dao.user_dao import UserDAO
from dao.appointment_dao import AppointmentDAO
from dao.admin_dao import AdminDAO
from dotenv import load_dotenv
from datetime import datetime, timedelta

from datetime import datetime, timedelta
from dao.appointment_dao import AppointmentDAO 
import calendar
from dao.doctor_dao import DoctorDAO
import random
import string
from flask import request, redirect, session, render_template, flash
from flask import jsonify, request 
from flask import session, redirect, flash

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


@app.route("/patient_dashboard")
def patient_dashboard():
    if "user" not in session or session["user"]["role"] != "patient":
        return redirect("/login")

    user = session["user"]
    tab = request.args.get("tab", "dashboard")
    now = datetime.now()
    dao = AppointmentDAO()

    upcoming_alerts = dao.get_upcoming_appointments(user["id"], "patient", hours=24)
    
    data = {
        "user": user, "tab": tab, "upcoming_alerts": upcoming_alerts, "now": now,
        "specialties": [], "filtered_doctors": [], "slots": [], "upcoming": [], "past": [], "appt_map": {},
        "week_offset": int(request.args.get("week_offset", 0))
    }

    if tab == "dashboard":
        appointments = dao.get_patient_appointments(user["id"])
        for a in appointments:
            appt_dt = datetime.strptime(f"{a['date']} {a['time']}", "%Y-%m-%d %H:%M")
            a["is_canceled"] = str(a.get("status", "")).lower() in ("canceled", "cancel")
            if appt_dt >= now: data["upcoming"].append(a)
            else: data["past"].append(a)

    elif tab == "booking":
        data["specialties"] = AdminDAO.get_specialties()
        spec_id = request.args.get("specialty_id")
        doc_id = request.args.get("doctor_id")
        date_str = request.args.get("date")

        if spec_id:
            data["selected_specialty"] = spec_id
            data["filtered_doctors"] = UserDAO.search_doctors_by_specialty(spec_id)
            if date_str:
                data["selected_date"] = date_str
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if doc_id and doc_id != "any":
                    data["selected_doctor"] = doc_id
                    data["slots"] = dao.get_available_slots_for_doctor(doc_id, date_obj)
                else:
                    data["selected_doctor"] = "any"
                    data["slots"] = dao.get_available_slots_by_specialty(spec_id, date_obj)

    elif tab == "calendar":
        monday = (now.date() - timedelta(days=now.date().weekday())) + timedelta(weeks=data["week_offset"])
        data["week_dates"] = [monday + timedelta(days=i) for i in range(7)]
        
        appointments = dao.get_patient_appointments(user["id"])
        for a in appointments:
            appt_dt = datetime.strptime(f"{a['date']} {a['time']}", "%Y-%m-%d %H:%M")
            d_obj = appt_dt.date()
            h_obj = appt_dt.hour
            
            a["is_canceled"] = str(a.get("status", "")).lower() in ("canceled", "cancel")
            a["is_past"] = appt_dt < now
            a["is_cancelable"] = (not a["is_canceled"]) and (not a["is_past"])
            a["time_short"] = a["time"]
            
            data["appt_map"][(d_obj, h_obj)] = a

        data["doctors"] = dao.get_active_doctors()

    return render_template("patient/dashboard.html", **data)


@app.route("/book_appointment", methods=["POST"])
def book_appointment():
    if "user" not in session: return redirect("/login")
    
    patient_id = session["user"]["id"]
    doc_id = request.form.get("doc_id")
    date = request.form.get("date")
    time = request.form.get("time")
    urgent = request.form.get("urgent") == "on"

    if datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M") < datetime.now():
        flash("Impossible de réserver dans le passé.", "danger")
        return redirect(url_for("patient_dashboard", tab="booking"))

    success, msg = AppointmentDAO.create_appointment(patient_id, doc_id, date, time, urgent=urgent)
    if success:
        flash("Rendez-vous confirmé !", "success")
        return redirect("/patient_dashboard?tab=dashboard")
    flash(f"Erreur : {msg}", "danger")
    return redirect("/patient_dashboard?tab=booking")

@app.route("/cancel_appointment/<int:appt_id>", methods=["POST"])
def cancel_appointment(appt_id):
    if "user" not in session: return redirect("/login")
    success, msg = AppointmentDAO.cancel_appointment(appt_id, session["user"]["id"])
    flash("Rendez-vous annulé." if success else msg, "success" if success else "danger")
    return redirect(request.referrer or "/patient_dashboard")

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



@app.route("/doctor_dashboard")
def doctor_dashboard():
    if "user" not in session or session["user"]["role"] != "doctor":
        return redirect("/login")

    user = session["user"]
    tab = request.args.get("tab", "dashboard")
    now = datetime.now()
    
    year = int(request.args.get("year", now.year))
    month = int(request.args.get("month", now.month))
    cal = calendar.monthcalendar(year, month)
    
    week_offset = int(request.args.get("week_offset", 0))
    monday = (now.date() - timedelta(days=now.date().weekday())) + timedelta(weeks=week_offset)
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    slots = DoctorDAO.get_doctor_slots(user["id"])
    slot_map = {f"{s['slot_date']}-{s['slot_hour']}": s["status"] for s in slots}

    appointments = AppointmentDAO.get_doctor_appointments(user["id"])
    appointment_map = {}

    for a in appointments:
        appt_dt = a['appointment_date']
        if isinstance(appt_dt, str):
            try:
                appt_dt = datetime.strptime(appt_dt, "%Y-%m-%d %H:%M:%S")
            except:
                appt_dt = datetime.strptime(appt_dt, "%Y-%m-%d %H:%M")

        key = f"{appt_dt.strftime('%Y-%m-%d')}-{appt_dt.hour}"
        
        a["is_urgent"] = a.get("urgent", False)
        
        a["is_canceled"] = str(a.get("status", "")).lower() in ("canceled", "cancel", "canceled_by_doctor")
        a["is_past"] = appt_dt < now
        
        a["is_cancelable"] = (not a["is_canceled"]) and (not a["is_past"])
        a["time_short"] = appt_dt.strftime("%H:%M")
        a["date_str"] = appt_dt.strftime("%d/%m/%Y")
        
        appointment_map[key] = a
    upcoming_appts = AppointmentDAO.get_upcoming_appointments(user["id"], "doctor", hours=24)

    data = {
        "user": user,
        "tab": tab,
        "year": year,
        "month": month,
        "cal": cal,
        "week_dates": week_dates,
        "week_offset": week_offset,
        "slot_map": slot_map,
        "appt_map": appointment_map,
        "upcoming_appts": upcoming_appts,
        "now": now
    }
    
    return render_template("doctor/dashboard.html", **data)


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



def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route("/admin_dashboard")
def admin_dashboard():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/login")

    user = session["user"]
    tab = request.args.get("tab", "dashboard")
    search_query = request.args.get("search", "").strip().lower()

    data = {
        "user": user,
        "tab": tab,
        "search_query": search_query,
        "stats": None,
        "all_users": [],
        "doctors": [],
        "specialties": []
    }

    if tab == "dashboard":
        users_list = AdminDAO.get_all_users()
        data["stats"] = {
            "total_users": len(users_list),
            "total_doctors": len([u for u in users_list if u['role'] == 'doctor']),
            "total_patients": len([u for u in users_list if u['role'] == 'patient'])
        }

    elif tab == "view_users":
        data["all_users"] = AdminDAO.get_all_users()

    elif tab == "view_doctors":
        all_docs = AdminDAO.get_doctors()
        if search_query:
            data["doctors"] = [
                d for d in all_docs 
                if search_query in d["name"].lower() 
                or search_query in d["username"].lower() 
                or search_query == str(d["id"])
            ]
        else:
            data["doctors"] = all_docs

    elif tab == "add_doctor":
        data["specialties"] = AdminDAO.get_specialties()

    elif tab == "specialties":
        data["specialties"] = AdminDAO.get_specialties()

    return render_template("admin/dashboard.html", **data)


@app.route("/admin_toggle_user/<int:user_id>", methods=["POST"])
def admin_toggle_user(user_id):
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/login")

    current_status = request.form.get("current_status")
    target_tab = request.form.get("tab", "view_users")
    
    success, msg = AdminDAO.toggle_user_status(user_id, current_status)
    
    if success:
        flash("Le statut de l'utilisateur a été mis à jour.", "success")
    else:
        flash(f"Erreur : {msg}", "danger")
    
    return redirect(url_for('admin_dashboard', tab=target_tab))


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



@app.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect("/")



@app.route("/admin_add_specialty", methods=["POST"])
def admin_add_specialty():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/login")

    name = request.form.get("name")
    if name:
        success, msg = AdminDAO.add_specialty(name)
        if success:
            flash(f"Spécialité '{name}' ajoutée.", "success")
        else:
            flash(f"Erreur : {msg}", "danger")
    
    return redirect(url_for('admin_dashboard', tab='specialties'))

@app.route("/admin_delete_specialty/<int:spec_id>", methods=["POST"])
def admin_delete_specialty(spec_id):
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect("/login")

    success, msg = AdminDAO.delete_specialty(spec_id)
    if success:
        flash("Spécialité supprimée.", "success")
    else:
        flash(msg, "warning") 
    
    return redirect(url_for('admin_dashboard', tab='specialties'))


if __name__ == "__main__":
    app.run(debug=True)
