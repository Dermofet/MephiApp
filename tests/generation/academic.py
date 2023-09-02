from backend.schemas.academic import AcademicCreateSchema, AcademicOutputSchema
from tests.generation import fake


def generate_academic_create_schema() -> AcademicCreateSchema:
    return AcademicCreateSchema(
        name=fake.lexify(text="?"*10),
    )

def generate_academic_output_schema() -> AcademicOutputSchema:
    return AcademicOutputSchema(
        name=fake.lexify(text="?"*10),
    )
