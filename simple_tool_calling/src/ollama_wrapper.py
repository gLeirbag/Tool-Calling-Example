import ollama
import json
from typing import Callable

DEBUG = False

model = "gemma3:12b-it-q8_0"

messages = []
first_message = {
    "role": "system",
    "content": "You are an LLM model, be helpful to the user. Please, answer the user in their native language, you can infer by the user message.",
}

messages.append(first_message)

def detect_food_subject(current_messages: list[str]) -> bool:
    # Remove the system, then select the last 5 messages.
    filtered_message = current_messages[1:][-5:]
    filtered_message.insert(
        0,
        {
            "role": "system",
            "content": "You are a tool to detect if the conversation is related to food in any way, even if indirectly - including mentions of food, questions about favorite food, eating habits, meals, ingredients, or cooking. You must not took into consideration your access to informations about people. Output a JSON",
        },
    )
    res = ollama.chat(
        format={
            "type": "object",
            "properties": {
                "is_food_subject": {"type": "boolean"},
                "reason": {"type": "string"},
            },
            "required": ["is_food_subject", "reason"],
        },
        model=model,
        messages=filtered_message[-5:],
    )
    if DEBUG:
        print("🍳 Food: ", json.loads(res.message.content))
    return json.loads(res.message.content)["is_food_subject"]


def extract_name_from_message(user_message: str) -> str:
    res = ollama.generate(
        format={
            "type": "object",
            "properties": {"name": {"type": "string"}, "reason": {"type": "string"}},
            "required": ["reason"],
        },
        model=model,
        prompt=user_message,
        system="Extract the name of the person from the text. Generate an json",
    )
    if DEBUG:
        print("👤 Name: ", json.loads(res.response))
    try:
        return json.loads(res.response)["name"]
    except KeyError:
        return None


def clean_messages():
    messages.clear()
    messages.append(first_message)
    print("🐍 App: Message History cleared.")


def set_debug():
    global DEBUG
    DEBUG = not DEBUG
    print(f"🐍 App: Debug mode set to {DEBUG}.")


def start_chat_thread(food_tool_function: Callable):
    while True:
        # Handling the user input
        while True:
            print("🧐 User:")
            user_content: str = input() + "\n"
            if user_content.find("/clean\n", 0, 8) != -1:
                clean_messages()
            elif user_content.find("/debug\n", 0, 9) != -1:
                set_debug()
            else:
                user_content.strip()
                break
        user_message = {"role": "user", "content": user_content}
        messages.append(user_message)
        # ==================
        # Handling food detection
        is_food_subject = detect_food_subject(messages)
        if is_food_subject:
            arg_name = extract_name_from_message(user_content)
            if arg_name:
                try:
                    favorite_food = food_tool_function(arg_name)
                    food_found_prompt = f"From a query executed in a Database her/his favorite food is {favorite_food}. Now that you know, you must explain to the user."
                    messages.append(
                        {
                            "role": "system",
                            "content": f"{food_found_prompt}",
                        }
                    )
                    if DEBUG:
                        print(f"📅 From database: {favorite_food}")
                except Exception as e:
                    if DEBUG:
                        print(f"📅 From database: {e}")

        response = ollama.chat(model, messages, stream=True)
        # ============================
        # Handling Ollama Output
        print("🤖 Assistant:")
        complete_response_content: str = None
        for chunk in response:
            if complete_response_content is None:
                complete_response_content = chunk.message.content.lstrip()
                print(f"{chunk.message.content.lstrip()}", end="")
            elif chunk.done:
                complete_response_content += chunk.message.content.rstrip()
                print(f"{chunk.message.content.rstrip()}")
            else:
                complete_response_content += chunk.message.content
                print(f"{chunk.message.content}", end="", flush=True)
        # =========================
        messages.append(
            {
                "role": "assistant",
                "content": complete_response_content,
            }
        )
