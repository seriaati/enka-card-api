import asyncio

from EnkaCard.enkacard import encbanner


async def update_assets() -> None:
    await encbanner.update()


asyncio.run(update_assets())
