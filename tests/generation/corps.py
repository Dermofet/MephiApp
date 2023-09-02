from backend.schemas.corps import CorpsCreateSchema, CorpsOutputSchema
from tests.generation import fake


def generate_corps_create_schema() -> CorpsCreateSchema:
    return CorpsCreateSchema(
        name=fake.lexify(text="?"*10),
    )

def generate_corps_output_schema() -> CorpsOutputSchema:
    return CorpsOutputSchema(
        name=fake.lexify(text="?"*10),
    )