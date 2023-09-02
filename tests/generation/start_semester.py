from backend.schemas.start_semester import (
    StartSemesterCreateSchema,
    StartSemesterOutputSchema,
)
from tests.generation import fake


def generate_start_semester_create_schema() -> StartSemesterCreateSchema:
    return StartSemesterCreateSchema(
        date=fake.date(),
    )

def generate_start_semester_output_schema() -> StartSemesterOutputSchema:
    return StartSemesterOutputSchema(
        date=fake.date(),
    )