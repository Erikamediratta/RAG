import os
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

from tools.doc_tool import search_docs
from tools.erp_tool import get_employee_info, get_tickets, get_assets

GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"
GITHUB_PAT = os.environ["GITHUB_PAT"]

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MAX_STEPS = 5
LOCAL_TOOLS = {    "search_docs": search_docs,    "get_employee_info": get_employee_info,    "get_tickets": get_tickets,    "get_assets": get_assets,} 
# Gemini needs a schema for each tool: its name, what it does in plain
# English, and what arguments it takes. This is how Gemini decides which
# tool (if any) to call for a given question.

LOCAL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="search_docs",
        description=(
            "Search documents for information relevant to the question. If the user has a "
            "specific document currently selected (a technical manual, SOP, resume, report, "
            "etc.), this searches only within that document. If no document is specifically "
            "selected, this searches across all documents that have been uploaded and "
            "embedded so far."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for in the documents"},
            },
            "required": ["query"],
        },
    ),
    types.FunctionDeclaration(
        name="get_employee_info",
        description="Look up an employee's basic info (department, email) by name.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Employee name or ID"},
            },
            "required": ["name"],
        },
    ),
    types.FunctionDeclaration(
        name="get_tickets",
        description="Look up an employee's IT support tickets, optionally filtered by status (Open or Closed).",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Employee name or ID"},
                "status": {"type": "string", "description": "Optional: 'Open' or 'Closed'"},
            },
            "required": ["name"],
        },
    ),
    types.FunctionDeclaration(
        name="get_assets",
        description="Look up equipment (laptops, monitors, etc.) assigned to an employee.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Employee name or ID"},
            },
            "required": ["name"],
        },
    ),
]

UNSUPPORTED_KEYS = {"additionalProperties", "dependentRequired", "$schema", "examples"}


def clean_schema(schema):
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

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to multiple tools: searching internal "
    "technical/SOP documents, looking up employee/ticket/asset records in the "
    "company ERP, and GitHub tools for repositories, code, and issues. "
    "Decide which tool(s), if any, are relevant to the user's question. You may "
    "call more than one tool, one at a time, before giving your final answer. If "
    "no tool is relevant, answer directly from your own knowledge. Always base "
    "your final answer on the tool results you gathered, and say which source "
    "each piece of information came from.“If the user asks about their identity e.g.,' who am I?', always call the get_me tool.")


async def get_answer(question, chat_history=None, document_filter=None):
    history_text = ""
    if chat_history:
        for turn in chat_history:
            history_text = history_text + f"{turn['role']}:{turn['content']}\n"

    contextual_question = question
    if history_text:
        contextual_question = f"Previous conversation:\n{history_text}\nCurrent question: {question}"

    # If a document is selected, inject its context directly
    if document_filter:
        doc_context = search_docs(query=question, document_filter=document_filter)
        contextual_question = (
            f"Document context:\n{doc_context}\n\nQuestion: {question}"
        )

    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(
        GITHUB_MCP_URL,
        headers={"Authorization": f"Bearer {GITHUB_PAT}"},
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = (await session.list_tools()).tools
            RELEVANT_GITHUB_TOOLS = {
                "get_me",
                "search_repositories",
                "search_code",
                "list_issues",
                "get_file_contents",
            }
            mcp_tools = [t for t in mcp_tools if t.name in RELEVANT_GITHUB_TOOLS]

            mcp_declarations = []
            for tool in mcp_tools:
                try:
                    mcp_declarations.append(types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description or "",
                        parameters=clean_schema(tool.inputSchema),
                    ))
                except Exception as e:
                    print(f"Skipping tool '{tool.name}': {e}")

            mcp_tool_names = {tool.name for tool in mcp_tools}
            all_tools = types.Tool(function_declarations=LOCAL_DECLARATIONS + mcp_declarations)

            chat = client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    tools=[all_tools],
                    system_instruction=SYSTEM_PROMPT,
                ),
            )

            decision_trace = []
            response = chat.send_message(contextual_question)

            for step in range(MAX_STEPS):
                part = response.candidates[0].content.parts[0]

                if not part.function_call:
                    return response.text, decision_trace

                tool_name = part.function_call.name
                tool_args = dict(part.function_call.args)

                if tool_name in LOCAL_TOOLS:
                    if tool_name == "search_docs":
                        result = LOCAL_TOOLS[tool_name](**tool_args, document_filter=document_filter)
                    else:
                        result = LOCAL_TOOLS[tool_name](**tool_args)
                elif tool_name in mcp_tool_names:
                    tool_result = await session.call_tool(tool_name, tool_args)
                    result = {"result": tool_result.content[0].text}
                else:
                    result = {"error": f"Unknown tool '{tool_name}'"}

                decision_trace.append({
                    "step": step + 1,
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result,
                })

                response = chat.send_message(
                    types.Part.from_function_response(name=tool_name, response=result)
                )

            return "Reached the reasoning step limit without a final answer.", decision_trace

def orchestrator_node(state):
    answer, decision_trace = asyncio.run(
        get_answer(state["question"], state.get("chat_history"), state.get("document_filter"))
    )
    return {"answer": answer, "decision_trace": decision_trace}


