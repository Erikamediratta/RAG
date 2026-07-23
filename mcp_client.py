import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"

GITHUB_PAT=os.environ["GITHUB_PAT"]

async def main():
    #connect to github mcp server
    client=httpx.AsyncClient(
        headers={"Authorization":f"Bearer {GITHUB_PAT}"}

    )
    async with streamable_http_client(
        GITHUB_MCP_URL,
       http_client=client

    ) as (read,write,_):
        async with ClientSession(read,write) as session:
            await session.initialize()
            #without initialize, cant start a session/use tools

            tools=await session.list_tools()
            print("First 5 tools are: ")
            for tool in tools.tools[:5]:
                print(tool.name,"\n")

            result=await session.call_tool("get_me",{})
            print(result)


asyncio.run(main())