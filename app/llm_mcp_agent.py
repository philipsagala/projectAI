from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI

from app.mcp_server import mcp


load_dotenv()


TOOLS = [
    {
        "type": "function",
        "name": "analyze_audio_file",
        "description": "Analyze an audio file and return metadata, audio quality metrics, issues, and suggested actions.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the audio file to analyze."
                }
            },
            "required": ["path"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "detect_silence",
        "description": "Detect silence segments in an audio file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the audio file."
                }
            },
            "required": ["path"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "detect_clipping",
        "description": "Detect possible clipping using heuristic audio metrics.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the audio file."
                }
            },
            "required": ["path"],
            "additionalProperties": False
        }
    },
]


async def call_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    client = Client(mcp)

    async with client:
        result = await client.call_tool(tool_name, arguments)

    if result.structured_content:
        return result.structured_content

    if result.data:
        return result.data

    return {
        "raw_result": str(result)
    }


async def run_agent(user_request: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing.")

    openai_client = OpenAI(api_key=api_key)

    system_prompt = """
You are an audio quality analysis agent.

You can call MCP-backed tools to analyze audio files.
Use tools when the user asks about an audio file.

Rules:
- Do not invent audio findings.
- Base your answer on tool results.
- If the tool returns issues, explain them clearly.
- If no issues are found, say the audio is generally usable.
- Mention that clipping detection is heuristic-based when relevant.
- Keep the final answer concise and professional.
""".strip()

    response = openai_client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_request,
            },
        ],
        tools=TOOLS,
    )

    tool_outputs = []

    for item in response.output:
        if item.type == "function_call":
            tool_name = item.name
            tool_args = json.loads(item.arguments)

            tool_result = await call_mcp_tool(tool_name, tool_args)

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(tool_result),
                }
            )

    if not tool_outputs:
        return response.output_text

    final_response = openai_client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_request,
            },
            *response.output,
            *tool_outputs,
        ],
    )

    return final_response.output_text


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the audio file to analyze")
    parser.add_argument(
        "--output_dir",
        default="output",
        help="Output directory (default: output/)"
    )
    args = parser.parse_args()

    input_path = Path(args.path)
    file_stem = input_path.stem

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    user_request = (
        f"Analyze this court deposition audio file and tell me whether it is usable, "
        f"risky, or poor. File path: {args.path}"
    )

    result = asyncio.run(run_agent(user_request))

    # Text output
    text_output_path = output_dir / f"agent_{file_stem}.txt"
    text_output_path.write_text(result, encoding="utf-8")

    # JSON output (optional but recommended)
    json_output_path = output_dir / f"agent_{file_stem}.json"
    json_output_path.write_text(
        json.dumps({"result": result}, indent=2),
        encoding="utf-8"
    )

    print(f"✅ Text saved to: {text_output_path}")
    print(f"✅ JSON saved to: {json_output_path}")