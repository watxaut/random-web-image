import os
import random
import logging
import time
import json
import traceback

from starlette.requests import Request
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

try:
    import gimp.gimp as gimp
    import gimp.config as config
except ModuleNotFoundError:
    import app.gimp.gimp as gimp
    import app.gimp.config as config


def load_json_params(json_path):
    f = open(json_path, "r")
    l_params = json.load(f)
    f.close()
    return l_params


l_json_faces = load_json_params(config.JSON_FACES_PATH)
l_json_backgrounds = load_json_params(config.JSON_BACKGROUNDS_PATH)

TITLE = "Manele's beerthday"
DESCRIPTION = "This is a shitty web to show shitty photos"


# Create FastApi app (has to be named like this)
app = FastAPI(title=TITLE, description=DESCRIPTION, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


@app.exception_handler(404)
async def not_found(request, exc):
    return templates.TemplateResponse("fpqll.html", {"request": request}, status_code=404)


async def get_random_image() -> (str, int, int):
    list_img = [img for img in os.listdir(r"static/manel")]
    random.shuffle(list_img)
    img_name = list_img[0]
    img_number = int(img_name.split(".")[0]) + 1
    return f"/static/manel/{img_name}", img_number, len(list_img)


@app.get("/", include_in_schema=False)
async def main(request: Request):
    url, img_number, total_img = await get_random_image()
    str_img_number = f"{img_number}/{total_img}"
    logger.info(f"URL showing: {url}")
    return templates.TemplateResponse("main.html", {"request": request, "url": url, "str_img_number": str_img_number})


def create_montage(background_img, json_faces, only_face=False):

    url = f'/app/static/tmp/i_{str(time.time()).replace(".", "_")}.jpeg'

    try:
        im_out = gimp.manelitify(background_img, json_faces, only_face, "static/backgrounds")
    except:  # something wrong with the image jej
        logger.error(traceback.format_exc())
        logger.error('Something wrong with image: "{}"'.format(background_img["rel_path"]))
        return None

    im_out.save(url)

    return url


@app.get("/i-am-feeling-lucky", include_in_schema=False)
async def feeling_lucky(request: Request):
    i = random.randint(0, len(l_json_backgrounds) - 1)

    url = create_montage(l_json_backgrounds[i], l_json_faces)
    if url is not None:
        url = url.replace("/app", "")
        str_img_number = "? out of ???"
    else:
        url = "static/fpqll.png"
        str_img_number = "woopsies, it crashed. Enjoy this Fran Perea"

    logger.info(f"URL showing: {url}")

    return templates.TemplateResponse("main.html", {"request": request, "url": url, "str_img_number": str_img_number})
