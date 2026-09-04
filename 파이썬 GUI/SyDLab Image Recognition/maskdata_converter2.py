import os
import cv2

label_path = "maskdata/labels_previous"
image_path = "maskdata/images"
save_path = "maskdata/face/"

import xml.etree.ElementTree as elemTree


iii = 5785
for file in os.listdir(label_path):
    file_path = label_path + "/" + file
    file_image_path = image_path + "/" + file[:-4] + ".jpg"
    print(file_path)

    tree = elemTree.parse(file_path)
    filename = tree.find('filename').text
    # print(filename)

    width = int(tree.find('size').find('width').text)
    height = int(tree.find('size').find('height').text)
    # print(width, height)

    object_info = []
    objects = tree.findall('object')
    for object in objects:
        class_name = object.find('name').text

        bndbox = object.find('bndbox')
        boundingbox = []

        for element in bndbox:
            boundingbox.append(int(element.text))
        # print(boundingbox)

        center_x = (boundingbox[0] + boundingbox[2]) / 2 / width
        center_y = (boundingbox[1] + boundingbox[3]) / 2 / height
        center_width = (boundingbox[2] - boundingbox[0]) / width
        center_height = (boundingbox[3] - boundingbox[1]) / height

        # print(center_x, center_y, center_width, center_height)
        object_info.append([boundingbox[0], boundingbox[1], boundingbox[2], boundingbox[3]])

    raw_image = cv2.imread(file_image_path)
    draw = raw_image.copy()

    for info in object_info:
        bbox = info
        margin_height = int((int(bbox[3]) - int(bbox[1])) / 2)
        margin_width = int((int(bbox[2]) - int(bbox[0])) / 4)

        crop_image = draw[max(int(bbox[1]) - margin_height, 0):int(bbox[3]), max(int(bbox[0]) - margin_width, 0):min(int(bbox[2]) + margin_width, draw.shape[1])]
        if draw.shape[0] * draw.shape[1] * 0.05 < crop_image.shape[0] * crop_image.shape[1]:
            crop_image = cv2.resize(crop_image, dsize=(128,128))
            cv2.imwrite(save_path + str(iii) + '.png', crop_image)
            iii += 1