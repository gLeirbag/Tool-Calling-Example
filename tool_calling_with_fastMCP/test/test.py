import sys
import os

sys.path.append(os.path.join(os.getcwd(), "src"))

import asyncio
from client import client


mcp_client = client.mcp_Client

async def test_get_resources():
    async with mcp_client:
        tools = await mcp_client.list_resources()
        print(f"The resources  are: {tools}")

async def test_ping():
    async with mcp_client:
        did_ping : bool = await mcp_client.ping()
        try:
            assert did_ping is True
        except Exception:
            print("Could not Ping!")

async def test_food_call(name: str):
    async with mcp_client:
        favorite_food = await mcp_client.read_resource(f"resource://favorite/food/{name}")
        print(f"Favorite food of {name} is {favorite_food[0].text}")

async def run():
    async with asyncio.TaskGroup() as group:
        group.create_task(test_get_resources())
        group.create_task(test_ping())
        group.create_task(test_food_call("Gabriel"))

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()

