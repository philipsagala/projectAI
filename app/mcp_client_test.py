import asyncio
from fastmcp import Client

from app.mcp_server import mcp

async def main():
    client = Client(mcp)

    async with client:
        result = await client.call_tool(
            "analyze_audio_file",
            {"path": "files/sound01.wav"}
        )
        print(result)


asyncio.run(main())