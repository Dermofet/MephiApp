import pytest
from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.academic import AcademicModel
from backend.repositories.academic import AcademicRepository
from tests.generation.academic import (
    generate_academic_create_schema,
    generate_academic_output_schema,
)


class TestAcademicRepository:
    repo = AcademicRepository()

    @pytest.mark.anyio
    async def test_create(self, session):
        input_ = generate_academic_create_schema()

        output = await self.repo.create(session, input_)
        assert output.name == input_.name

    # @pytest.mark.anyio
    # async def test_bulk_insert(self, session):
    #     input_ = [generate_academic_create_schema() for _ in range(10)]
    #     await self.repo.bulk_insert(session, input_)
    #
    #     output = await session.execute(select(AcademicModel.name))
    #     assert len(await session.execute(select(AcademicModel))) == 10
    #
    #     in_set = {i.name for i in input_}
    #     out_set = {i.name for i in output}
    #     assert in_set == out_set
    #
    # @pytest.mark.anyio
    # async def test_get_by_id(self, session):
    #     academic_in = generate_academic_create_schema()
    #     academic_out = await self.repo.create(session, academic_in)
    #
    #     output = await self.repo.get_by_id(session, academic_out.guid)
    #     assert output.name == academic_out.name
    #
    # @pytest.mark.anyio
    # async def test_get_by_name(self, session):
    #     academic_in = generate_academic_create_schema()
    #     academic_out = await self.repo.create(session, academic_in)
    #
    #     output = await self.repo.get_by_name(session, academic_out.name)
    #     assert output.guid == academic_out.guid
    #
    # @pytest.mark.anyio
    # async def test_update(self, session):
    #     academic_create = generate_academic_create_schema()
    #     academic_out = await self.repo.create(session, academic_create)
    #
    #     academic_update = generate_academic_create_schema()
    #     output = await self.repo.update(session, academic_out.guid, academic_update)
    #     assert academic_update == output.name
    #
    #     academic_create = generate_academic_create_schema()
    #     academic_out = generate_academic_output_schema()
    #     with pytest.raises(HTTPException):
    #         await self.repo.update(session, academic_out.guid, academic_create)
    #
    # @pytest.mark.anyio
    # async def test_delete(self, session):
    #     academic_create = generate_academic_create_schema()
    #     academic_out = await self.repo.create(session, academic_create)
    #
    #     await self.repo.delete(session, academic_out.guid)
    #
    #     assert len(await session.execute(select(AcademicModel))) == 0