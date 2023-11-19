from typing import Dict, List

from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.filters.room import RoomFilter
from backend.api.schemas.room import RoomCreateSchema, RoomOutputSchema, RoomSchema
from backend.api.services.v0_0_1.base_servise import BaseService


class RoomService(BaseService):
    async def create(self, schemas: RoomCreateSchema) -> RoomOutputSchema:
        room = await self.facade.get_by_number_room(schemas.number)
        if room is not None:
            raise HTTPException(409, "Аудитория уже существует")

        corps = await self.facade.get_by_name_corps(name=schemas.corps)
        if corps is None:
            raise HTTPException(404, "Корпус, в котором находится аудитория, не найден")

        room = await self.facade.create_room(schemas, corps_guid=corps.guid)
        await self.facade.commit()

        return RoomOutputSchema(**RoomSchema.model_validate(room).model_dump())

    async def get_by_id(self, guid: UUID4) -> RoomOutputSchema:
        room = await self.facade.get_by_id_room(guid)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutputSchema(**RoomSchema.model_validate(room).model_dump())

    async def get_by_name(self, name: str) -> RoomOutputSchema:
        room = await self.facade.get_by_number_room(name)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutputSchema(**RoomSchema.model_validate(room).model_dump())

    async def get_all(self) -> list[str]:
        rooms = await self.facade.get_all_room()
        if not rooms:
            raise HTTPException(404, "Аудитории не найдены")
        rooms = [room.number for room in rooms]
        rooms.sort()
        return rooms

    async def get_empty(self, room_filter: RoomFilter, corps: list[str]) -> Dict[str, List[Dict]]:
        if not corps:
            raise HTTPException(422, "Не было выбрано ни одного корпуса")

        rooms = await self.facade.get_empty_room(room_filter, corps)
        if rooms is None:
            raise HTTPException(404, "Аудитории не найдены")

        res = [
            {
                "name": room[0],
                "time_start": room[1].strftime("%H:%M"),
                "time_end": room[2].strftime("%H:%M"),
                "corps": room[3],
                "floor": None,
            }
            for room in rooms
        ]
        res.sort(key=lambda x: x["name"])

        return {"rooms": res}

    async def update(self, guid: UUID4, schemas: RoomCreateSchema) -> RoomOutputSchema:
        room = await self.facade.update_room(guid, schemas)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")

        await self.facade.commit()

        return RoomOutputSchema(**RoomSchema.model_validate(room).model_dump())

    async def delete(self, guid: UUID4) -> Response(status_code=204):
        await self.facade.delete_room(guid)
        await self.facade.commit()

        return Response(status_code=204)
