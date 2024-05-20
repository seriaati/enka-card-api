from typing import Literal

from pydantic import BaseModel


class OwnerInfo(BaseModel):
    username: str
    hash: str
    build_id: int


class StarRailCardData(BaseModel):
    uid: int
    lang: str
    template: Literal[1, 2, 3]
    character_id: str
    character_art: str | None = None
    color: str | None = None
    owner: OwnerInfo | None = None


class EnkaCardData(BaseModel):
    uid: int
    lang: str
    character_id: str
    character_art: str | None = None
    template: Literal[1, 2]
    owner: OwnerInfo | None = None


class ENCardData(BaseModel):
    uid: int
    lang: str
    character_id: str
    character_art: str | None = None
    color: str | None = None
    owner: OwnerInfo | None = None


class HattvrEnkaCardData(BaseModel):
    uid: int
    lang: str
    character_id: str
    owner: OwnerInfo | None = None
