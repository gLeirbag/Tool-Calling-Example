import ollama
import json
from typing import Callable

model = "gemma3:12b-it-q8_0"

messages = []
first_message = {
    "role": "system",
    "content": "You are an LLM model, be helpful to the user. Please, answer the user in their native language, you can infer by the user message.",
}

messages.append(first_message)

def detect_food_subject(current_messages: list[str]) -> bool:
    filtered_message = messages[1:]
    filtered_message.insert(0,
        {"role": "system", "content": "Detect if the current subject of the text is a question of favorite food of some person. Generate an json"}
    )
    res = ollama.chat(
        format={"type": "boolean"},
        model=model,
        messages=filtered_message[:3],
    )
    return json.loads(res.message.content)


def extract_name_from_message(user_message: str) -> str:
    res = ollama.generate(
        format={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]},
        model=model,
        prompt=user_message,
        system="Extract the name of the person from the text. Generate an json",
    )
    return json.loads(res.response)["name"]


def start_chat_thread(food_tool_function: Callable):
    while True:
        print("🧐 Usuário:", end=" ")
        user_content: str = input()
        user_message = {"role": "user", "content": user_content}
        messages.append(user_message)

        is_food_subject = detect_food_subject(messages)
        if is_food_subject:
            arg_name = extract_name_from_message(user_content)
            try:
                favorite_food = food_tool_function(arg_name)
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"<think>The system says her/his favorite food is {favorite_food}. Now that I know, I have to explain to the user.<think/>",
                    }
                )
            except Exception:
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"<think>The system says it does not know {arg_name} favorite food. I have to tell the user that I don't know.<think/>",
                    }
                )
        response = ollama.chat(model, messages, stream=True)

        print("🤖 Assistant: ", end="")
        completed_response = None
        for chunk in response:
            print(f"{chunk.message.content}", end= "\n" if chunk.done else "", flush=True)
            completed_response = chunk

        messages.append(
            {"role": completed_response.message.role, "content": completed_response.message.content}
        )
