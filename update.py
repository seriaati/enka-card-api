import asyncio

from enkanetwork import EnkaNetworkAPI


async def update_assets() -> None:
    async with EnkaNetworkAPI() as client:
        await client.update_assets()


asyncio.run(update_assets())
