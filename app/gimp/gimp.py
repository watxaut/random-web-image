import json
import logging
import os
import random

from PIL import Image


logger = logging.getLogger(__name__)

try:
    import face_recognition
except ModuleNotFoundError:
    logger.warning("Face recognition not found")


def create_face_params(json_save_path, imgs_face_path):
    """
    Loads all faces in 'background_path', calculates their bounding box and puts the bb and the path into a list
    :return: json file path of the params
    """

    l_img = []
    l_name_img = os.listdir(imgs_face_path)
    for s_name in l_name_img:

        # get rid of tests and .md files
        if not s_name.startswith("_") and not s_name.endswith(".md"):
            im_face_path = "{}/{}".format(imgs_face_path, s_name)
            im_face = face_recognition.load_image_file(im_face_path)
            l_faces = face_recognition.face_locations(im_face)

            # if a face is detected (should only be one)
            if l_faces:
                t_face = l_faces[0]  # only one face
                l_img.append({"rel_path": im_face_path, "t_face": t_face})
            else:
                logger.info(
                    "Image '{}' has no face :( Try to make the frame a little bigger without resizing the face".format(
                        s_name)
                )

    # save list of params
    json_img = json.dumps(l_img)

    f = open(json_save_path, "w")
    f.write(json_img)
    f.close()
    return json_save_path


def create_background_params(json_save_path, background_path):
    """
    Loads all backgrounds in 'resources/in/backgrounds', gets all faces, calculates their bounding box and puts the bbs
    and the path into a list.
    :return: file path of the json file
    """

    l_img = []
    l_name_img = os.listdir(background_path)
    for s_name in l_name_img:

        # get rid of tests and .md files
        if not s_name.startswith("_") and not s_name.endswith(".md"):
            im_background_path = "{}/{}".format(background_path, s_name)
            im_background = face_recognition.load_image_file(im_background_path)
            l_faces = face_recognition.face_locations(im_background)

            # if a face is detected, more than one
            if l_faces:
                l_img.append({"rel_path": im_background_path, "l_faces": l_faces})
            else:
                logger.info("No face found in image: '{}' :(".format(s_name))

    # save list of params
    json_img = json.dumps(l_img)

    f = open(json_save_path, "w")
    f.write(json_img)
    f.close()
    return json_save_path


def check_return_png_path(im_path, root_folder):
    """
    Checks the image is in png and if not, converts it to png, saves it in the same folder and returns the new im path.
    If it is, returns the same path
    :param im_path:
    :param root_folder:
    :return:
    """
    if not im_path.endswith(".png"):
        im_name = im_path.replace("\\", "/").split("/")[-1].split(".")[0]

        im_jpg = Image.open(im_path)
        im_path = "{}/{}.png".format(root_folder, im_name)
        try:
            im_jpg.save(im_path)
            return im_path
        except IOError:
            raise
    else:
        return im_path


def manelitify(background_img, l_img_faces, only_face, root_folder):
    """
    The function that makes the magic. Gets an image background path, the list of faces {bb, path} and crops, resizes
    and pastes the faces into the image.
    :param background_img: background image, can either be a path or a dict of list_of_faces, path_to_background_img ->
    {rel_path, l_faces}
    :param l_img_faces: list of dictionaries {bb, path} of each face
    :param only_face: param that crops (or not) the face
    :param root_folder:
    :return: the PIL background image
    """

    if type(background_img) is dict:
        im_path = background_img["rel_path"]
        im_path_new = check_return_png_path(im_path, root_folder)

        l_faces = background_img["l_faces"]
    else:
        im_path = background_img

        im_path_new = check_return_png_path(im_path, root_folder)  # check background image png format
        im_base = face_recognition.load_image_file(im_path_new)     # load face_recognition PIL background image
        l_faces = face_recognition.face_locations(im_base)          # get tuple with face locations
        logger.info(f"Found '{len(l_faces)}' faces")

    # reload images again because yes (I was having problems with that method so I opened it again using PIL)
    im_base = Image.open(im_path_new)

    f_factor = 1.1  # multiplies width and creates the width of the new face

    # face with this method gets pasted to high. The greater it is, the lower the face will be pasted
    f_moderate_height = 0.15

    for l_face in l_faces:

        # get image props
        upper, right, lower, left = l_face
        width = right - left
        height = lower - upper

        # get a random face from the list of faces
        i = random.randint(0, len(l_img_faces) - 1)
        d_face = l_img_faces[i]

        # load face
        im_face = Image.open(d_face["rel_path"])

        # get face props
        f_upper, f_right, f_lower, f_left = d_face["t_face"]
        face_width = f_right - f_left
        face_height = f_lower - f_upper

        if not only_face:  # if the full face is needed (with hair)

            # calculate the aspect ratio of the face to keep it the same when resizing
            k_aspect_ratio_face = im_face.size[0] / im_face.size[1]

            # calculate how big (or small) is the face compared with the one in the image
            k_factor_width = face_width / width
            face_new_width = int(im_face.size[0] / k_factor_width * f_factor)
            face_new_height = int(face_new_width / k_aspect_ratio_face)

            # calculate the point to paste the image
            p1 = [int(left - (face_new_width / face_width * f_left)),
                  int((upper - (face_new_height / face_height) * f_upper))]
            p1[1] = p1[1] + int(face_new_height * f_moderate_height)
            p1 = tuple(p1)

            # resize the face and paste it into the background image
            im_face_aux = im_face.resize((face_new_width, face_new_height), Image.ANTIALIAS).convert("RGBA")
            im_base.paste(im_face_aux, p1, im_face_aux)

        else:  # if only the face needs to get pasted it's easier

            # just crop the new face, resize it to match the background face and paste it
            im_face = im_face.crop((f_left, f_upper, f_right, f_lower))

            im_face_aux = im_face.resize((width, height), Image.ANTIALIAS).convert("RGBA")
            im_base.paste(im_face_aux, (left, upper), im_face_aux)

    return im_base
