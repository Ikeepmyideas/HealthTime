from database.db import get_connection
from datetime import datetime, timedelta

class AppointmentDAO:

    @staticmethod
    def get_active_doctors():
        """Return list of active doctors as dicts [{'id': ..., 'name': ...}]"""
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM users WHERE role='doctor' AND status='active'")
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return [{"id": r[0], "name": r[1]} for r in results]
        except:
            conn.close()
            return []

    @staticmethod
    def get_appointments_for_doctor_on_date(doctor_id, date):
        """Return list of times already booked for doctor on given date"""
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT appointment_date
                    FROM appointments
                    WHERE doctor_id=%s
                    AND DATE(appointment_date)=%s
                    AND status='scheduled'
            """, (doctor_id, date))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return [r[0].strftime("%H:%M") for r in results]
        except:
            conn.close()
            return []

    @staticmethod
    def get_available_slots_for_doctor(doctor_id, date):
        """
        Retourne les créneaux disponibles pour un docteur spécifique à une date donnée
        en croisant la table time_slots et la table appointments.
        """
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ts.slot_hour
                FROM time_slots ts
                WHERE ts.doctor_id = %s
                AND ts.slot_date = %s
                AND ts.status = 'available'
                AND NOT EXISTS (
                    SELECT 1 FROM appointments a
                    WHERE a.doctor_id = ts.doctor_id
                    AND DATE(a.appointment_date) = ts.slot_date
                    AND EXTRACT(HOUR FROM a.appointment_date) = ts.slot_hour
                    AND a.status = 'scheduled'
                )
                ORDER BY ts.slot_hour
            """, (doctor_id, date))

            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [f"{r[0]:02d}:00" for r in rows]
        except Exception as e:
            if conn: conn.close()
            print(f"Erreur get_available_slots_for_doctor: {e}")
            return []

    @staticmethod
    def get_available_slots_by_specialty(specialty_id, date):
        """
        RECHERCHE MULTI-DOCTEURS (Option 'Peu importe')
        Retourne une liste de dictionnaires contenant l'heure, l'ID et le nom du docteur
        pour tous les praticiens d'une spécialité ayant des créneaux libres.
        """
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT ts.slot_hour, u.id, u.name
                FROM time_slots ts
                JOIN users u ON ts.doctor_id = u.id
                JOIN doctor_specialties ds ON u.id = ds.doctor_id
                WHERE ds.specialty_id = %s
                AND ts.slot_date = %s
                AND ts.status = 'available'
                AND u.status = 'active'
                AND NOT EXISTS (
                    SELECT 1 FROM appointments a
                    WHERE a.doctor_id = ts.doctor_id
                    AND DATE(a.appointment_date) = ts.slot_date
                    AND EXTRACT(HOUR FROM a.appointment_date) = ts.slot_hour
                    AND a.status = 'scheduled'
                )
                ORDER BY ts.slot_hour, u.name
            """
            cursor.execute(query, (specialty_id, date))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            return [
                {
                    "time": f"{r[0]:02d}:00",
                    "doctor_id": r[1],
                    "doctor_name": r[2]
                } for r in rows
            ]
        except Exception as e:
            if conn: conn.close()
            print(f"Erreur get_available_slots_by_specialty: {e}")
            return []


    @staticmethod
    def create_appointment(patient_id, doctor_id, date_str, time_str, urgent=False):
        """Crée un rendez-vous avec gestion optionnelle du flag urgent"""
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()
            appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            # Note: Assurez-vous que votre table 'appointments' possède la colonne 'urgent' (BOOLEAN)
            cursor.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, urgent)
                VALUES (%s, %s, %s, 'scheduled', %s)
            """, (patient_id, doctor_id, appointment_datetime, urgent))

            cursor.execute("""
                UPDATE time_slots
                SET status = 'booked'
                WHERE doctor_id = %s
                AND slot_date = %s
                AND slot_hour = %s
            """, (doctor_id, date_str, appointment_datetime.hour))

            conn.commit()
            cursor.close()
            conn.close()
            return True, "Appointment booked successfully"
        except Exception as e:
            if conn: conn.rollback(); conn.close()
            return False, str(e)


    @staticmethod
    def get_patient_appointments(patient_id):
        """Retourne tous les rendez-vous d'un patient avec le flag urgent"""
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, u.name, a.appointment_date, a.status, a.urgent
                FROM appointments a
                JOIN users u ON a.doctor_id = u.id
                WHERE a.patient_id=%s
                ORDER BY a.appointment_date ASC
            """, (patient_id,))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            appointments = []
            for r in results:
                appointments.append({
                    "id": r[0],
                    "doctor_name": r[1],
                    "date": r[2].strftime("%Y-%m-%d"),
                    "time": r[2].strftime("%H:%M"),
                    "status": r[3],
                    "urgent": r[4] # Récupération de l'état urgent
                })
            return appointments
        except:
            if conn: conn.close()
            return []
        

    @staticmethod
    def cancel_appointment(appointment_id, patient_id):
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT doctor_id, appointment_date
                FROM appointments
                WHERE id=%s AND patient_id=%s
            """, (appointment_id, patient_id))

            row = cursor.fetchone()

            if not row:
                cursor.close()
                conn.close()
                return False, "Appointment not found or not yours"

            doctor_id = row[0]
            appointment_date = row[1]
            hour = appointment_date.hour
            date_str = appointment_date.date()

            cursor.execute("""
                UPDATE appointments
                SET status='canceled'
                WHERE id=%s AND patient_id=%s
            """, (appointment_id, patient_id))

            cursor.execute("""
                UPDATE time_slots
                SET status='available'
                WHERE doctor_id=%s
                AND slot_date=%s
                AND slot_hour=%s
            """, (doctor_id, date_str, hour))

            conn.commit()
            cursor.close()
            conn.close()

            return True, "Appointment canceled"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)

    @staticmethod
    def modify_appointment(appointment_id, doctor_id, new_date_str, new_time_str):
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"
        try:
            cursor = conn.cursor()
            new_datetime = datetime.strptime(f"{new_date_str} {new_time_str}", "%Y-%m-%d %H:%M")
            cursor.execute("""
                UPDATE appointments
                SET doctor_id=%s, appointment_date=%s, status='scheduled'
                WHERE id=%s
            """, (doctor_id, new_datetime, appointment_id))
            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return False, "Appointment not found"
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Appointment modified successfully"
        except Exception as e:
            conn.close()
            return False, str(e)
        

    @staticmethod
    def get_upcoming_appointments(user_id, role, hours=24):
        """
        Returns appointments happening within the next X hours for a doctor OR a patient
        """
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            
            now = datetime.now()
            limit_time = now + timedelta(hours=hours)

            if role == 'doctor':
                query = """
                    SELECT a.appointment_date, u.name
                    FROM appointments a
                    JOIN users u ON a.patient_id = u.id
                    WHERE a.doctor_id = %s
                    AND a.status = 'scheduled'
                    AND a.appointment_date BETWEEN %s AND %s
                    ORDER BY a.appointment_date
                """
            else:
                query = """
                    SELECT a.appointment_date, u.name
                    FROM appointments a
                    JOIN users u ON a.doctor_id = u.id
                    WHERE a.patient_id = %s
                    AND a.status = 'scheduled'
                    AND a.appointment_date BETWEEN %s AND %s
                    ORDER BY a.appointment_date
                """

            cursor.execute(query, (user_id, now, limit_time))
            results = cursor.fetchall()

            return [{
                "date": r[0].strftime("%d/%m/%Y"), 
                "time": r[0].strftime("%H:%M"),
                "contact_name": r[1]
            } for r in results]

        except Exception as e:
            print(f"Erreur get_upcoming_appointments: {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

    @staticmethod
    def get_available_slots_for_doctor(doctor_id, date):
        """
        Return available slots from doctor time_slots
        AND not already booked
        """
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ts.slot_hour
                FROM time_slots ts
                WHERE ts.doctor_id = %s
                AND ts.slot_date = %s
                AND ts.status = 'available'
                AND NOT EXISTS (
                    SELECT 1 FROM appointments a
                    WHERE a.doctor_id = ts.doctor_id
                    AND DATE(a.appointment_date) = ts.slot_date
                    AND EXTRACT(HOUR FROM a.appointment_date) = ts.slot_hour
                    AND a.status = 'scheduled'
                )
                ORDER BY ts.slot_hour
            """, (doctor_id, date))

            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            return [f"{r[0]:02d}:00" for r in rows]

        except Exception as e:
            conn.close()
            return []

    @staticmethod
    def get_appointment_by_doctor_date_hour(doctor_id, date, hour):
        conn = get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT a.id, u.name, a.appointment_date, a.status
                FROM appointments a
                JOIN users u ON a.patient_id = u.id
                WHERE a.doctor_id = %s
                AND DATE(a.appointment_date) = %s
                AND EXTRACT(HOUR FROM a.appointment_date) = %s
                AND a.status = 'scheduled'
            """, (doctor_id, date, hour))

            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if not row:
                return None

            return {
                "id": row[0],
                "patient_name": row[1],
                "datetime": row[2],
                "status": row[3]
            }

        except Exception as e:
            conn.close()
            return None

    @staticmethod
    def cancel_appointment_by_doctor(appointment_id):
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT doctor_id, appointment_date
                FROM appointments
                WHERE id = %s
            """, (appointment_id,))

            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return False, "Appointment not found"

            doctor_id = row[0]
            appointment_datetime = row[1]

            slot_date = appointment_datetime.date()
            slot_hour = appointment_datetime.hour

            cursor.execute("""
                UPDATE appointments
                SET status = 'canceled_by_doctor'
                WHERE id = %s
            """, (appointment_id,))

            cursor.execute("""
                UPDATE time_slots
                SET status = 'available'
                WHERE doctor_id = %s
                AND slot_date = %s
                AND slot_hour = %s
            """, (doctor_id, slot_date, slot_hour))

            conn.commit()
            cursor.close()
            conn.close()

            return True, "Appointment canceled successfully"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)
        
    @staticmethod
    def get_doctor_appointments(doctor_id):
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT a.id,
                       a.appointment_date,
                       a.status,
                       a.urgent,
                       u.name,
                       u.username
                FROM appointments a
                JOIN users u ON a.patient_id = u.id
                WHERE a.doctor_id = %s
                ORDER BY a.appointment_date ASC
            """, (doctor_id,))

            rows = cursor.fetchall()
            
            return [
                {
                    "id": r[0],
                    "appointment_date": r[1],
                    "status": r[2],
                    "urgent": r[3],         
                    "patient_name": r[4],    
                    "patient_email": r[5],   
                    "patient_phone": "Non disponible"
                }
                for r in rows
            ]

        except Exception as e:
            print(f"Erreur SQL dans get_doctor_appointments : {e}")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()
