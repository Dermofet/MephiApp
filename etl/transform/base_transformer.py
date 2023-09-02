from redis import Redis

from logging_ import Logger


class BaseTransformer:
    db: Redis
    logger: Logger

    def __init__(
            self,
            redis_host: str,
            redis_port: int,
            db: int,
            single_connection_client: bool = True,
            is_logged: bool = True
    ):
        self.db = Redis(
            host=redis_host,
            port=redis_port,
            db=db,
            single_connection_client=single_connection_client
        )
        self.logger = Logger(is_logged)