import os
import asyncio
import httpx
from dotenv import load_dotenv
load_dotenv()
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from google import genai
from google.genai import types


GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"

GITHUB_PAT=os.environ["GITHUB_PAT"]
import copy

UNSUPPORTED_KEYS = {"additionalProperties", "dependentRequired", "$schema", "examples"}

def clean_schema(schema):
    """Recursively remove fields Gemini's function-calling schema doesn't support."""
    if not isinstance(schema, dict):
        return schema

    cleaned = {}
    for key, value in schema.items():
        if key.startswith("x-") or key in UNSUPPORTED_KEYS:
            continue
        if isinstance(value, dict):
            cleaned[key] = clean_schema(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_schema(v) if isinstance(v, dict) else v for v in value]
        else:
            cleaned[key] = value
    return cleaned

async def run(question):
    async with streamablehttp_client(
        GITHUB_MCP_URL,
        headers={"Authorization":f"Bearer {GITHUB_PAT}"}

    )as (read,write,_):
        async with ClientSession(read,write) as session:
            await session.initialize()
            #Now allowed to list tools or call tools
            



            client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])



            # call gemini to see if it should actually use a tool
            # from github tools listed or give a general response

            mcp_tools =(await session.list_tools()).tools

            #gemini cant call mcp_tools directly, convert them into gemini functionDeclaration

            declarations=[]
            for tool in mcp_tools:
                try:
                    declaration=types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description or "",
                        parameters=clean_schema(tool.inputSchema)
                    )
                    declarations.append(declaration)
                except Exception as e:
                    print(f"Skipping tool '{tool.name}', {e}")

            gemini_tools=types.Tool(
                function_declarations=declarations
            )

            response=client.models.generate_content(
                model="gemini-2.5-flash",
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[gemini_tools],
                     system_instruction=(
            "You are a helpful assistant. You have access to GitHub tools, which you should use "
            "when the question is specifically about GitHub repositories, code, issues, or similar. "
            "For any other question, answer normally using your own general knowledge — "
            "do not refuse to answer just because a GitHub tool doesn't apply."
        )
                ) 

            )
            part = response.candidates[0].content.parts[0]
            if part.function_call:
                tool_name = part.function_call.name
                tool_args = dict(part.function_call.args)

                #execute tool on github mcp server

                tool_result = await session.call_tool(
                        tool_name,
                        tool_args
                    )

                returned=tool_result.content[0].text
                final_response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=(
                            f"Tool result:\n{returned}\n\n"
                            f"Answer this question using the tool result:\n{question}"
                        )
                    )
                return final_response.text
            else:
                return response.text

def tool_agent_node(state):
    answer = asyncio.run(run(state["question"]))
    return {"answer": answer}


if __name__ == "__main__":
    print(asyncio.run(run("Search GitHub for the langgraph repository and tell me about it")))
            

