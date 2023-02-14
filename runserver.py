import uvicorn

from backend.config import config

if __name__ == "__main__":
    uvicorn.run("backend.main:app",
                host=config.BACKEND_HOST,
                port=config.BACKEND_PORT,
                reload=config.BACKEND_RELOAD)
