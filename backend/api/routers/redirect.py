from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from config import config
from utils import redirect

router = APIRouter()


@router.get(
    "/redirect-to-store",
    include_in_schema=False,
    description="Перенаправить в маркетплейс в зависимости от устройства",
    summary="Перенаправить в маркетплейс",
)
async def redirect_to_marketplace(request: Request):
    user_os = redirect.get_user_os(request)
    if user_os == "iOS":
        return RedirectResponse(url=config.IOS_MARKETPLACE_URL.unicode_string())
    else:
        return RedirectResponse(url=config.ANDROID_MARKETPLACE_URL.unicode_string())

