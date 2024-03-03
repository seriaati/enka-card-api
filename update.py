import asyncio

from enkacard2 import encbanner2


async def update_assets() -> None:
    await encbanner2.upload()


asyncio.run(update_assets())
