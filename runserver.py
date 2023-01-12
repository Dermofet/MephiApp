import uvicorn

from backend.Config.config import get_config

if __name__ == "__main__":
    config = get_config()
    uvicorn.run("backend.main:app",
                host=config.BACKEND_HOST,
                port=config.BACKEND_PORT,
                reload=config.BACKEND_RELOAD)
