from teacher_translate import generate_teacher_translate_output_schema

from backend.schemas.teacher import TeacherCreateSchema, TeacherOutputSchema
from tests.generation import fake


def generate_teacher_create_schema() -> TeacherCreateSchema:
    return TeacherCreateSchema(
        online_url=fake.url(),
        alt_online_url=fake.url(),
        lang=fake.language_code(),
        name=fake.name(),
        fullname=fake.name(),
    )

def generate_teacher_output_schema() -> TeacherOutputSchema:
    return TeacherOutputSchema(
        online_url=fake.url(),
        alt_online_url=fake.url(),
        trans=generate_teacher_translate_output_schema(),
    )