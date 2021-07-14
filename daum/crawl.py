from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import configparser
import time
import json, os
import urllib.request

driver = webdriver.Chrome('../driver/chromedriver')
START = 1
END = 250
IMG_PATH = os.getcwd() + "/stored/images/"
CAFE_LOGIN_PAGE = 'https://accounts.kakao.com/login?continue=https%3A%2F%2Flogins.daum.net%2Faccounts%2Fksso.do%3Frescue%3Dtrue%26url%3Dhttp%253A%252F%252Fm.cafe.daum.net%252F-ohmygirl%252F_newmember%253Fnull'


def downloadImg(urls, article_no, hashtags):
    # 이미 다운받은 이미지인 경우
    if article_no in imgList:
        print('%s in img' % article_no)
        return

    # 현재 페이지에 이미지가 몇개 있나 프린트
    try:
        print("id - %s , url length - %d" %(article_no, len(urls)))
    except:
        pass

    index = 0
    for media_url in urls:
        # 이미지 이름 - 게시글 넘버 , 게시글 제목 단어, 사진 번호
        name = article_no + '-' + '_'.join(hashtags) + '-' + str(index)
        name = name.replace("/", "") # 파일 이름에 / 포함되면 디렉토리 에러 남.
        index += 1
        try:
            urllib.request.urlretrieve(media_url, IMG_PATH + name + ".jpg")
            print(name)
        except Exception as e:
            print(e)
            pass

        time.sleep(0.3)

def login():
    config = configparser.ConfigParser()
    config.read('./daum_config.ini')
    config = config['DAUM']
    # 카카오 로그인
    driver.get(CAFE_LOGIN_PAGE)
    time.sleep(1)

    driver.find_element_by_id('id_email_2').send_keys(config['id'])
    driver.find_element_by_id('id_password_3').send_keys(config['pw'])
    driver.find_element_by_class_name('submit').click()
    time.sleep(2)

def move_page(prevPage):
    # 게시글 내부에서 리스트로 이동
    print('move to List page')
    driver.get(prevPage)

    html = driver.page_source
    page = BeautifulSoup(html, 'lxml')
    paging = page.find('span', id='pagingNav')

    nowPage = 1
    for x in paging.children:
        if hasattr(x, 'attrs'):
            # 'sr_only' = 현재 페이지
            if 'sr_only' in x.attrs['class']:
                break
            else:
                nowPage += 1
    if nowPage == 5:
        # 마지막 페이지, 옆으로 버튼 클릭
        driver.find_element_by_xpath('//a[contains(@class, "btn_page") and contains(@class, "btn_next")]').click()
    else:
        driver.find_elements_by_class_name('link_page')[nowPage].click()
    time.sleep(2)

    # 게시글 순회 후 빠져나올 페이지, 이게 다음의 prev_page가 된다.
    return driver.current_url

# 현재 페이지에서 보이는 게시글들의 url을 가져오는 함수
def get_articles(curr_driver):
    html = curr_driver.page_source
    page = BeautifulSoup(html, 'lxml')
    data = page.findAll('a', class_='#article_list')

    return data


def get_article_data(article_driver, root_url, article_no):
    # 해당 게시글로 이동
    url = root_url + '/' + article_no
    article_driver.get(url)
    time.sleep(3)

    html = article_driver.page_source
    page = BeautifulSoup(html, 'html.parser')

    data = {}
    data['id'] = article_no

    subject = page.find('h3', class_='tit_subject').text.strip()
    data['subject'] = subject
    data['hashtags'] = subject.split(" ")
    data['url'] = url

    created_at = page.find('span', class_='num_subject').text.strip()
    if '.' not in created_at:
        created_at = str(datetime.now()).split(" ")[0]
    data['created_at'] = created_at

    contents = page.find('div', id='article')
    try:
        data['text'] = contents.find('p').text
    except:
        print('no text')
        data['text'] = ''

    # 이미지 url
    data['media_url'] = [x.attrs['src'] for x in contents.findAll('img')]

    downloadImg(data['media_url'], article_no, data['hashtags'])

    return data

def make_json(result, start, page):
    json_data = json.dumps(result, ensure_ascii=False)
    filename = str(datetime.now()).split(".")[0] + '-page-' + str(start) + '-' + str(page - 1)
    file = open("./jsonOutput/" + filename + ".json", "w")
    file.write(json_data)
    file.close()

def main():
    page = START

    login()
    # 시작 페이지
    photo_board = 'https://m.cafe.daum.net/-ohmygirl/XtXW/'
    prev_page = 'https://m.cafe.daum.net/-ohmygirl/XtXW?prev_page=2&firstbbsdepth=00368&lastbbsdepth=0035j&page=' + str(START)

    driver.get(photo_board)
    time.sleep(2)

    result = []
    try:
        while page <= END:
            articles = get_articles(driver)
            for x in articles:
                # move to article page and get data
                article_no = x.attrs['href'].split("/")[-1]
                result.append(get_article_data(driver, photo_board, article_no))

            page += 1
            prev_page = move_page(prev_page)

    except KeyboardInterrupt:
        make_json(result, START,page)
        exit()

    make_json(result, START,page)







downloadedImg = []
path = os.getcwd() + '/stored/images'
file_list = os.listdir(path)
file_list_py = [file for file in file_list]

imgList = []
for name in file_list_py:
    splitedName = name.split("-")[0]
    if splitedName not in imgList:
        imgList.append(splitedName)
main()