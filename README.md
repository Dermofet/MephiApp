В данном репозитории находится вся серверная часть, необходимая работе приложения "Mephi APP" (https://play.google.com/store/apps/details?id=acm.mephiapp&hl=ru&gl=US).

Она состоит из API, реализованное с помощью библиотеки FastAPI, и БД, для создания которого использовался СУБД PostgreQL и библиотеки SQLAlchemy. Серверная часть реализована в контейнере с помощью Docker Compose. 

Приложение создавалось как аналог приложения "НИЯУ МИФИ. Личный кабинет" (https://play.google.com/store/apps/details?id=com.mephi.corporatemephi&hl=ru&gl=US).

-------------

В текущий момент backend переписывается под асинхронную работу SQLAlchemy (https://github.com/Dermofet/MephiApp/tree/async_backend_1)
