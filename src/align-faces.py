import glob
import pickle
import face_recognition as fr
from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2
import os


# calculate center of a shape (average of all points)
def centroid(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return int(round(sum_x / length)), int(round(sum_y / length))


# calculate polar angle of 2 points
def angle(x1, y1, x2, y2):
    return np.degrees(np.arctan((y2 - y1) / (x2 - x1)))


# calculate distance between two points
def distance(x1, y1, x2, y2):
    return np.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))


# rotates an image around some point (center_x, center_y)
def rotate_image(img, rot_angle, center_x, center_y):
    center = (center_x, center_y)
    rot_mat = cv2.getRotationMatrix2D(center, rot_angle, 1.0)
    result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


# translate an image by some horizontal and vertical offset
def translate_image(img, hor_shift, vert_shift):
    h, w = img.shape[:2]
    tran_mat = np.float32([[1, 0, hor_shift], [0, 1, vert_shift]])
    result = cv2.warpAffine(img, tran_mat, (w, h))
    return result


# scale an image by some magnitude from the center, and crop to 1920x1080
def scale_image(img, scale, desired_width, desired_height):
    h, w = img.shape[:2]
    result = cv2.resize(img, (int(scale * w), int(scale * h)), interpolation=cv2.INTER_CUBIC)
    center = (int(result.shape[0] / 2), int(result.shape[1] / 2))
    background = np.zeros((desired_height, desired_width, 3), np.uint8)
    h, w = result.shape[:2]
    if w >= desired_width:
        crop_x = int(desired_width / 2)
    else:
        crop_x = int(w / 2)
    if h >= desired_height:
        crop_y = int(desired_height / 2)
    else:
        crop_y = int(h / 2)

    result = result[(center[0] - crop_y):(center[0] + crop_y), (center[1] - crop_x):(center[1] + crop_x)]
    h, w = result.shape[:2]
    background[int(desired_height / 2 - h / 2):int(desired_height / 2 + h / 2), int(desired_width / 2 - w / 2):int(desired_width / 2 + w / 2)] = result[0:h, 0:w]

    return background


def classify_unknown(image, trained_enc):
    face_locations = fr.face_locations(image)
    unknown_face_encodings = fr.face_encodings(image, face_locations)

    face_names = []
    for face in unknown_face_encodings:
        matches = fr.compare_faces(trained_enc, face, tolerance=0.45)
        name = "unknown"

        face_distances = fr.face_distance(trained_enc, face)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            # name = trained_name[best_match_index]
            name = 'me'
        face_names.append(name)

    if 'me' in face_names:
        face_temp = face_locations[face_names.index('me')]
    elif len(face_locations) > 0:
        face_temp = face_locations[0]
    else:
        return None
    face = dlib.rectangle(face_temp[3], face_temp[0], face_temp[1], face_temp[2])
    return face


def main():

    # construct the argument parser and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--shape-predictor", help="path to facial landmark predictor", default="predictor.dat")
    parser.add_argument("-f", "--faces", help="path to trained faces", default="trained_faces.dat")
    parser.add_argument("-s", "--source", action="store", required=True, dest="source",
                        help="source directory of images to align", default="")
    parser.add_argument("-d", "--destination", action="store", dest="destination",
                        help="destination directory for indexed align", default="")
    parser.add_argument("-t", "--type", action="store", dest="type",
                        help="file extension for images to align", choices=['jpg', 'png'], default="jpg")
    parser.add_argument("-W", "--width", action="store", dest="width",
                        help="width of output image", default=1920, type=int)
    parser.add_argument("-H", "--height", action="store", dest="height",
                        help="height of output image", default=1080, type=int)
    parser.add_argument("-S", "--scale", action="store", dest="scale",
                        help="pixel distance between eyes", default=200, type=int)
    parser.add_argument("-G", "--gui", action="store_true", help=argparse.SUPPRESS)
    args = vars(parser.parse_args())

    # initialize dlib's face detector (HOG-based) and then create the facial landmark predictor
    # detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])

    # import trained faces into readable dictionary
    trained = pickle.load(open(args["faces"], "rb"))
    trained_enc = list(trained.values())

    # input validation for source directory
    if os.path.isdir(args["source"]):
        os.chdir(args["source"])
    else:
        print("Source directory could not be found.")
        exit()

    # if source and destination directories are the same, make sure user wants to overwrite original files
    if not args["gui"] and args["destination"] == args["source"]:
        choice = input("Destination directory same as source directory. Modify files in directory [ORIGINALS WILL BE "
                       "LOST]? (y/n) ")
        if choice.lower() != 'y':
            exit()

    # if there is no specified destination directory, make sure user wants to overwrite original files
    if not args["gui"] and not args["destination"]:
        choice = input("Destination directory not specified. Modify files in directory [ORIGINALS WILL BE LOST]? (y/n) ")
        if choice.lower() == 'y':
            args["destination"] = args["source"]

    # input validation for destination directory
    if not os.path.isdir(args["destination"]):
        print("Destination directory could not be found.")
        exit()

    # retrieve the files of the correct type from the directory and store into an array
    files = glob.glob("*." + args["type"])
    total = len(files)
    cnt = 0

    # iterate through all of the different files in the directory
    for file in files:

        # load the input image, resize it, and convert it to grayscale
        image = cv2.imread(args["source"] + "\\" + file)
        image = imutils.resize(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale image
        # faces = detector(gray, 1)

        face = classify_unknown(image, trained_enc)
        if face is not None:
            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)  # 68 points held in a np array
            clone = image.copy()
            landmarks = face_utils.FACIAL_LANDMARKS_IDXS
            height, width = image.shape[:2]

            # find centroids which will be used for aligning
            right_eye_centroid = centroid(shape[landmarks["right_eye"][0]:landmarks["right_eye"][1]])
            left_eye_centroid = centroid(shape[landmarks["left_eye"][0]:landmarks["left_eye"][1]])
            nose_centroid = centroid(shape[landmarks["nose"][0]:landmarks["nose"][1]])

            # calculate angle (negated because of flipped coordinate grid) and distance between the two eyes
            eye_angle = -1 * angle(right_eye_centroid[0], right_eye_centroid[1], left_eye_centroid[0], left_eye_centroid[1])
            eye_distance = distance(right_eye_centroid[0], right_eye_centroid[1], left_eye_centroid[0],
                                    left_eye_centroid[1])

            # re-center image based on the nose centroid
            clone = translate_image(clone, width / 2 - nose_centroid[0], height / 2 - nose_centroid[1])

            # rotate the to counteract the calculate angle error after re-centering
            clone = rotate_image(clone, -1 * eye_angle, width / 2, height / 2)

            # scale the image so the eye distance is of the desired value
            clone = scale_image(clone, args["scale"] / eye_distance, args["width"], args["height"])

            # output the file
            cv2.imwrite(args["destination"]+"\\"+file, clone)

        if args["gui"]:
            cnt += 1
            print((cnt/total) * 100)
        else:
            print(args["destination"]+"\\"+file+" written")


if __name__ == '__main__':
    main()
