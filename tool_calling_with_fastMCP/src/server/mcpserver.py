from fastmcp import FastMCP
from database import postgres

postgres.connect_to_postgresql()

mcp_server = FastMCP("Meu Servidor")

@mcp_server.resource(
    uri = "resource://favorite/food/{person}",
    mime_type= "text/plain"
)
async def get_favorite_food(person: str) -> str:
    """Finds the favorite food of a person by its name!"""
    return postgres.get_comida_favorita(person)

if __name__ == "__main__":
    mcp_server.run()