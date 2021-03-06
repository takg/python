import os
import face_recognition
import cv2
import pickle
import argparse

#  the logic of face recognition is derived from -->
#  https://www.pyimagesearch.com/2018/06/18/face-recognition-with-opencv-python-and-deep-learning/

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", help="input path containing the images for training program")
    parser.add_argument("--output_path", help="ouput path for saving the details of computed faces")
    parser.add_argument("--image_path_to_be_recognized", help="input path containing the images to be recognized")

    args = parser.parse_args()
    return args


def get_files_from_folder(folder):
    names = get_folders_from_folder(folder)
    files = {}
    for name in names:
        path = folder + '/' + name + '/'
        files[name] = [path + x for x in os.listdir(path)]

    return files


def get_folders_from_folder(folder):
    folders = os.listdir(folder)
    return [x for x in folders]


def encode_faces(image_files, output_file):
    knownEncodings = []
    knownNames = []
    for name in image_files.keys():
        for image_path in image_files[name]:
            image_path = image_path.replace('/', '\\\\')
            encodings, boxes, image = encode_face(image_path)
            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                knownEncodings.append(encoding)
                knownNames.append(name)

    data = {"name": knownNames, "encoding": knownEncodings}
    file = open(output_file, "wb")
    file.write(pickle.dumps(data))
    file.close()

    return knownNames, knownEncodings


def get_encodings(input_file):
    file = open(input_file, "rb")
    data = pickle.loads(file.read())
    file.close()

    return data["name"], data["encoding"]


def encode_face(image_path):
    # load the input image and convert it from BGR (OpenCV ordering)
    # to dlib ordering (RGB)
    print('Encoding image ', image_path, '...')
    image = cv2.imread(image_path, 1)
    # rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input image
    # model = cnn, hog
    # The CNN method is more accurate but slower. HOG is faster but less accurate.
    boxes = face_recognition.face_locations(image, model="cnn")
    # compute the facial embedding for the face
    encodings = face_recognition.face_encodings(image, boxes)

    return encodings, boxes, image


def recognize_face(image_path, known_names, known_encoding):
    encodings, boxes, image = encode_face(image_path.replace("/", "\\\\"))
    names = []
    print("Starting face recognition...")

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(known_encoding, encoding)
        name = "Unknown"
        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matched_ids = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matched_ids:
                name = known_names[i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number of
            # votes (note: in the event of an unlikely tie Python will
            # select first entry in the dictionary)
            name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)

    print('Names found', names)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)

    # show the output image
    cv2.imshow("Image", image)
    cv2.waitKey(0)
