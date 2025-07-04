import sys
import os
import asyncio

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, "src"))

from client import ollama_wrapper
async def main():
    await ollama_wrapper.start_chat_thread()


if __name__ == "__main__":
    asyncio.run(main())
