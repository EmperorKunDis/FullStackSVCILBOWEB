from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import ReturnDocument

from uuid import uuid4
from datetime import datetime

from pydantic import BaseModel


class KingdomSummary(BaseModel):
    id: str
    name: str
    clan_count: int

    @staticmethod
    def from_doc(doc) -> "KingdomSummary":
        return KingdomSummary(
            id=str(doc["_id"]),
            name=doc["name"],
            clanCount=doc[clanCount],
        )

class ClanSummary(BaseModel):
    id: str
    name: str
    member_count: int

    @staticmethod
    def from_doc(doc) -> "ClanSummary":
        return ClanSummary(
            id=str(doc["_id"]),
            name=doc["name"],
            memberCount=doc["memberCount"],
        )



class Clan(BaseModel):
    id: str
    name: str
    description: str

    @staticmethod
    def from_doc(doc) -> "Clan":
        return Clan(
            id=str(doc["_id"]),
            name=doc["clanName"],
            description=doc.get("description", ""),
        )


class Member(BaseModel):
    id: str
    nickname: str
    email: str
    password: str
    rank: str
    member_of: list[str]
    status: str
    registration_date: datetime
    last_login: datetime
    description: str
    phone: str
    image_access: bool
    info_access: bool
    manage_access: bool
    media_access: bool

    @staticmethod
    def from_doc(doc) -> "Member":
        return Member(
            id=str(doc["_id"]),
            nickname=doc["nickname"],
            email=doc.get("email", ""),
            password=doc.get("password", ""),
            rank=doc.get("rank", ""),
            member_of=list(filter(None, doc.get("memberOf", []))),
            status=doc.get("status", ""),
            registration_date=datetime.fromisoformat(doc.get("registrationDate", "")),
            last_login=datetime.fromisoformat(doc.get("lastLogin", "")),
            description=doc.get("description", ""),
            phone=doc.get("phone", ""),
            image_access=bool(doc.get("imageAccess", False)),
            info_access=bool(doc.get("infoAccess", False)),
            manage_access=bool(doc.get("manageAccess", False)),
            media_access=bool(doc.get("mediaAccess", False)),
        )


class KingdomDAL:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._kingdom_collection = db["kingdoms"]
        self._clan_collection = db["clans"]

    async def list_kingdoms(self) -> list[KingdomSummary]:
        kingdoms = []
        cursor = self._kingdom_collection.find({}, {"name": 1})
        async for doc in cursor:
            kingdom = KingdomSummary.from_doc(doc)
            clans = await self.list_clans(kingdom.id)
            kingdom.clan_count = len(clans)
            kingdoms.append(kingdom)
        return kingdoms

    async def create_kingdom(self, name: str) -> str:
        result = await self._kingdom_collection.insert_one({"name": name})
        return str(result.inserted_id)

    async def get_kingdom(self, id: str | ObjectId) -> dict:
        doc = await self._kingdom_collection.find_one({"_id": ObjectId(id)})
        if doc:
            clans = await self.list_clans(doc["_id"])
            for clan in clans:
                clan["armyMembers"] = [
                    ArmyMember.from_doc(member).dict()
                    for member in clan.get("armyMembers", [])
                ]
            doc["clans"] = [Clan.from_doc(clan).dict() for clan in clans]
        return doc

    async def delete_kingdom(self, id: str | ObjectId) -> bool:
        result = await self._kingdom_collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count == 1

    async def create_clan(
        self, kingdom_id: str | ObjectId, clan_name: str, description: str
    ) -> Clan | None:
        response = await self._clan_collection.insert_one(
            {
                "_id": ObjectId(),
                "kingdomId": ObjectId(kingdom_id),
                "clanName": clan_name,
                "description": description,
                "armyMembers": [],
            }
        )
        if response.acknowledged:
            return Clan.from_doc(await self.get_clan(str(response.inserted_id)))

    async def get_clan(self, id: str | ObjectId) -> Clan | None:
        doc = await self._clan_collection.find_one({"_id": ObjectId(id)})
        if doc:
            clan = Clan.from_doc(doc)
            clan.armyMembers = [
                ArmyMember.from_doc(member).dict()
                for member in doc.get("armyMembers", [])
            ]
            return clan.dict()
        return None

    async def delete_clan(self, id: str | ObjectId) -> bool:
        result = await self._clan_collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count == 1

    async def add_armymember(
        self,
        clan_id: str | ObjectId,
        nickname: str,
        email: str,
        password: str,
        rank: str,
    ) -> ArmyMember:
        new_member = {
            "_id": ObjectId(),
            "nickname": nickname,
            "email": email,
            "password": password,
            "rank": rank,
            "memberOf": [str(clan_id)],
            "status": "",
            "registrationDate": datetime.now(),
            "lastLogin": datetime.now(),
            "description": "",
            "phone": "",
            "imageAccess": False,
            "infoAccess": False,
            "manageAccess": False,
            "mediaAccess": False,
        }
        response = await self._clan_collection.update_one(
            {"_id": ObjectId(clan_id)},
            {"$push": {"armyMembers": new_member}},
            upsert=False,
        )
        if response.modified_count > 0:
            return ArmyMember.from_doc(new_member)

    async def remove_armymember(self, clan_id: str | ObjectId, member_id: str) -> bool:
        result = await self._clan_collection.update_one(
            {"_id": ObjectId(clan_id)},
            {"$pull": {"armyMembers": {"_id": ObjectId(member_id)}}},
        )
        return result.modified_count > 0

    async def list_clans(self, kingdom_id: str | ObjectId) -> list[Clan]:
        clans = []
        cursor = self._clan_collection.find({"kingdomId": ObjectId(kingdom_id)})
        async for doc in cursor:
            clan = Clan.from_doc(doc)
            clan.armyMembers = [
                ArmyMember.from_doc(member).dict()
                for member in doc.get("armyMembers", [])
            ]
            clans.append(clan.dict())
        return clans

    async def update_armymember(
        self,
        clan_id: str | ObjectId,
        member_id: str,
        nickname: str,
        email: str,
        password: str,
        rank: str,
        status: str,
        registration_date: datetime,
        last_login: datetime,
        description: str,
        phone: str,
        image_access: bool,
        info_access: bool,
        manage_access: bool,
        media_access: bool,
    ) -> ArmyMember:
        response = await self._clan_collection.update_one(
            {"_id": ObjectId(clan_id)},
            {
                "$set": {
                    "armyMembers.$[member].nickname": nickname,
                    "armyMembers.$[member].email": email,
                    "armyMembers.$[member].password": password,
                    "armyMembers.$[member].rank": rank,
                    "armyMembers.$[member].status": status,
                    "armyMembers.$[member].registrationDate": registration_date,
                    "armyMembers.$[member].lastLogin": last_login,
                    "armyMembers.$[member].description": description,
                    "armyMembers.$[member].phone": phone,
                    "armyMembers.$[member].imageAccess": image_access,
                    "armyMembers.$[member].infoAccess": info_access,
                    "armyMembers.$[member].manageAccess": manage_access,
                    "armyMembers.$[member].mediaAccess": media_access,
                }
            },
            array_filters=[{"member._id": ObjectId(member_id)}],
        )
        if response.modified_count > 0:
            member = await self.get_armymember(clan_id, member_id)
            return ArmyMember.from_doc(member)

    async def get_armymember(self, clan_id: str | ObjectId, member_id: str) -> dict:
        cursor = self._clan_collection.find(
            {"_id": ObjectId(clan_id)}, {"armyMembers.$[member]": 1}
        )
        result = await cursor.aggregate(
            [{"$match": {"armyMembers.member._id": ObjectId(member_id)}}]
        ).to_list(1)
        if result:
            return result[0]["armyMembers"][0]
        return None

    async def update_clan(
        self, clan_id: str | ObjectId, name: str = None, description: str = None
    ) -> Clan | None:
        """
        Aktualizuje záznam skupiny (clanu).

        :param clan_id: ID skupiny pro aktualizaci.
        :param name: Nový název skupiny.
        :param description: Nový popis skupiny.
        :return: Změněné záznamy skupiny, pokud byla vytvořena změna; Jinak None.
        """

        # Sestavíme aktualizované pole na základě předaných parametrů
        update_fields = {}
        if name:
            update_fields["clanName"] = name
        if description is not None:
            update_fields["description"] = description

        result = await self._clan_collection.find_one_and_update(
            {"_id": ObjectId(clan_id)},
            {"$set": update_fields},
            return_document=ReturnDocument.AFTER,
        )

        # Pokud byla nalezena a aktualizována skupina, vrátíme změněné záznamy
        if result:
            clan = Clan.from_doc(result)
            clan.armyMembers = [
                ArmyMember.from_doc(member).dict()
                for member in result.get("armyMembers", [])
            ]
            return clan.dict()
