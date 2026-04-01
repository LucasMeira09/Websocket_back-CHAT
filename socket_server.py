import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
import json
import os

clients = set()

async def health_check(connection, request):
    upgrade_header = request.headers.get("Upgrade", "")
    if "upgrade" not in upgrade_header.lower():
        return (200, [], b"OK\n")
    return None

async def handler(websocket):
    try:
        clients.add(websocket)
        async for message in websocket:
            message_text = json.loads(message)

            data = json.dumps(message_text)
            task_message = [client.send(data) for client in clients]
            await asyncio.gather(*task_message)

        clients.remove(websocket)
    except ConnectionClosedOK:
        pass

async def main():
    port = int(os.getenv("PORT", 8002))

    async with serve(handler, "0.0.0.0", port, process_request=health_check) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
