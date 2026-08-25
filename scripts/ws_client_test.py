import asyncio, websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8000/ws/audio") as ws:
        await ws.send("Welcome to Chicago, home of deep dish pizza.")
        chunks = []
        async for chunk in ws:          # receives binary frames
            chunks.append(chunk)
        with open("ws_out.mp3", "wb") as f:
            f.write(b"".join(chunks))
        print(f"received {len(chunks)} chunks")

asyncio.run(main())