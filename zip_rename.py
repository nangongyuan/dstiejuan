import os
import zipfile
from pathlib import Path


def extract_zip(dir):
    files = os.listdir(dir)
    count = 0
    dir_count = 0
    for name in files:
        if name.find('.zip') == -1:
            continue
        count = count + 1
        if count % 400 == 1:
            dir_count = dir_count + 1
        fullname = os.path.join(dir, name)
        file_zip = zipfile.ZipFile(fullname, 'r')
        zip_count = 0
        for f in file_zip.namelist():
            zip_count = zip_count + 1
            temp = os.path.join(dir, str(dir_count))
            extracted_path = Path(file_zip.extract(f, temp))
            if zip_count > 1:
                extracted_path.rename(temp+'/'+name.split('.zip')[0] + str(zip_count) + ".txt")
            else:
                extracted_path.rename(temp + '/' + name.split('.zip')[0] + ".txt")
        file_zip.close()
        os.remove(fullname)


extract_zip('D:/jianghuiyan/童话故事')
# try:
#     file_zip = zipfile.ZipFile(file_name, 'r')
#     for file in file_zip.namelist():
#         extracted_path = Path(file_zip.extract(file, 'h:/jianghuiyan/' + type + '/'))
#         extracted_path.rename('h:/jianghuiyan/' + type + '/' + name + "_" + author + ".txt")
#     file_zip.close()
#     os.remove(file_name)
# except BaseException as e:
#     print(e)
#     os.remove(file_name)