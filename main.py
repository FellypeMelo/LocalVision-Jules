from local_vision.ui.main_window import InterfaceGrafica
from local_vision.data.database_manager import DatabaseManager
from local_vision.data.history_manager import HistoryManager

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.connect()
    db_manager.create_tables()
    history_manager = HistoryManager(db_manager)

    app = InterfaceGrafica(history_manager)
    app.run()
