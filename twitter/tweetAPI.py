import urllib.request
import tweepy
import json
from datetime import datetime
import time, os
import configparser
import zipfile, shutil
"""
트위터 긁어서 JSON파일 생성하기
JSON 구조는 최하단 참고

"""
consumer_key = "N0BynX4WSi5vV6T4KACu0oX02"
consumer_secret = "DeX70n0cWIYtkysdng5VFlpCLVQXdziV0BAXsey1V0XP1ogaDM"
access_token = '1410111878840291328-yCWpvkoh4A7HBQMUe6AuPgeD7Nz9ku'
access_token_secret = 'ze9Meuu1QEWic3WiN93MJJra6IU07Uyse68uOzREapdAS'

def makejson(api_result, length):
    retList = []

    for result in api_result:
        tw = {}
        hashtag = []
        tw['id'] = result.id
        tw['created_at'] = str(result.created_at)
        tw['text'] = result.text

        for tag in result.entities['hashtags']:
            hashtag.append(tag['text'])
        tw['hashtags'] = hashtag

        if 'media' in result.entities.keys():
            for media in result.entities['media']:
                tw['url'] = media['url']
                tw['media_url'] = media['media_url']
                tw['sizes'] = media['sizes']

        retList.append(tw)

        jsonRet = json.dumps(retList, ensure_ascii=False)
        filename = str(datetime.now()).split(".")[0] +'N'+ str(length)
        file = open(os.getcwd() + '/twitter/jsonOutput/' + filename + '.json', "w")
        file.write(jsonRet)
        file.close()

    return filename


"""
트위터 API로 데이터 검색
json파일로 저장
"""
def search(twitter_api, keyword):
    api_result = []

    #tweets = twitter_api.search(q=keyword, count=50000, lang="ko")
    tweets = tweepy.Cursor(twitter_api.search,
                               q=keyword,
                               count=50,
                               include_entities=True,
                               lang="ko").items()

    all = 0
    while True:
        try:
            tweet = tweets.next()
            api_result.append(tweet)

            all += 1
            if all % 1000 == 0:
                print("all - %d" % all)

        except tweepy.TweepError:
            print("TweepError ! wait 15m")
            time.sleep(60 * 15)
            continue
        except StopIteration:
            print("StopIter")
            break

    return makejson(api_result, all)

"""
json으로 저장한 데이터파일에서 기존에 가지고 있던 데이터 삭제
"""
def cutNewData(originJson):
    # 저장된 이미지 목록 불러오기
    path = os.getcwd() + '/twitter/stored/images'
    file_list = os.listdir(path)
    file_list_py = [file for file in file_list]

    imgList = []
    for name in file_list_py:
        imgList.append(name.split("-")[0])

    file = open(os.getcwd() + '/twitter/jsonOutput/' + originJson  + '.json', 'r')
    originJSON = json.load(file)

    for i in range(len(originJSON) - 1, -1, -1):
        if str(originJSON[i]['id']) in imgList:
            del originJSON[i]

    # tweetAPI에서 생성된 Json과 기존 이미지 목록 비교해서 아직 이미지가 없는 json 목록만 가져옴
    jsonRet = json.dumps(originJSON, ensure_ascii=False)
    file = open(os.getcwd() + "/twitter/stored/" + originJson + ".json", "w")
    file.write(jsonRet)
    file.close()

def downloadIMG(jsonName):
    with open(os.getcwd() + '/stored/' + jsonName + '.json', 'r') as f:
        json_data = json.load(f)
        for tweet in json_data:
            if 'media_url' in tweet.keys():
                url = tweet['media_url']
                name = str(tweet['id']) + '-' + '_'.join(tweet['hashtags'])
                try:
                    urllib.request.urlretrieve(url, os.getcwd() + "/stored/" + jsonName + "/" + name + ".jpg")
                except Exception as e:
                    print(e)
                    pass

                time.sleep(0.3)

    # 이미지 압축
    imgZip = zipfile.ZipFile(os.getcwd() + '/stored/' + jsonName + '.zip', 'w')
    imgZip.write(os.getcwd() + '/stored/' + jsonName, compress_type=zipfile.ZIP_DEFLATED)
    imgZip.close()

    # 이미지 이동
    #shutil.move(os.getcwd() + '/stored/' + jsonName, os.getcwd() + '/stored/images/')


def main():
    #계정 승인
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    twitter_api = tweepy.API(auth)

    keyword = "#더보이즈 OR #THEBOYZ"

    json_file_name = search(twitter_api, keyword)

    cutNewData(json_file_name)

    downloadIMG(json_file_name)

main()

"""
tw.entities[hashtags][i].text // 해시태그
tw.entities[media][i].url // 트윗 주소
tw.entities[media][i].media_url // 이미지 주소
tw.entities[media][i].sizes // 사진 사이즈

[tw.id](http://tw.id) // 
tw.text
tw.created_at
"""