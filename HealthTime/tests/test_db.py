import unittest
from database.db import get_connection

class TestDatabaseConnection(unittest.TestCase):

    def test_connection_success(self):
        conn = get_connection()
        self.assertIsNotNone(conn, "Database connection should not be None")
        conn.close()

if __name__ == "__main__":
    unittest.main()
