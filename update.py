import asyncio

from enkacard2 import encbanner2

from ENCard.encard.encard import ENCard


async def update_assets() -> None:
    await encbanner2.upload()
    await ENCard().update_assets()


asyncio.run(update_assets())
