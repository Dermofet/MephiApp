from etl.loaders.base_loader import BaseLoader
from etl.schemas.lesson import LessonTranslateLoading
from etl.schemas.teacher import TeacherTranslateLoading


class TranslateLoader(BaseLoader):
    def __init__(
            self,
            redis: str,
            postgres_dsn: str,
            single_connection_client: bool = True,
            is_logged: bool = True,
            debug: bool = False
    ):
        super().__init__(
            redis=redis,
            postgres_dsn=postgres_dsn,
            single_connection_client=single_connection_client,
            is_logged=is_logged,
            debug=debug
        )
    
    async def load(self):
        self.logger.info("Loading translate...")
        try:
            await self.__load_lessons()
            await self.__load_teachers()
            await self.facade_db.commit()
            self.logger.info("Translate were loaded successfully")
        except Exception as e:
            self.logger.error("Can't load translate")
            await self.facade_db.rollback()
            raise e

    async def __load_lessons(self):
        trans = []
        i = 0
        for key in self.redis_db.keys("lesson_translate:*"):
            trans.append(LessonTranslateLoading.model_validate_redis(self.redis_db.hget(name=key, key="trans")))
            i += 1

            if i % 100 == 0:
                await self.facade_db.bulk_insert_trans_lesson(trans)
                self.logger.debug(f"Loaded {i} lesson_translate")
                trans = []

        if len(trans) > 0: 
            await self.facade_db.bulk_insert_trans_lesson(trans)
            self.logger.debug(f"Loaded {i} lesson_translate")

        for key in self.redis_db.scan_iter("lesson_translate:*"):
            self.redis_db.delete(key)

        self.logger.debug("Lesson_translate are loaded")

    async def __load_teachers(self):
        trans = []
        i = 0
        for key in self.redis_db.keys("teacher_translate:*"):
            trans.append(TeacherTranslateLoading.model_validate_redis(self.redis_db.hget(name=key, key="trans")))
            i += 1

            if i % 100 == 0:
                await self.facade_db.bulk_insert_trans_teacher(trans)
                self.logger.debug(f"Loaded {i} teacher_translate")
                trans = []

        if len(trans) > 0:
            await self.facade_db.bulk_insert_trans_teacher(trans)
            self.logger.debug(f"Loaded {i} teacher_translate")

        for key in self.redis_db.scan_iter("teacher_translate:*"):
            self.redis_db.delete(key)

        self.logger.debug("Teacher_translate are loaded")