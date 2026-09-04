import os, random
import cv2

with_helmet_path = "helmetdata/with_helmet"
without_helmet_path = "helmetdata/without_helmet"

train_with_helmet_path = "helmetdata/train/with_helmet"
train_without_helmet_path = "helmetdata/train/without_helmet"

test_with_helmet_path = "helmetdata/test/with_helmet"
test_without_helmet_path = "helmetdata/test/without_helmet"

max_image = min(len(os.listdir(with_helmet_path)), len(os.listdir(without_helmet_path)))
print(max_image)

shuffle_list = []
for i in range(max_image):
    shuffle_list.append(i)

random.shuffle(shuffle_list)
print(shuffle_list)

train_test_ratio = 0.9

train_index = shuffle_list[:int(len(shuffle_list) * train_test_ratio)]
test_index = shuffle_list[:int(len(shuffle_list) * (1 - train_test_ratio))]

print(len(train_index), len(test_index))
# 5822,646

for i in train_index:
    with_helmet = cv2.imread(with_helmet_path + "/" + str(i) + ".png")
    cv2.imwrite(train_with_helmet_path + "/" + str(i) + ".png", with_helmet)

    without_helmet = cv2.imread(without_helmet_path + "/" + str(i) + ".png")
    cv2.imwrite(train_without_helmet_path + "/" + str(i) + ".png", without_helmet)

for i in test_index:
    with_helmet = cv2.imread(with_helmet_path + "/" + str(i) + ".png")
    cv2.imwrite(test_with_helmet_path + "/" + str(i) + ".png", with_helmet)

    without_helmet = cv2.imread(without_helmet_path + "/" + str(i) + ".png")
    cv2.imwrite(test_without_helmet_path + "/" + str(i) + ".png", without_helmet)
