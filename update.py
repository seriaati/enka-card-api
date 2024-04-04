import asyncio

from enkacard2 import encbanner2

from ENCard.encard.src.tools.namecard_map import update_data


async def update_assets() -> None:
    await encbanner2.upload()
    await update_data()


asyncio.run(update_assets())
