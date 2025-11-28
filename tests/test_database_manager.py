import unittest
import os
import sys
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.data.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_file = "test_local_vision.db"
        self.db_manager = DatabaseManager(self.db_file)
        self.db_manager.connect()
        self.db_manager.create_tables()

    def tearDown(self):
        if self.db_manager.conn:
            self.db_manager.conn.close()
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_create_tables(self):
        cursor = self.db_manager.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        self.assertIn('conversations', table_names)
        self.assertIn('interactions', table_names)

    def test_execute_crud_query_insert(self):
        query = "INSERT INTO conversations (start_timestamp, user_nickname) VALUES (?, ?)"
        params = ("2023-01-01T00:00:00", "TestUser")
        row_id = self.db_manager.execute_crud_query(query, params)
        self.assertIsNotNone(row_id)
        self.assertGreater(row_id, 0)

    def test_execute_crud_query_select(self):
        query = "INSERT INTO conversations (start_timestamp, user_nickname) VALUES (?, ?)"
        params = ("2023-01-01T00:00:00", "TestUser")
        self.db_manager.execute_crud_query(query, params)

        select_query = "SELECT * FROM conversations WHERE user_nickname = ?"
        result = self.db_manager.execute_crud_query(select_query, ("TestUser",))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "TestUser")

if __name__ == '__main__':
    unittest.main()
