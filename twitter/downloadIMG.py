import json, os
import time
import urllib.request

file = open(os.getcwd() + '/stored/downloadedIMG.json', 'r')
downloadedImg = json.load(file)

with open(os.getcwd() + '/stored/tweet-7-3.json', 'r') as f:
    json_data = json.load(f)
    for tweet in json_data:
        if str(tweet['id']) in downloadedImg:
            print("already have image - id %s" % str(tweet['id']))
            continue
        if 'media_url' in tweet.keys():
            url = tweet['media_url']
            name = str(tweet['id']) + '-' + '_'.join(tweet['hashtags'])
            try:
                urllib.request.urlretrieve(url, os.getcwd() + "/stored/7-3/" + name + ".jpg")
            except Exception as e:
                print(e)
                pass

            time.sleep(0.3)


