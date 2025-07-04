import ollama
from client import client
model = "llama3.2"
tools = []

messages = []
first_message = {
    "role": "system",
    "content": "You are an LLM model, be helpful to the user. Please, answer the user in their native language, you can infer by the user message. Only use the available tools when the user specifically asks about someone's favorite food.",
}

mcp_client = client.mcp_Client


async def insert_tools_into_context():
    async with mcp_client:
        resources = await mcp_client.list_resource_templates()
        for resource in resources:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": resource.name,
                        "description": resource.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "person": {
                                    "type": "string",
                                    "description": "The name of the person whose favorite food you want to know.",
                                }
                            },
                            "required": ["person"],
                        },
                    },
                }
            )


async def handle_tool_calls(response):
    async with mcp_client:
        for tool_call in response.message.tool_calls:
            try:
                result = await mcp_client.read_resource(
                    f"resource://favorite/food/{tool_call.function.arguments['person']}"
                )
                print(f"\n🛠️ Tool call result: {result[0].text}")
                messages.append(
                    {
                        "role": "tool",
                        "content": f"The assistant has the information that {tool_call.function.arguments['person']}'s favorite food is {result[0].text}. "
                        "Even if you think you don't know the answer, you must answer that.",
                        "name": tool_call.function.name,
                    }
                )
            except Exception as e:
                messages.append(
                    {
                        "role": "tool",
                        "content": f"I don't have information about {tool_call.function.arguments['person']}'s favorite food. Please provide a valid person's name.",
                        "name": tool_call.function.name,
                    }
                )


async def start_chat_thread():
    messages.append(first_message)
    await insert_tools_into_context()
    while True:
        print("🧐 Usuário:", end=" ")
        user_content: str = input()
        user_message = {"role": "user", "content": user_content}
        messages.append(user_message)

        response = ollama.chat(model=model, messages=messages, tools=tools, stream=True)


        print("🤖 Assistant: ", end="")
        completed_response = None
        
        for chunk in response:
            if chunk.message.tool_calls:
                await handle_tool_calls(chunk)
                new_response = ollama.chat(model=model, messages=messages, stream=True)
                for new_chunk in new_response:
                    if new_chunk.message.content:
                        print(f"{new_chunk.message.content}", end="", flush=True)
                    if new_chunk.done:
                        print() 
                        completed_response = new_chunk
                        break
                break
            else:
                if chunk.message.content:
                    print(f"{chunk.message.content}", end="", flush=True)
                
                if chunk.done:
                    print() 
                    completed_response = chunk
                    break

        if completed_response and completed_response.message.content:
            messages.append(
                {"role": completed_response.message.role, "content": completed_response.message.content}
            )
