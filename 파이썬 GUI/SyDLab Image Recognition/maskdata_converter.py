import os
import cv2

label_path = "maskdata/labels_previous"
image_path = "maskdata/images"
save_path = "maskdata/labels"

import xml.etree.ElementTree as elemTree

ccc = 1
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
        print(class_name)

        class_index = 0
        if class_name == 'with_mask':
            class_index = 0
        elif class_name == 'mask_weared_incorrect':
            class_index = 1
            # raw_image = cv2.imread(file_image_path)
            # draw = raw_image.copy()
            # cv2.imshow(file_image_path, draw)
            # cv2.waitKey(0)
        else:
            class_index = 2

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
        object_info.append([class_index, [boundingbox[0], boundingbox[1], boundingbox[2], boundingbox[3]]])
        # object_info.append([class_index, center_x, center_y, center_width, center_height])

    raw_image = cv2.imread(file_image_path)
    draw = raw_image.copy()
    print(file_image_path)

    for info in object_info:
        class_index = info[0]
        bbox = info[1]
        if class_index == 0:
            cv2.rectangle(draw, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255,0,0), thickness=3)
        elif class_index == 1:
            cv2.rectangle(draw, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 255), thickness=3)
        else:
            cv2.rectangle(draw, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), thickness=3)
        ccc+=1
    # cv2.imshow('mask', draw)
# print(ccc)
    file_save_path = "temp/" + file[:-4] + ".jpg"
    cv2.imwrite(file_save_path, draw)
    # cv2.waitKey(0)

    # if len(object_info) == 0:
    #     continue
    # else:
    #     f = open(save_path + "/" + file[:-4] + ".txt" ,'w')
    #     for i, info in enumerate(object_info):
    #         data = str(info[0]) + ' ' + str(info[1]) + ' ' + str(info[2]) + ' ' + str(info[3]) + ' ' + str(info[4])
    #         # print(data)
    #         if i != len(object_info) - 1:
    #             data += '\n'
    #
    #         f.write(data)
    #     f.close()
