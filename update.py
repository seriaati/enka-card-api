from __future__ import annotations

import asyncio

from enkanetwork import EnkaNetworkAPI
from starrailcard.src.api import enka


async def update_assets() -> None:
    async with EnkaNetworkAPI() as client:
        await client.update_assets()
    await enka.ApiEnkaNetwork().update_assets()


asyncio.run(update_assets())
