from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from asyncio import sleep

import os
from aiofiles import os as aos


app = FastAPI()


@app.get("/tile")
async def tile(x: int, y: int, z: int):
    await sleep(0.2)

    filename = "{}-{}-{}.png".format(z, x, y)
    filepath = os.path.join(".", "tiles", filename)

    file_exists = await aos.path.isfile(filepath)

    if not file_exists:
        raise HTTPException(status_code=404)

    return FileResponse(filepath)
