import io
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import uvicorn
from enkacard2 import encbanner2
from enkanetwork import EnkaNetworkAPI, Language
from fastapi import FastAPI, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from ENCard.encard import encard
from enka_card import generator
from StarRailCard.starrailcard import honkaicard

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from PIL import Image


class StarRailCardData(BaseModel):
    uid: int
    lang: str
    template: int
    character_name: str
    character_art: str | None = None


class EnkaCardData(BaseModel):
    uid: int
    lang: str
    character_id: str
    character_art: str | None = None
    template: int


class ENCardData(BaseModel):
    uid: int
    lang: str
    character_name: str
    character_art: str | None = None


class HattvrEnkaCardData(BaseModel):
    uid: int
    lang: str
    character_id: str


@asynccontextmanager
async def lifespan(_: FastAPI) -> "AsyncGenerator[None, Any]":
    FastAPICache.init(InMemoryBackend(), expire=60)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index() -> Response:
    return Response(content="Enka Card API v1.2.0")


@app.post("/star-rail-card")
@cache()
async def star_rail_card(data: StarRailCardData) -> Response:
    async with honkaicard.MiHoMoCard(
        lang=data.lang,
        template=data.template,
        characterName=data.character_name,
        characterImgs={data.character_name: data.character_art}
        if data.character_art is not None
        else None,
        font="StarRailCard/starrailcard/src/assets/font/GenSenRoundedTW-B-01.ttf"
        if data.lang in {"cn", "cht"}
        else None,
    ) as draw:
        r = await draw.creat(data.uid)
        img = r.card[0].card  # type: ignore

        bytes_obj = io.BytesIO()
        img.save(bytes_obj, format="WEBP")
        bytes_obj.seek(0)

    return Response(content=bytes_obj.read(), media_type="image/webp")


@app.post("/enka-card")
@cache()
async def enka_card(data: EnkaCardData) -> Response:
    async with encbanner2.ENC(
        lang=data.lang,
        uid=data.uid,
        character_id=data.character_id,
        character_art={data.character_id: data.character_art}
        if data.character_art is not None
        else None,
    ) as draw:
        r = await draw.creat(template=data.template)
        img: Image.Image = r.card[0].card  # type: ignore

        bytes_obj = io.BytesIO()
        img.save(bytes_obj, format="WEBP")
        bytes_obj.seek(0)

    return Response(content=bytes_obj.read(), media_type="image/webp")


@app.post("/en-card")
@cache()
async def en_card(data: ENCardData) -> Response:
    async with encard.ENCard(
        lang=data.lang,
        characterName=data.character_name,
        characterImgs={data.character_name: data.character_art}
        if data.character_art is not None
        else None,
    ) as enc:
        result = await enc.create_cards(data.uid)
        img = result.card[0].card  # type: ignore

        bytes_obj = io.BytesIO()
        img.save(bytes_obj, format="WEBP")
        bytes_obj.seek(0)

    return Response(content=bytes_obj.read(), media_type="image/webp")


@app.post("/hattvr-enka-card")
@cache()
async def hattvr_enka_card(data: HattvrEnkaCardData) -> Response:
    async with EnkaNetworkAPI(lang=Language(data.lang)) as client:
        showcase = await client.fetch_user(data.uid)
        character = next(c for c in showcase.characters if c.id == int(data.character_id))
        im = generator.generate_image(showcase, character, client.lang)

        bytes_obj = io.BytesIO()
        im.save(bytes_obj, format="WEBP")
        bytes_obj.seek(0)

    return Response(content=bytes_obj.read(), media_type="image/webp")


@app.post("/en-card-profile")
@cache()
async def en_card_profile(
    data: ENCardData,
) -> Response:
    async with encard.ENCard(lang=data.lang) as enc:
        result = await enc.create_profile(data.uid)
        img = result.card  # type: ignore

        bytes_obj = io.BytesIO()
        img.save(bytes_obj, format="WEBP")
        bytes_obj.seek(0)

    return Response(content=bytes_obj.read(), media_type="image/webp")


uvicorn.run(app, port=7652)
