import os
import random
import logging

from starlette.requests import Request
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

TITLE = "Manele's beerthday"
DESCRIPTION = "This is a shitty web to show shitty photos"


# Create FastApi app (has to be named like this)
app = FastAPI(title=TITLE, description=DESCRIPTION, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

list_img = [img for img in os.listdir("static") if "fpqll" not in img]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


@app.exception_handler(404)
async def not_found(request, exc):
    return templates.TemplateResponse("fpqll.html", {"request": request}, status_code=404)


async def get_random_image() -> str:
    random.shuffle(list_img)

    return f"/static/{list_img[0]}"


@app.get("/", include_in_schema=False)
async def main(request: Request):
    url = await get_random_image()
    logger.info(f"URL showing: {url}")
    return templates.TemplateResponse("main.html", {"request": request, "url": url})


@app.get("/i-am-feeling-lucky", include_in_schema=False)
async def main(request: Request):
    url = await get_random_image()
    logger.info(f"URL showing: {url}")
    return templates.TemplateResponse("main.html", {"request": request, "url": url})
