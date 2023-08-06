from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import random
from io import BytesIO
from PIL import Image
from asyncio import sleep

width = 256
height = 256

app = FastAPI()


def get_rnd_color():
    return tuple([random.choice(range(255)) for _ in range(3)])


@app.get("/tile")
async def tile(x: int, y: int, z: int):
    await sleep(0.2)
    output = BytesIO()
    img = Image.new(
        mode="RGB",
        size=(width, height),
        color=get_rnd_color()
    )
    img.save(output, format="JPEG")
    output.seek(0)
    return StreamingResponse(output, media_type="image/jpeg")
