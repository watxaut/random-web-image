import logging
import random
import typing

from PIL import Image

logger = logging.getLogger(__name__)


def manelitify(background_img: dict, l_img_faces: typing.List[dict], only_face: bool):
    """
    The function that makes the magic. Gets an image background path, the list of faces {bb, path} and crops, resizes
    and pastes the faces into the image.
    :param background_img: background image as dict of list_of_faces, path_to_background_img -> {rel_path, l_faces}
    :param l_img_faces: list of dictionaries {bb, path} of each face
    :param only_face: param that crops (or not) the face
    :return: the PIL background image
    """

    im_path: str = background_img["rel_path"]
    l_faces = background_img["l_faces"]

    # load base image
    im_base = Image.open(im_path)

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
