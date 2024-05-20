from __future__ import annotations

import io
from typing import TYPE_CHECKING

import starrailcard
import uvicorn
from enkacard import encbanner
from enkanetwork import EnkaNetworkAPI, Language
from fastapi import FastAPI, Response

from ENCard.encard import encard
from enka_card import generator
from utils import hex_to_rgb, update_enc_characters

if TYPE_CHECKING:
    from models import ENCardData, EnkaCardData, HattvrEnkaCardData, StarRailCardData


app = FastAPI()


@app.get("/")
async def index() -> Response:
    return Response(content="Enka Card API v1.2.1")


@app.post("/star-rail-card")
async def star_rail_card(data: StarRailCardData) -> Response:
    try:
        async with starrailcard.Card(
            lang=data.lang,
            character_id=data.character_id,
            character_art={data.character_id: data.character_art}
            if data.character_art is not None
            else None,
            user_font="fonts/GenSenRoundedTW-B-01.ttf" if data.lang in {"cn", "cht"} else None,
            color={data.character_id: hex_to_rgb(data.color)} if data.color is not None else None,  # type: ignore [reportArgumentType]
            boost_speed=True,
            asset_save=True,
        ) as draw:
            r = await draw.create(data.uid, style=data.template)
            img = r.card[0].card  # type: ignore [reportIndexIssue]

            bytes_obj = io.BytesIO()
            img.save(bytes_obj, format="WEBP")  # type: ignore [reportAttributeAccessIssue]
            bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/webp")
    except Exception as e:
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
                await update_enc_characters(data, draw)

            r = await draw.creat(template=data.template)
            img = r.card[0].card  # type: ignore

            bytes_obj = io.BytesIO()
            img.save(bytes_obj, format="WEBP")  # type: ignore
            bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/webp")
    except Exception as e:
        return Response(content=str(e), media_type="text/plain", status_code=500)


@app.post("/en-card")
async def en_card(data: ENCardData) -> Response:
    try:
        async with encard.ENCard(
            lang=data.lang,
            character_id=data.character_id,
            character_image={data.character_id: data.character_art}
            if data.character_art is not None
            else None,
            color={data.character_id: hex_to_rgb(data.color)} if data.color is not None else None,
        ) as enc:
            if data.owner is not None:
                await update_enc_characters(data, enc)

            result = await enc.create_cards(data.uid)
            img = result.card[0].card  # type: ignore

            bytes_obj = io.BytesIO()
            img.save(bytes_obj, format="WEBP")
            bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/webp")
    except Exception as e:
        return Response(content=str(e), media_type="text/plain", status_code=500)


@app.post("/hattvr-enka-card")
async def hattvr_enka_card(data: HattvrEnkaCardData) -> Response:
    try:
        async with EnkaNetworkAPI(lang=Language(data.lang)) as client:
            showcase = await client.fetch_user(data.uid)
            character = next(c for c in showcase.characters if c.id == int(data.character_id))
            im = generator.generate_image(showcase, character, client.lang)

            bytes_obj = io.BytesIO()
            im.save(bytes_obj, format="WEBP")
            bytes_obj.seek(0)

        return Response(content=bytes_obj.read(), media_type="image/webp")
    except Exception as e:
        return Response(content=str(e), media_type="text/plain", status_code=500)


uvicorn.run(app, port=7652)
