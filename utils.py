from __future__ import annotations

from typing import TYPE_CHECKING

from enkanetwork import EnkaNetworkAPI, Language

if TYPE_CHECKING:
    from enkanetwork.model import CharacterInfo

    from models import ENCardData, EnkaCardData, HattvrEnkaCardData


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


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
