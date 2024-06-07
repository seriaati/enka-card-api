from __future__ import annotations

from typing import TYPE_CHECKING

from enkanetwork import EnkaNetworkAPI, Language
from starrailcard.src.api.enka import ApiEnkaNetwork

if TYPE_CHECKING:
    from enkanetwork.model import CharacterInfo
    from starrailcard.src.model import api_mihomo

    from models import ENCardData, EnkaCardData, HattvrEnkaCardData, StarRailCardData


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


async def update_hsr_characters(
    data: StarRailCardData, characters: list[api_mihomo.Character]
) -> list[api_mihomo.Character]:
    assert data.owner is not None

    enka = ApiEnkaNetwork(uid=data.uid, lang=data.lang)
    mihomo_data = await enka.get_build(name=data.owner.username, hash=data.owner.hash)
    assert mihomo_data is not None
    build = None
    for c in mihomo_data.characters:
        if c.build is not None and c.build["id"] == data.owner.build_id:
            build = c
            break

    for character in characters:
        if character.id == data.character_id:
            characters.remove(character)
            break

    if build is not None:
        characters.append(build)
    return characters


async def update_enc_characters(
    data: EnkaCardData | ENCardData | HattvrEnkaCardData, characters: list[CharacterInfo]
) -> list[CharacterInfo]:
    assert data.owner is not None

    async with EnkaNetworkAPI(lang=Language(data.lang)) as client:
        builds = await client.fetch_builds(profile_id=data.owner.username, metaname=data.owner.hash)
        character_builds = builds.get_character(data.character_id)
        assert character_builds is not None
        build = next(b for b in character_builds if b.id == data.owner.build_id)

    for character in characters:
        if str(character.id) == data.character_id:
            characters.remove(character)
            break
    characters.append(build.avatar_data)

    return characters
