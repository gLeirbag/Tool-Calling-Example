# Simple Tool Calling

In the first project, we'll implement our own system of tool calling with our tool defined inside the application that wraps around the Ollama api.

## Creating functions to Interact with Postgres

The application files are located in the `src` folder. The `main.py` will be the entry point of the application.

Inside the `src` folder, can be encountered the `postgresql.py` file, which contains the functions to interact with the Postgres database.

```python
connection = None

def connect_to_postgresql():
    global connection
    try:
        connection = psycopg2.connect(
            "dbname=experimentos user=postgres password=admin"
        )
```

The first function is to establish a connection to the Postgres database. 

>[!NOTE]
> Please, change the connection parameters to match your Postgres database configuration - `dbname=database user=postgres password=admin`

```python
def get_favorite_food(name: str):
    cursor = connection.cursor()
    cursor.execute(f"SELECT comida FROM comida_favorita WHERE nome_pessoa='{name}'")

    record = cursor.fetchone()
    if record:
        return record[0]
    else:
        return None
```

The second function is to get the favorite food of a person from the database. It executes a SQL query to fetch the food based on the person's name.

Please, adapt the SQL query to match your database schema.

## Creating our LLM wrapper.

The `ollama_wrapper.py` file contains the functions to interact with the Ollama API.

The necessary packages are imported at the beginning of the file. Then we define the model we will use in Ollama.

Before running the code, make sure to download the model through the Ollama CLI. You can Inspect the models here: [Ollama Models](https://ollama.com/models).

I'm using `gemma3` model, notice that we are gonna implement tool calling with a model that does not "support it" according to the Ollama Models list.

![Ollama Model List](<../docs/Ollama Model List.png>)

```python
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
```

`messages` is a list that functions as a chat history to store all the conversation with the LLM. The first message is a system message that instructs the way the assistant should behave.

### The Chat Loop

The `start_chat_thread` function contains the key loop of our program. It is this loop that allows our application to wrap itself around the LLM, with it our applications has the messages that the LLM receives and the responses it generates.

```python
def start_chat_thread():
    while True:
        print("🧐 User:", end=" ")
        user_content: str = input()
        user_message = {"role": "user", "content": user_content}
        messages.append(user_message)

        response = ollama.chat(model, messages, stream=True)

        print("🤖 Assistant: ", end="")
        completed_response = None
        for chunk in response:
            print(f"{chunk.message.content}", end= "\n" if chunk.done else "", flush=True)
            completed_response = chunk

        messages.append(
            {"role": completed_response.message.role, "content": completed_response.message.content}
        )
```

In its essence, the function prompts the user for input, transform the input into a message that is appended to the `messages` list. Then the 
