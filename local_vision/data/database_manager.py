import sqlite3
from sqlite3 import Error

class DatabaseManager:
    """
    Manages the connection to the SQLite database and table creation.
    """
    def __init__(self, db_file="local_vision.db"):
        """
        Initializes the DatabaseManager.

        Args:
            db_file (str): The path to the SQLite database file.
        """
        self.db_file = db_file
        self.conn = None

    def connect(self):
        """
        Create a database connection to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            print(f"Successfully connected to SQLite version {sqlite3.version}")
        except Error as e:
            print(e)
        return self.conn

    def create_tables(self):
        """
        Creates the necessary tables if they do not exist.
        """
        create_conversations_table = """
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_timestamp TEXT NOT NULL,
            user_nickname TEXT NOT NULL
        );
        """
        create_interactions_table = """
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            actor TEXT NOT NULL,
            type TEXT NOT NULL,
            content TEXT,
            image_path TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
        );
        """
        try:
            if not self.conn:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute(create_conversations_table)
            cursor.execute(create_interactions_table)
            self.conn.commit()
            print("Tables created successfully.")
        except Error as e:
            print(e)

    def execute_crud_query(self, query, params=()):
        """
        Executes a CRUD (Create, Read, Update, Delete) query.

        Args:
            query (str): The SQL query to execute.
            params (tuple): The parameters to substitute in the query.

        Returns:
            list: The result of the query (for 'SELECT' statements).
        """
        try:
            if not self.conn:
                self.connect()
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.conn.commit()
                return cursor.lastrowid
        except Error as e:
            print(e)
            return None

if __name__ == '__main__':
    # Example usage:
    db_manager = DatabaseManager()
    db_manager.connect()
    db_manager.create_tables()
    print("Database setup complete.")
