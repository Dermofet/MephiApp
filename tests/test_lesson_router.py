import pytest
from httpx import AsyncClient

from backend.main import app


@pytest.mark.anyio
async def test_lesson_post()