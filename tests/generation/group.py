from backend.schemas.academic import AcademicOutputSchema
from backend.schemas.group import GroupCreateSchema, GroupOutputSchema
from tests.generation import fake


def generate_group_create_schema() -> CorpsCreateSchema:
    return GroupCreateSchema(
        name=fake.lexify(text="?"*10),
        course=fake.random_int(min=1, max=5),
        academic=fake.lexify(text="?"*10),
    )

def generate_group_output_schema() -> CorpsOutputSchema:
    return GroupOutputSchema(
        name=fake.lexify(text="?"*10),
        course=fake.random_int(min=1, max=5),
        academic=AcademicOutputSchema(name=fake.lexify(text="?"*10)),
    )