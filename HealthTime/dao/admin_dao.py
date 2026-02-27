from database.db import get_connection
from psycopg2.extras import RealDictCursor


class AdminDAO:

    @staticmethod
    def get_doctors():
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT id, name, username, status, license_number
                FROM users
                WHERE role='doctor'
            """)

            doctors = cursor.fetchall()

            for doc in doctors:
                doc["specialties"] = AdminDAO.get_doctor_specialties(doc["id"])

            cursor.close()
            conn.close()
            return doctors

        except Exception as e:
            conn.close()
            print("GET_DOCTORS ERROR:", e)
            return []


    @staticmethod
    def add_doctor(name, username, password, license_number, specialties=[]):
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (name, username, password, role, license_number, status)
                VALUES (%s, %s, %s, 'doctor', %s, 'active')
                RETURNING id
            """, (name, username, password, license_number))

            doctor_id = cursor.fetchone()[0]

            for specialty_id in specialties:
                cursor.execute("""
                    INSERT INTO doctor_specialties (doctor_id, specialty_id)
                    VALUES (%s, %s)
                """, (doctor_id, specialty_id))

            conn.commit()
            cursor.close()
            conn.close()

            return True, "Doctor created successfully"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)


    @staticmethod
    def delete_doctor(doctor_id):
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM users WHERE id=%s AND role='doctor'",
                (doctor_id,)
            )

            conn.commit()
            cursor.close()
            conn.close()

            return True, "Doctor deleted"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)


    @staticmethod
    def deactivate_doctor(doctor_id):
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET status='inactive'
                WHERE id=%s AND role='doctor'
            """, (doctor_id,))

            conn.commit()
            cursor.close()
            conn.close()

            return True, "Doctor deactivated"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)


    @staticmethod
    def get_specialties():
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM specialties ORDER BY name")
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            return data

        except Exception as e:
            conn.close()
            print("GET_SPECIALTIES ERROR:", e)
            return []

    @staticmethod
    def get_doctor_specialties(doctor_id):
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT s.id, s.name
                FROM specialties s
                JOIN doctor_specialties ds ON ds.specialty_id = s.id
                WHERE ds.doctor_id = %s
            """, (doctor_id,))

            specialties = cursor.fetchall()
            cursor.close()
            conn.close()

            return specialties

        except Exception as e:
            conn.close()
            print("GET_DOCTOR_SPECIALTIES ERROR:", e)
            return []
        
    @staticmethod
    def reactivate_doctor(doctor_id):
        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users
                SET status='active'
                WHERE id=%s AND role='doctor'
            """, (doctor_id,))

            conn.commit()
            cursor.close()
            conn.close()

            return True, "Doctor reactivated"

        except Exception as e:
            conn.rollback()
            conn.close()
            return False, str(e)