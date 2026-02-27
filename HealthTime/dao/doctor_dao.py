from database.db import get_connection
from psycopg2.extras import RealDictCursor


class DoctorDAO:

    @staticmethod
    def create_time_slot(doctor_id, start_time, end_time):
        conn = get_connection()
        if not conn:
            return False, "DB error"

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO time_slots (doctor_id, start_time, end_time)
                VALUES (%s, %s, %s)
            """, (doctor_id, start_time, end_time))

            conn.commit()
            cursor.close()
            conn.close()

            return True, "Time slot created"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)
        
    @staticmethod
    def get_doctor_slots(doctor_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT slot_date, slot_hour, status
            FROM time_slots
            WHERE doctor_id=%s
        """, (doctor_id,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            {"slot_date": r[0], "slot_hour": r[1], "status": r[2]}
            for r in rows
        ]
        

    @staticmethod
    def book_slot(slot_id):
        conn = get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE time_slots
                SET status = 'booked'
                WHERE id = %s
            """, (slot_id,))

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception:
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def create_time_slot_day_hour(doctor_id, slot_date, slot_hour):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO time_slots (doctor_id, slot_date, slot_hour, status)
            VALUES (%s, %s, %s, 'available')
            ON CONFLICT DO NOTHING
        """, (doctor_id, slot_date, slot_hour))

        conn.commit()
        cursor.close()
        conn.close()

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

        except:
            conn.close()
            return None


    @staticmethod
    def toggle_doctor_slot(doctor_id, slot_date, slot_hour):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, status FROM time_slots 
            WHERE doctor_id = %s AND slot_date = %s AND slot_hour = %s
        """, (doctor_id, slot_date, slot_hour))
        
        slot = cursor.fetchone()
        
        if slot:
            if slot[1] == 'available':
                cursor.execute("DELETE FROM time_slots WHERE id = %s", (slot[0],))
                conn.commit()
                action = "removed"
            else:
                action = "booked" 
        else:
            cursor.execute("""
                INSERT INTO time_slots (doctor_id, slot_date, slot_hour, status, is_booked) 
                VALUES (%s, %s, %s, 'available', False)
            """, (doctor_id, slot_date, slot_hour))
            conn.commit()
            action = "added"
            
        cursor.close()
        conn.close()
        return action