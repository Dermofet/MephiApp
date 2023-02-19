from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.lesson import LessonCreateSchema
from backend.schemas.lesson_translate import LessonTranslateCreateSchema
from backend.services.lesson import LessonService


async def test_create_lesson(
    async_session: AsyncSession, mock_lesson_create_schema: LessonCreateSchema
) -> None:
    lesson_output_schema = await LessonService.create(async_session, mock_lesson_create_schema)

    assert lesson_output_schema.name == mock_lesson_create_schema.name
    assert lesson_output_schema.subgroup == mock_lesson_create_schema.subgroup
    assert lesson_output_schema.group == mock_lesson_create_schema.group
    assert lesson_output_schema.room == mock_lesson_create_schema.room
    assert lesson_output_schema.type == mock_lesson_create_schema.type


async def test_get_lesson_by_id(
    async_session: AsyncSession, mock_lesson_create_schema: LessonCreateSchema
) -> None:
    lesson_output_schema = await LessonService.create(async_session, mock_lesson_create_schema)
    lesson_id = lesson_output_schema.guid

    fetched_lesson = await LessonService.get(async_session, lesson_id)

    assert fetched_lesson.guid == lesson_id
    assert fetched_lesson.name == mock_lesson_create_schema.name


async def test_get_nonexistent_lesson(
    async_session: AsyncSession, nonexistent_lesson_id: UUID
) -> None:
    try:
        await LessonService.get(async_session, nonexistent_lesson_id)
    except HTTPException as error:
        assert error.status_code == 404
        assert error.detail == "Занятие не найдено"
    else:
        assert False, "Expected HTTPException"


async def test_get_lessons_by_group(
    async_session: AsyncSession,
    mock_lesson_create_schema: LessonCreateSchema,
    mock_lesson_translate_create_schema: LessonTranslateCreateSchema,
) -> None:
    group = mock_lesson_create_schema.group
    lang = mock_lesson_create_schema.lang
    await LessonService.create(async_session, mock_lesson_create_schema)
    await LessonService.create(async_session, mock_lesson_create_schema)
    await LessonService.create(async_session, mock_lesson_create_schema)

    fetched_lessons = await LessonService.get_by_group(async_session, group, lang)

    assert len(fetched_lessons) == 3
    for lesson in fetched_lessons:
        assert lesson.group == group
        assert lesson.lang == lang


async def test_get_lessons_by_teacher(
    async_session: AsyncSession,
    mock_lesson_create_schema: LessonCreateSchema,
    mock_lesson_translate_create_schema: LessonTranslateCreateSchema,
) -> None:
    teacher = mock_lesson_create_schema.teacher_name
    lang = mock_lesson_create_schema.lang
    await LessonService.create(async_session, mock_lesson_create_schema)
    await LessonService.create(async_session, mock_lesson_create_schema)
    await LessonService.create(async_session, mock_lesson_create_schema)

    fetched_lessons = await LessonService.get_by_teacher(async_session, teacher, lang)

    assert len(fetched_lessons) == 3
    for lesson in fetched_lessons:
        assert lesson.teacher_name == teacher
        assert lesson.lang == lang


async def test_update_lesson(
    async_session: AsyncSession,
    mock_lesson_create_schema: LessonCreateSchema,
    lesson_changes: dict,
) -> None:
    # Create a new lesson
    lesson = await LessonService.create(async_session, mock_lesson_create_schema)

    # Update the lesson
    updated_lesson = await LessonService.update(
        async_session, lesson.guid, LessonCreateSchema(**lesson_changes)
    )

    # Check that the lesson was updated correctly
    assert updated_lesson.group == lesson_changes["group"]
    assert updated_lesson.type == lesson_changes["type"]
    assert updated_lesson.name == lesson_changes["name"]
    assert updated_lesson.subgroup == lesson_changes["subgroup"]
    assert updated_lesson.lang == lesson_changes["lang"]

    # Check that the original lesson was not changed
    lesson_in_db = await LessonRepository.get_by_id(async_session, lesson.guid)
    assert lesson_in_db.group == mock_lesson_create_schema.group
    assert lesson_in_db.type == mock_lesson_create_schema.type
    assert lesson_in_db.name == mock_lesson_create_schema.name
    assert lesson_in_db.subgroup == mock_lesson_create_schema.subgroup
    assert lesson_in_db.lang == mock_lesson_create_schema.lang
    