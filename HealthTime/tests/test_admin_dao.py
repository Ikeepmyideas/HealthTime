import unittest
from dao.admin_dao import AdminDAO
from database.db import get_connection


class TestAdminDAO(unittest.TestCase):

    def setUp(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute("DELETE FROM users WHERE username LIKE 'test_admin_%'")
        self.conn.commit()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_add_doctor_success(self):
        success, msg = AdminDAO.add_doctor(
            "Test Admin Doctor",
            "test_admin_doc1",
            "1234"
        )

        self.assertTrue(success)
        self.assertIn("doctor", msg.lower())

    def test_get_doctors(self):
        AdminDAO.add_doctor(
            "Test Admin Doctor",
            "test_admin_doc2",
            "1234"
        )

        doctors = AdminDAO.get_doctors()

        usernames = [doc["username"] for doc in doctors]
        self.assertIn("test_admin_doc2", usernames)

    def test_deactivate_doctor(self):
        AdminDAO.add_doctor(
            "Test Admin Doctor",
            "test_admin_doc3",
            "1234"
        )

        doctors = AdminDAO.get_doctors()
        doctor = next((d for d in doctors if d["username"] == "test_admin_doc3"), None)

        self.assertIsNotNone(doctor)

        success, msg = AdminDAO.deactivate_doctor(doctor["id"])
        self.assertTrue(success)

        self.cursor.execute(
            "SELECT status FROM users WHERE username='test_admin_doc3'"
        )
        status = self.cursor.fetchone()[0]

        self.assertEqual(status, "inactive")

    def test_delete_doctor(self):
        AdminDAO.add_doctor(
            "Test Admin Doctor",
            "test_admin_doc4",
            "1234"
        )

        doctors = AdminDAO.get_doctors()
        doctor = next((d for d in doctors if d["username"] == "test_admin_doc4"), None)

        self.assertIsNotNone(doctor)

        success, msg = AdminDAO.delete_doctor(doctor["id"])
        self.assertTrue(success)

        self.cursor.execute(
            "SELECT * FROM users WHERE username='test_admin_doc4'"
        )
        result = self.cursor.fetchone()

        self.assertIsNone(result)


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


if __name__ == "__main__":
    unittest.main()