import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
import json
import os

# Set to store connected clients
clients = set()

# Health check endpoint for load balancers or monitoring tools
async def health_check(connection, request):
    if "upgrade" not in request.headers.get("Upgrade", "").lower():
        # répond 200 OK à n'importe quelle requête HTTP (GET, HEAD, etc.)
        # empêche de couper la connexion
        return (200, [("Content-Type", "text/plain"), ("Connection", "close")], b"OK\n")
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
