from backend.schemas.lesson_translate import (
    LessonTranslateCreateSchema,
    LessonTranslateOutputSchema,
)
from tests.generation import fake


def generate_lesson_translate_create_schema() -> LessonTranslateCreateSchema:
    return LessonTranslateCreateSchema(
        lesson_guid=fake.uuid4(),
        type=fake.random_choices(elements=["пр","лек","лаб"], length=1)[0],
        name=fake.lexify(text="?"*10),
        subgroup=fake.lexify(text="?"*10),
        lang="ru",
    )

def generate_lesson_translate_output_schema() -> LessonTranslateOutputSchema:
    return LessonTranslateOutputSchema(
        type=fake.random_choices(elements=["пр", "лек", "лаб"], length=1)[0],
        name=fake.lexify(text="?"*10),
        subgroup=fake.lexify(text="?"*10),
        lang="ru",
    )