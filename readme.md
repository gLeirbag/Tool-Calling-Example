# Tool Calling

> Tool calling (or function calling) is an ability that wraps around an **LLM** that ables it to interact with environments.

In the present repository, we'll investigate some ways to implement tool calling around a LLM. Python is the chosen language.

## How to Implement Tool Calling

The core idea of tool calling is to bear in mind the **inversion of control** design principle. The responsibility of deciding when to call functions is not of the developer. Instead - with this change in perspective - it must be of the application itself.

Therefore, the LLM has to know in advance which functions it has access to. More than that, the application must include a trigger that start the process of function calling.

One way to implementing this trigger is having the LLM send a signal to the application that wrap itself. This signal could be a **structured json** that contain the information of the function to be called.

In this scenario, the LLM must be informed beforehand that - when sensing that could provide a better answer with tool - should respond with the structured json.

## The Projects

The repository currently have two projects: **Simple Tool Calling** and **Tool Calling with FastMCP**.

Both of the projects has the need of you downloading [Ollama](https://ollama.com). A software that makes easier to use LLM on a local machine.

In the project, the LLM'll interact with an Postgresql database, specifically with a table that exposes the favorite food of some person.

| Name | Food  |
| ---- | ----- |
| John | Pizza |
| Ana  | Sushi |

You don't need to use Postgresql, it should be easy to create some file similar to `postgresql.py` that can be useful in your context.

### Simple Tool Calling

In the first project, we'll implement our own system of tool calling with our tool defined inside the application that wraps around the Ollama api.

### Tool Calling with FastMCP

**MCP** (Model Context Protocol) is a protocol developed by [Anthropic](https://www.anthropic.com) - The Organization behind Cloud AI - that defines a standardization for tool calling.

Using `fastmcp`, we'll create a MCP Server with the same tool we developed in the first project.
A MCP Client also'll be created so we can access our MCP Server tools.

This time, we use the own API of Ollama to use the tools.

## Dependencies

Firstly, you need to install the dependencies of the projects, they are listed in `requirements.txt` file.

On the terminal, inside the project directory do `pip install -r requirements.txt`.

- **psycopg**: Is the driver that we use so we can access our postgresql database;
- **ollama**: An API that facilitates our interaction with Ollama.
- **fastMCP**: A package that abstracts the creation of a MCP server and MCP client.

Please, **create a database table and populate** with some data so we can access with our application.

## What now?

Each project has it own `readme` that explains the idea behind it!