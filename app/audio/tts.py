import asyncio
from elevenlabs.client import ElevenLabs
from app.config import ELEVENLABS_API_KEY  
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def synthesize(script_text):
    stream = client.text_to_speech.stream(
        text=script_text,
        voice_id="TX3LPaxmHKxFdv7VOQHJ",       
        model_id="eleven_flash_v2_5",
        output_format="mp3_44100_128",
    )
    for chunk in stream:
        yield chunk  



async def test():
    chunks = []
    async for chunk in synthesize("Welcome to Chicago, home of deep dish pizza."):
        print(f"chunk: {len(chunk)} bytes")
        chunks.append(chunk)
    with open("test_audio.mp3", "wb") as f:
        f.write(b"".join(chunks))
    print(f"total: {sum(len(c) for c in chunks)} bytes")

if __name__ == "__main__":
    asyncio.run(test())