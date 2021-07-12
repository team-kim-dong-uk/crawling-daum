import os
import json
path = 'stored/images'
file_list = os.listdir(path)
file_list_py = [file for file in file_list] ## 파일명 끝이 .csv인 경우

print(len(file_list_py))
file = open('stored/tweet.json', 'r')
originJSON = json.load(file)

print(len(originJSON))
