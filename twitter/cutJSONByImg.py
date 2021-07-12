import os
import json

"""
2. make new json data (except previous data)
"""

# 저장된 이미지 목록 불러오기
path = os.getcwd() + '/twitter/stored/images'
file_list = os.listdir(path)
file_list_py = [file for file in file_list]

imgList = []
for name in file_list_py:
    imgList.append(name.split("-")[0])

# 파일 이름 바꿔주세요
file = open(os.getcwd() + '/twitter/jsonOutput/2021-07-12 07:04:12N111709.json', 'r')
originJSON = json.load(file)

for i in range(len(originJSON)-1, -1, -1):
    if str(originJSON[i]['id']) in imgList:
        del originJSON[i]

# tweetAPI에서 생성된 Json과 기존 이미지 목록 비교해서 아직 이미지가 없는 json 목록만 가져옴
jsonRet = json.dumps(originJSON, ensure_ascii=False)
file = open(os.getcwd() + "/twitter/stored/tweet-7-3.json", "w")
file.write(jsonRet)
file.close()