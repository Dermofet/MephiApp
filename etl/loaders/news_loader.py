from etl.loaders.base_loader import BaseLoader
from etl.schemas.news import NewsLoading


class NewsLoader(BaseLoader):
    def __init__(
        self,
        redis: str,
        postgres_dsn: str,
        single_connection_client: bool = True,
        is_logged: bool = True,
        debug: bool = False,
    ):
        super().__init__(redis, postgres_dsn, single_connection_client, is_logged, debug)

    async def load(self):
        self.logger.info("Loading news...")

        try:
            await self.__load_news()
            await self.facade_db.commit()
        except Exception as e:
            self.logger.error(f"Can't loading data: {e}")
            await self.facade_db.rollback()

        self.logger.info("News loaded successfully")

    async def __load_news(self):
        news = []
        i = 0
        for key in self.redis_db.keys("news:*"):
            news.append(NewsLoading.model_validate_redis(self.redis_db.hget(name=key, key="news")))
            i += 1

            if i % 100 == 0:
                await self.facade_db.bulk_insert_news(news)
                self.logger.debug(f"Loaded {i} news")
                news = []

        if len(news) > 0:
            await self.facade_db.bulk_insert_news(news)
            self.logger.debug(f"Loaded {i} news")

        for key in self.redis_db.scan_iter("news:*"):
            self.redis_db.delete(key)

        self.logger.debug("News are loaded")
