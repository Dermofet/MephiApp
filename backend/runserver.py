import os
import sys

import uvicorn

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from config import config

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=config.BACKEND_RELOAD,
    )
