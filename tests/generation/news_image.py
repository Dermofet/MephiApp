from backend.schemas.news_img import NewsImageOutputSchema
from tests.generation import fake


def generate_news_image_output_schema() -> NewsImageOutputSchema:
    return NewsImageOutputSchema(
        url=fake.url(),
        text=fake.text(),
    )