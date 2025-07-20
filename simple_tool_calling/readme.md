# Simple Tool Calling

In this first project, we'll implement our own system of tool calling with our tool defined inside the application that wraps around the Ollama api. You can see an example of the result in the end of this file!

## Creating functions to Interact with Postgres

The application files are located in the `src` folder. The `main.py` will be the entry point of the application.

Inside the `src` folder, can be encountered the `postgresql.py` file, which contains the functions to interact with the Postgres database.

```python
connection = None

def connect_to_postgresql():
    global connection
    try:
        connection = psycopg2.connect(
            "dbname=database user=postgres password=admin"
        )
```

The first function is to establish a connection to the Postgres database. 

>[!NOTE]
> Please, change the connection parameters to match your Postgres database configuration - `dbname=database user=postgres password=admin`

```python
def get_favorite_food(name: str):
    cursor = connection.cursor()
    cursor.execute(f"SELECT comida FROM favorite_food WHERE name='{name}'")

    record = cursor.fetchone()
    if record:
        return record[0]
    else:
        raise ValueError("No favorite food found for the given name.")
```

The second function is to get the favorite food of a person from the database. It executes a SQL query to fetch the food based on the person's name.

Please, adapt the SQL query to match your database schema.

## Creating our LLM wrapper.

The `ollama_wrapper.py` file contains the functions to interact with the Ollama Server.

The necessary packages are imported at the beginning of the file. Then we define the model we will use.

Before running the code, make sure to download the model through the Ollama CLI. You can Inspect the models here: [Ollama Models](https://ollama.com/models).

I'm using `gemma3` model, notice that we are gonna implement tool calling with a model that does not "support it" according to the Ollama Models list.

![Ollama Model List](<../docs/Ollama Model List.png>)

```python
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
```

`messages` is a list that functions as a chat history to store all the conversation with the LLM. The first message is a system message that instructs the way the assistant should behave. `DEBUG` will server as a really usefull global variable that'll help during the developing process.

Currently, from my experiments, `gemma3` supports 3 types of roles: `system`, `user` and `assistant`. `system` is usually used to describe the behavior of the assistant, `user` indicates the user messages, whereas `assistant` represents the llm messages.

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
        completed_response = ""
        for chunk in response:
            print(f"{chunk.message.content}", end= "\n" if chunk.done else "", flush=True)
            completed_response += chunk.message.content

        messages.append(
            {"role": "assistant", "content": completed_response}
        )
```
> [!NOTE]
> The code above is a simplified version of the chat loop, it illustrate the main idea behind the chat.

In its essence, the function prompts the user for input, transform the input into a message that is appended to the `messages` list. Then the `messages` are sent to Ollama, returned back as a response stream and printed to the console.

### Intercepting the Messages with other Personas

Now that we have control over the messages exchanged between the user and the assistant, we can interpret it and use in the favour of the application.

In the section **How to Implement Tool Calling** was mentioned that the LLM has to known beforehand it tools so it can call them when necessary. Let's adot a slightly different approach.

The application not necessary has to have one "LLM persona". In this project, there is a "food subject detector" and "name extractor" personas. These different characters will build the arguments necessary to call the tool, that will only be called the all the personas work together.

I suspect this approach will trigger the tool more consistently.

> [!NOTE]
> Note that the current subject now is blending with multiple agents system.

### Food Subject Detector

```python
def detect_food_subject(current_messages: list[str]) -> bool:
    # Remove the orginal system message, then select the last 5 messages.
    filtered_message = current_messages[1:][-5:]
    # Insert the new system message.
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
```

The function above is used to detect if the conversation is related to food. There is not need to check all the messages, in the code block python slice mechanism is used to select only the last five messages.

The new assistant behavior is defined in the system message that is inserted at the beginning of the `filtered_message`. The system message instructs the LLM to detect if the conversation is related to food. We use the `format` mechanism of Ollama API to define the expected output with a **json schema**.

Note, if the `DEBUG` global variable is set to true, we can evaluate the content of the message.

### Name Extractor

The function to extract a persons name is similar to the function explained before. One key difference is in this case only the last user message is used to extract the name.  

```python
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
```

## Back to the Chat Loop

Now that we have the functions to detect food subjects and extract names, we can integrate them into the chat loop.

The first section of the was improved, now you can clean the sent messages and activate the debug mode by typing `/clean` or `/debug` respectively. The two functions that are called are simple and can be found in the `ollama_wrapper.py` file.

Please, note that we are now also injecting the `food_tool_function` as an argument of the `start_chat_thread` function. This allows us to pass the tool function that will be called when the LLM detects a food-related subject.

```python
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
```

Now, let's discuss the food detection section. If, with the function `detect_food_subject`, is determined that the conversation is related to food, the `extract_name_from_message` function is called to extract the name of the person from the user message.

Now that the name is extracted, it can be used to call the `food_tool_function`, which is the function that interacts with the Postgres database to get the favorite food of the person.

We inject a new system message into the messages list containing the information of the person's favorite food, that way, the LLM will use this data into it next new generation.

## Results

``` plaintext
🧐 User:
Hello, how are you? I speak English language.
🤖 Assistant:
Hello! I'm doing well, thank you for asking! It's nice to know you speak English – I do too! 😊 How are *you* doing today?
🧐 User:
/debug
🐍 App: Debug mode set to True.
🧐 User:
I'm fine, thank you! I would like to know Gabriel's favorite dish. I was planning to do something special for him
🍳 Food:  {'is_food_subject': True, 'reason': "The conversation explicitly mentions a 'favorite dish', indicating a food-related topic."}
👤 Name:  {'reason': "The text mentions a person's name.", 'name': 'Gabriel'}
📅 From database: Karê
🤖 Assistant:
That's wonderful you're planning something special for Gabriel! 😊

According to the information I have, Gabriel's favorite dish is **Karê (カレー)**. 

Karê is a Japanese curry dish. It's a thick, flavorful curry typically made with meat (often beef or pork), vegetables like carrots, potatoes, and onions, and a rich, savory curry roux. It's incredibly popular in Japan and loved by many!

Knowing this, you could consider making him some delicious homemade Karê, or even taking him out to a restaurant that serves it. He's sure to appreciate the thoughtfulness! 🍛🎉
```

## Conclusion

I hope, from the little I know, we have learnt something about the practical ways of implementing tools mechanism for agents. We discussed a bit about the principles behind it and how separating the system responsabilities can facilitate the implementation.

From the results above, I invite you to ask the assistant more questions related to how it knows the favorite food of Gabriel, also try to ask about other people that aren't in the database.