import sys
import os

sys.path.append(os.getcwd())

try:
    print("Importing DatabaseManager...")
    from local_vision.data.database_manager import DatabaseManager
    print("DatabaseManager imported successfully.")
    
    print("Importing HistoryManager...")
    from local_vision.data.history_manager import HistoryManager
    print("HistoryManager imported successfully.")
    
    print("Importing DiscordBot...")
    try:
        from local_vision.logic.discord_bot import DiscordBot
        print("DiscordBot imported successfully.")
    except ImportError as e:
        print(f"DiscordBot import failed (might be missing dependency): {e}")

    print("Importing ImageProcessor...")
    from local_vision.logic.image_processor import ImageProcessor
    print("ImageProcessor imported successfully.")
    
    print("Importing LLM_Manager...")
    from local_vision.logic.llm_manager import LLM_Manager
    print("LLM_Manager imported successfully.")

    print("All syntax checks passed.")
except Exception as e:
    print(f"Syntax check FAILED: {e}")
    sys.exit(1)
