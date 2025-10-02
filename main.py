from __future__ import annotations

import asyncio
import io
import logging
import os
import tomllib
import warnings
from pathlib import Path

import sentry_sdk
import starrailcard
import uvicorn
from dotenv import load_dotenv
from enkacard import encbanner
from enkanetwork import EnkaNetworkAPI, Language
from fastapi import FastAPI, Response
from starrailcard.src.api.enka import ApiEnkaNetwork

from ENCard.encard import encard
from enka_card import generator
from models import ENCardData, EnkaCardData, HattvrEnkaCardData, StarRailCardData
from utils import hex_to_rgb, setup_logging, update_enc_characters, update_hsr_characters

load_dotenv()
setup_logging()

warnings.filterwarnings("ignore")
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), send_default_pii=True)

app = FastAPI()
logger = logging.getLogger("uvicorn")


def get_version() -> str:
    """Get version from pyproject.toml"""
    try:
        with Path("pyproject.toml").open("rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except (FileNotFoundError, KeyError):
        return "unknown"


@app.get("/")
async def index() -> Response:
    return Response(content=f"Enka Card API v{get_version()}")


@app.post("/star-rail-card")
async def star_rail_card(data: StarRailCardData) -> Response:
    try:
        character_art = (
            {data.character_id: data.character_art} if data.character_art is not None else None
        )
        user_font = "fonts/GenSenRoundedTW-B-01.ttf" if data.lang in {"cn", "cht"} else None
        color = {data.character_id: hex_to_rgb(data.color)} if data.color is not None else None

        if data.cookies is not None:
            cookie_pairs = data.cookies.split("; ")
            cookie_dict = dict(pair.split("=", 1) for pair in cookie_pairs)
            async with starrailcard.HoYoCard(
                cookie_dict,
                lang=data.lang,
                character_art=character_art,
                character_id=data.character_id,
                color=color,  # type: ignore [reportArgumentType]
                boost_speed=True,
                asset_save=True,
            ) as draw:
                r = await draw.create(data.uid, style=data.template)
        else:
            enka = ApiEnkaNetwork(uid=data.uid, lang=data.lang)
            api_data = await enka.get()
            if api_data is None:
                msg = "Failed to get data from API, please try again"
                raise ValueError(msg)  # noqa: TRY301

            if data.owner is not None:
                api_data.characters = await update_hsr_characters(data, api_data.characters)

            async with starrailcard.Card(
                lang=data.lang,
                character_id=data.character_id,
                character_art=character_art,
                user_font=user_font,
                color=color,  # type: ignore [reportArgumentType]
                boost_speed=True,
                asset_save=True,
                api_data=api_data,
            ) as draw:
                r = await draw.create(data.uid, style=data.template)

        img = r.card[0].card  # type: ignore [reportIndexIssue]

        bytes_obj = io.BytesIO()
        img.save(bytes_obj, format="PNG")  # type: ignore [reportAttributeAccessIssue]
        bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/png")
    except Exception as e:
        logger.exception("StarRailCard error")
        return Response(content=str(e), media_type="text/plain", status_code=500)


@app.post("/enka-card")
async def enka_card(data: EnkaCardData) -> Response:
    try:
        async with encbanner.ENC(
            lang=data.lang,
            uid=data.uid,
            character_id=data.character_id,
            character_art={data.character_id: data.character_art}
            if data.character_art is not None
            else None,
        ) as draw:
            if data.owner is not None:
                assert draw.enc is not None
                draw.enc.characters = await update_enc_characters(data, draw.enc.characters)

            r = await draw.creat(template=data.template)
            img = r.card[0].card  # type: ignore

            bytes_obj = io.BytesIO()
            img.save(bytes_obj, format="PNG")  # type: ignore
            bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/png")
    except Exception as e:
        logger.exception("EnkaCard error")
        return Response(content=str(e), media_type="text/plain", status_code=500)


@app.post("/en-card")
async def en_card(data: ENCardData) -> Response:
    try:
        async with encard.ENCard(
            uid=data.uid,
            lang=data.lang,
            character_id=data.character_id,
            character_image={data.character_id: data.character_art}
            if data.character_art is not None
            else None,
            color={data.character_id: hex_to_rgb(data.color)} if data.color is not None else None,
        ) as draw:
            if data.owner is not None:
                assert draw.enc is not None
                draw.enc.characters = await update_enc_characters(data, draw.enc.characters)

            result = await draw.create_cards(data.uid)
            img = result.card[0].card  # type: ignore

            bytes_obj = io.BytesIO()
            img.save(bytes_obj, format="PNG")
            bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/png")
    except Exception as e:
        logger.exception("ENCard error")
        return Response(content=str(e), media_type="text/plain", status_code=500)


@app.post("/hattvr-enka-card")
async def hattvr_enka_card(data: HattvrEnkaCardData) -> Response:
    try:
        async with EnkaNetworkAPI(lang=Language(data.lang)) as client:
            showcase = await client.fetch_user(data.uid)
            if data.owner is not None:
                showcase.characters = await update_enc_characters(data, showcase.characters)

            character = next(c for c in showcase.characters if c.id == int(data.character_id))
            im = await asyncio.to_thread(generator.generate_image, showcase, character, client.lang)

            bytes_obj = io.BytesIO()
            im.save(bytes_obj, format="PNG")
            bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/png")
    except Exception as e:
        logger.exception("Hattvr Enka card error")
        return Response(content=str(e), media_type="text/plain", status_code=500)


uvicorn.run(app, port=7652)
