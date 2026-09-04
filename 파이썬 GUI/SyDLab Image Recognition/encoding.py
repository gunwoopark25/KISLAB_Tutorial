folder_name = "Unity/labels/"
new_folder_name = "new_labels"

import os

for ff_name in os.listdir(folder_name):
  file_name = folder_name + "/" + ff_name
  with open(file_name, 'rb') as source_file:
    target_file_name = new_folder_name + "/" + ff_name
    with open(target_file_name, 'w+b') as dest_file:
      contents = source_file.read()
      dest_file.write(contents.decode('utf-16').encode('utf-8'))