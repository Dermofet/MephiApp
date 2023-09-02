from backend.schemas.corps import CorpsOutputSchema
from backend.schemas.room import RoomCreateSchema, RoomOutputSchema
from tests.generation import fake


def generate_room_create_schema() -> RoomCreateSchema:
    return RoomCreateSchema(
        number=fake.lexify(text="?"*10),
        corps=fake.lexify(text="?"*10),
    )

def generate_room_output_schema() -> RoomOutputSchema:
    return RoomOutputSchema(
        number=fake.lexify(text="?"*10),
        corps=CorpsOutputSchema(
            name=fake.lexify(text="?"*10),
        )
    )