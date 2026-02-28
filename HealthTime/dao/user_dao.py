from database.db import get_connection

class UserDAO:

    @staticmethod
    def test_connection():
        conn = get_connection()
        if conn:
            conn.close()
            return True
        return False
    
    @staticmethod
    def register_user(name, username, password, role):
        role = role.lower()
        if role != "patient":
            return False, "Only patients can self-register"

        status = 'active'

        conn = get_connection()
        if not conn:
            return False, "Database connection failed"

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, username, password, role, status) VALUES (%s, %s, %s, %s, %s)",
                (name, username, password, role, status)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"{role.capitalize()} registration successful"
        except Exception as e:
            conn.close()
            return False, f"Error: {e}"


    @staticmethod
    def authenticate(username, password):
        """
        Returns user dict if successful login, None if failed or doctor pending.
        """
        conn = get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, role, status FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                user_id, name, role, status = result
                if role == "doctor" and status == "pending":
                    return {"error": "Doctor account pending approval"}
                return {"id": user_id, "name": name, "role": role}
            else:
                return None
        except Exception as e:
            conn.close()
            return {"error": str(e)}
        

    @staticmethod
    def get_all_specialties():
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM specialties ORDER BY name ASC")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [{"id": r[0], "name": r[1]} for r in rows]

        except Exception as e:
            if conn:
                conn.close()
            return []

    @staticmethod
    def search_doctors_by_specialty(specialty_id):
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.name, u.username, s.name as specialty
                FROM users u
                JOIN doctor_specialties ds ON u.id = ds.doctor_id
                JOIN specialties s ON ds.specialty_id = s.id
                WHERE u.role = 'doctor' 
                AND u.status = 'active'
                AND s.id = %s
            """, (specialty_id,))

            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            return [
                {"id": r[0], "name": r[1], "username": r[2], "specialty": r[3]}
                for r in rows
            ]

        except Exception as e:
            if conn:
                conn.close()
            return []

    @staticmethod
    def search_doctors_by_name(name):
        conn = get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.name, u.username, s.name as specialty
                FROM users u
                LEFT JOIN doctor_specialties ds ON u.id = ds.doctor_id
                LEFT JOIN specialties s ON ds.specialty_id = s.id
                WHERE u.role = 'doctor' 
                AND u.status = 'active'
                AND LOWER(u.name) LIKE LOWER(%s)
            """, (f"%{name}%",))

            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            return [
                {"id": r[0], "name": r[1], "username": r[2], "specialty": r[3]}
                for r in rows
            ]

        except Exception as e:
            if conn:
                conn.close()
            return []
