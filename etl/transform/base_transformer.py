from redis import Redis

from logging_ import Logger


class BaseTransformer:
    db: Redis
    logger: Logger

    def __init__(
            self,
            redis: str,
            single_connection_client: bool = True,
            is_logged: bool = True
    ):
        self.db = Redis.from_url(redis, single_connection_client=single_connection_client)
        self.logger = Logger(is_logged)