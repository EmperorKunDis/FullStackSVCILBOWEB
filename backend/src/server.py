from contextlib import asynccontextmanager
from datetime import datetime
import os
import sys

from bson import ObjectId
from fastapi import FastAPI, status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import uvicorn

# Import models and DAL from your project
from dal import KingdomDAL, KingdomSummary, Clan, ArmyMember


COLLECTION_NAME_KINGDOMS = "kingdoms"
COLLECTION_NAME_CLANS = "clans"
MONGODB_URI = os.environ["MONGODB_URI"]
DEBUG = os.environ.get("DEBUG", "").strip().lower() in {"1", "true", "on", "yes"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    client = AsyncIOMotorClient(MONGODB_URI)
    database = client.get_default_database()

    # Ensure the database is available:
    pong = await database.command("ping")
    if int(pong["ok"]) != 1:
        raise Exception("Cluster connection is not okay!")

    kingdoms_collection = database.get_collection(COLLECTION_NAME_KINGDOMS)
    clans_collection = database.get_collection(COLLECTION_NAME_CLANS)

    # Initialize DAL
    app.kingdom_dal = KingdomDAL(kingdoms_collection, clans_collection)

    yield

    client.close()


app = FastAPI(lifespan=lifespan, debug=DEBUG)


@app.get("/api/kingdoms")
async def get_all_kingdoms() -> list[KingdomSummary]:
    return [i async for i in app.kingdom_dal.list_kingdoms()]


class NewKingdom(BaseModel):
    name: str


class NewKingdomResponse(BaseModel):
    id: str
    name: str


@app.post("/api/kingdoms", status_code=status.HTTP_201_CREATED)
async def create_new_kingdom(new_kingdom: NewKingdom) -> NewKingdomResponse:
    return NewKingdomResponse(
        id=await app.kingdom_dal.create_kingdom(new_kingdom.name),
        name=new_kingdom.name,
    )


@app.get("/api/kingdoms/{kingdom_id}")
async def get_kingdom(kingdom_id: str) -> KingdomSummary:
    return await app.kingdom_dal.get_kingdom(ObjectId(kingdom_id))


@app.delete("/api/kingdoms/{kingdom_id}")
async def delete_kingdom(kingdom_id: str) -> bool:
    return await app.kingdom_dal.delete_kingdom(ObjectId(kingdom_id))


class NewClan(BaseModel):
    clan_name: str
    description: str


class NewClanResponse(BaseModel):
    id: str
    name: str
    description: str


@app.post(
    "/api/kingdoms/{kingdom_id}/clans",
    status_code=status.HTTP_201_CREATED,
)
async def create_new_clan(kingdom_id: str, new_clan: NewClan) -> Clan:
    return await app.kingdom_dal.create_clan(
        ObjectId(kingdom_id), new_clan.clan_name, new_clan.description
    )


@app.get("/api/kingdoms/{kingdom_id}/clans")
async def get_all_clans_of_kingdom(kingdom_id: str) -> list[Clan]:
    return await app.kingdom_dal.list_clans(ObjectId(kingdom_id))


@app.delete("/api/clans/{clan_id}")
async def delete_clan(clan_id: str) -> bool:
    return await app.kingdom_dal.delete_clan(ObjectId(clan_id))


class NewArmyMember(BaseModel):
    nickname: str
    email: str
    password: str
    rank: str


@app.post(
    "/api/clans/{clan_id}/members",
    status_code=status.HTTP_201_CREATED,
)
async def create_armymember(clan_id: str, new_member: NewArmyMember) -> ArmyMember:
    return await app.kingdom_dal.add_armymember(
        ObjectId(clan_id),
        new_member.nickname,
        new_member.email,
        new_member.password,
        new_member.rank,
    )


@app.delete("/api/clans/{clan_id}/members/{member_id}")
async def delete_armymember(clan_id: str, member_id: str) -> bool:
    return await app.kingdom_dal.remove_armymember(ObjectId(clan_id), member_id)


class ArmyMemberUpdate(BaseModel):
    nickname: str
    email: str
    password: str
    rank: str
    status: str
    registration_date: datetime
    last_login: datetime
    description: str
    phone: str
    image_access: bool
    info_access: bool
    manage_access: bool
    media_access: bool


@app.patch("/api/clans/{clan_id}/members/{member_id}")
async def update_armymember(
    clan_id: str, member_id: str, update: ArmyMemberUpdate
) -> ArmyMember:
    return await app.kingdom_dal.update_armymember(
        ObjectId(clan_id),
        member_id,
        update.nickname,
        update.email,
        update.password,
        update.rank,
        update.status,
        update.registration_date,
        update.last_login,
        update.description,
        update.phone,
        update.image_access,
        update.info_access,
        update.manage_access,
        update.media_access,
    )


def main(argv=sys.argv[1:]):
    try:
        uvicorn.run("server:app", host="0.0.0.0", port=3001, reload=DEBUG)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
