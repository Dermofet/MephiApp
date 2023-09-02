from news_image import generate_news_image_output_schema

from backend.schemas.news import NewsOutputSchema
from tests.generation import fake


def generate_news_output_schema() -> NewsOutputSchema:
    return NewsOutputSchema(
        title=fake.lexify(text="?"*10),
        preview_url=fake.url(),
        text=fake.text(),
        date=fake.date(),
        imgs=[generate_news_image_output_schema()],
    )