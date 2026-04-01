import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
import json

clients = set()

async def handler(websocket):
    try:
        clients.add(websocket)
        async for message in websocket:
            message_text = json.loads(message)
            print(message_text['content'])

            data = json.dumps(message_text)
            task_message = [client.send(data) for client in clients]
            await asyncio.gather(*task_message)

        clients.remove(websocket)
    except ConnectionClosedOK:
        print("A client disconnected.")
        pass

async def main():
    async with serve(handler, "", 8002) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())