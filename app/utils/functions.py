import os
from os.path import exists

import aiofiles


async def save_file(file, location):
    async with aiofiles.open(location, "wb") as f:
        while content := await file.read(1024):  # Read file in chunks
            await f.write(content)
    return {"info": f"file '{file.filename}' saved at '{location}'"}


async def update_file(file, old_location, location):
    if exists(old_location):
        if old_location == location:
            return
        os.remove(old_location)
    async with aiofiles.open(location, "wb") as f:
        while content := await file.read(1024):  # Read file in chunks
            await f.write(content)
    return


