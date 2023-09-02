from group import generate_group_output_schema
from lesson_translate import generate_lesson_translate_output_schema
from room import generate_room_output_schema
from teacher import generate_teacher_output_schema
from utils import generate_random_bool

from tests.generation import fake


def generate_lesson_create_schema() -> LessonCreateSchema:
    return LessonCreateSchema(
        time_start=fake.time(pattern="HH:mm"),
        time_end=fake.time(pattern="HH:mm"),
        dot=generate_random_bool(),
        weeks=fake.random_int(min=0, max=2),
        day=fake.day_of_week(),
        date_start=fake.date(),
        date_end=fake.date(),
        type=fake.random_choices(elements=["пр","лек","лаб"], length=1)[0],
        name=fake.lexify(text="?"*10),
        subgroup=fake.lexify(text="?"*10),
        group=fake.lexify(text="?"*10),
        course=fake.random_int(min=1, max=5),
        room=fake.lexify(text="?"*10),
        academic=fake.lexify(text="?"*10),
        teacher_name=fake.name(),
        lang="ru",
    )

def generate_lesson_output_schema() -> LessonOutputSchema:
    return LessonOutputSchema(
        time_start=fake.time(pattern="HH:mm"),
        time_end=fake.time(pattern="HH:mm"),
        dot=generate_random_bool(),
        day=fake.day_of_week(),
        date_start=fake.date(),
        date_end=fake.date(),
        weeks=fake.random_choice(elements=[list(range(2, 16, 2)), list(range(1, 15, 2)), list(range(1, 16))], length=1)[0],
        trans=generate_lesson_translate_output_schema(),
        groups=[generate_group_output_schema() for _ in range(fake.random_int(min=1, max=3))],
        teachers=[generate_teacher_output_schema() for _ in range(fake.random_int(min=1, max=3))],
        rooms=[generate_room_output_schema() for _ in range(fake.random_int(min=1, max=3))],
    )