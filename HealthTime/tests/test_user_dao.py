import unittest
from dao.user_dao import UserDAO
from database.db import get_connection

class TestUserDAO(unittest.TestCase):

    def setUp(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM users WHERE username LIKE 'test_%'")
        self.conn.commit()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_register_patient_success(self):
        success, msg = UserDAO.register_user(
            "Test Patient", "test_patient", "1234", "patient"
        )
        self.assertTrue(success)
        self.assertIn("registration successful", msg.lower())

    def test_register_invalid_role(self):
        success, msg = UserDAO.register_user(
            "Test Doctor", "test_doctor", "1234", "doctor"
        )
        self.assertFalse(success)
        self.assertIn("only patients", msg.lower())

if __name__ == "__main__":
    unittest.main()
