import gimpify


JSON_FACES_PATH = "app/gimp/faces.json"
JSON_BACKGROUNDS_PATH = "app/gimp/backgrounds.json"

IMG_FACES_PATH = "app/static/faces"
IMG_BACKGROUNDS_PATH = "app/static/backgrounds"

gimpify.create_face_json(IMG_FACES_PATH, JSON_FACES_PATH)
gimpify.create_background_json(IMG_BACKGROUNDS_PATH, JSON_BACKGROUNDS_PATH)
