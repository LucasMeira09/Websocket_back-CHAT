import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
from websockets.http11 import Response, Headers
import json
import os

# Set to store connected clients
clients = set()

# Health check endpoint for load balancers or monitoring tools
async def health_check(connection, request):
    if request.header.get("Upgrade", "").lower() != "websocket":
        headers = Headers[("Content-Type", "text/plain"), ("Content-Length", "2"), ("Connection", "close")]
        return Response(200, "OK", headers, b"OK")
    return None

# WebSocket handler to manage client connections and broadcast messages
async def handler(websocket):
    try:
        clients.add(websocket)
        async for message in websocket:
            message_text = json.loads(message)

            data = json.dumps(message_text)
            task_message = [client.send(data) for client in clients]
            await asyncio.gather(*task_message)

    except ConnectionClosedOK:
        pass
    finally:
        clients.remove(websocket)

# Main function to start the WebSocket server
async def main():
    port = int(os.getenv("PORT", 8002))

    async with serve(handler, "0.0.0.0", port, process_request=health_check) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
