from backend.schemas.teacher_translate import (
    TeacherTranslateCreateSchema,
    TeacherTranslateOutputSchema,
)
from tests.generation import fake


def generate_teacher_translate_create_schema() -> TeacherTranslateCreateSchema:
    return TeacherTranslateCreateSchema(
        teacher_guid=fake.uuid4(),
        lang=fake.language_code(),
        name=fake.name(),
        fullname=fake.name(),
    )

def generate_teacher_translate_output_schema() -> TeacherTranslateOutputSchema:
    return TeacherTranslateOutputSchema(
        lang=fake.language_code(),
        name=fake.name(),
        fullname=fake.name(),
    )