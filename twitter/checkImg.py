import os
import json
path = os.getcwd() + '/twitter/stored/images'
file_list = os.listdir(path)
file_list_py = [file for file in file_list]

ret = []
for name in file_list_py:
    ret.append(name.split("-")[0])

jsonRet = json.dumps(ret, ensure_ascii=False)
file = open(os.getcwd() + "/twitter/stored/downloadedIMG.json", "w")
file.write(jsonRet)
file.close()