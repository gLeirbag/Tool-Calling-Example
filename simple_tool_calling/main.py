import sys
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, "src"))

import postgresql
import ollama_wrapper as ollama_wrapper


if __name__ == "__main__":
    postgresql.connect_to_postgresql()
    ollama_wrapper.start_chat_thread(postgresql.get_favorite_food)
