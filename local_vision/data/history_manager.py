from local_vision.data.database_manager import DatabaseManager
import datetime

class HistoryManager:
    """
    Manages the history of conversations and interactions.
    """
    def __init__(self, db_manager: DatabaseManager):
        """
        Initializes the HistoryManager.

        Args:
            db_manager (DatabaseManager): The database manager instance.
        """
        self.db_manager = db_manager

    def create_conversation(self, nickname):
        """
        Creates a new conversation in the database.

        Args:
            nickname (str): The nickname of the user.

        Returns:
            int: The ID of the new conversation.
        """
        timestamp = datetime.datetime.now().isoformat()
        query = "INSERT INTO conversations (start_timestamp, user_nickname) VALUES (?, ?)"
        params = (timestamp, nickname)
        return self.db_manager.execute_crud_query(query, params)

    def save_interaction(self, conversation_id, actor, interaction_type, content=None, image_path=None):
        """
        Saves a new interaction in the database.

        Args:
            conversation_id (int): The ID of the conversation.
            actor (str): The actor of the interaction ('user' or 'system').
            interaction_type (str): The type of interaction ('text', 'image', 'description').
            content (str, optional): The text content of the interaction. Defaults to None.
            image_path (str, optional): The path to the image file. Defaults to None.
        """
        timestamp = datetime.datetime.now().isoformat()
        query = """
        INSERT INTO interactions (conversation_id, timestamp, actor, type, content, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (conversation_id, timestamp, actor, interaction_type, content, image_path)
        self.db_manager.execute_crud_query(query, params)

    def get_conversations(self):
        """
        Retrieves all conversations from the database.

        Returns:
            list: A list of all conversations.
        """
        query = "SELECT * FROM conversations ORDER BY start_timestamp DESC"
        return self.db_manager.execute_crud_query(query)

    def get_conversation_history(self, conversation_id, as_dict=False):
        """
        Retrieves the full history of a specific conversation.

        Args:
            conversation_id (int): The ID of the conversation.
            as_dict (bool): If True, returns a list of dictionaries.

        Returns:
            list: A list of all interactions in the conversation.
        """
        query = "SELECT * FROM interactions WHERE conversation_id = ? ORDER BY timestamp ASC"
        params = (conversation_id,)
        history = self.db_manager.execute_crud_query(query, params)

        if not as_dict:
            return history

        # Convert list of tuples to list of dictionaries
        dict_history = []
        for row in history:
            dict_history.append({
                "interaction_id": row[0],
                "conversation_id": row[1],
                "timestamp": row[2],
                "actor": row[3],
                "type": row[4],
                "content": row[5],
                "image_path": row[6]
            })
        return dict_history


    def delete_conversation(self, conversation_id):
        """
        Deletes a conversation and all its interactions.

        Args:
            conversation_id (int): The ID of the conversation to delete.
        """
        # First, delete all interactions associated with the conversation
        query_interactions = "DELETE FROM interactions WHERE conversation_id = ?"
        params = (conversation_id,)
        self.db_manager.execute_crud_query(query_interactions, params)

        # Then, delete the conversation itself
        query_conversation = "DELETE FROM conversations WHERE conversation_id = ?"
        self.db_manager.execute_crud_query(query_conversation, params)
