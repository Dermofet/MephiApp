from typing import Optional
import loguru


class Logger:
    __is_logged: bool
    __logger: loguru.logger
    filepath: Optional[str]

    def __init__(self, is_logged: bool = True):
        self.__is_logged = is_logged
        self.__logger = loguru.logger
        # self.__logger.add(
        #     "logging_/logs/log.log",
        #     format="{time} {level} {message}",
        # )

    def info(self, msg: str):
        if self.__is_logged:
            self.__logger.info(msg)

    def debug(self, msg: str):
        if self.__is_logged:
            self.__logger.debug(msg)

    def error(self, msg: str):
        if self.__is_logged:
            self.__logger.error(msg)

    def warning(self, msg: str):
        if self.__is_logged:
            self.__logger.warning(msg)