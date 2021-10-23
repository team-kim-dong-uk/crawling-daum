from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import configparser
import time
import json, os
import urllib.request


"""
{
    title: 제목, 
    upload_date: 업로드 날짜, 
    view_count: 조회수, 
    crawled_date: 크롤링 시각
}
을 얻기 위한 코드.
"""
driver = webdriver.Chrome('../driver/chromedriver')
START = 1
END = 250
IMG_PATH = os.getcwd() + "/stored/images/"
CAFE_LOGIN_PAGE = 'https://accounts.kakao.com/login?continue=https%3A%2F%2Flogins.daum.net%2Faccounts%2Fksso.do%3Frescue%3Dtrue%26url%3Dhttp%253A%252F%252Fm.cafe.daum.net%252F-ohmygirl%252F_newmember%253Fnull'
BASE_URL = 'https://m.cafe.daum.net/-ohmygirl/XtXW/'

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

# 현재 페이지에서 보이는 게시글들을 가져오는 함수
def get_articles(curr_driver):
    html = curr_driver.page_source
    page = BeautifulSoup(html, 'lxml')
    data = page.findAll('li', class_='thumbnail_on')
    return data


def parse_article_data(article_data):
    data = {}

    body = article_data.find('a', class_='#article_list')
    article_no = body.attrs['href'].split("/")[-1]

    if article_no in imgList:
        print("%s는 이미 확인 및 다운로드 했읍니다." % article_no)
        raise KeyboardInterrupt

    data['id'] = article_no
    data['url'] = BASE_URL + '/' + article_no
    data['title'] = body.find('span', class_='txt_detail').text.strip()  # 제목

    uploaded_date = body.find('span', class_='created_at').text.strip()
    if '.' not in uploaded_date:
        uploaded_date = str(datetime.now()).split(" ")[0]
    else:
        uploaded_date  = uploaded_date.replace('.', '-', 2)
    data['uploaded_date'] = uploaded_date  # 업로드 날짜

    data['crawled_date'] = str(datetime.now()).split(" ")[0]  # 크롤링 시점
    #data['recommended_count'] = article_data.find('span', class_='tbl_txt_recommend')  # 추천 수
    data['view_count'] = int(article_data.find('span', class_='view_count').text.strip())  # 조회수

    commentPart = article_data.find('a', class_='#comment_view')
    data['comment_count'] = int(commentPart.find('span', class_='num_cmt').text.strip()) # 댓글 수

    print(data)

    return data

def make_json(result, start, page, sortBy):
    result = sorted(result, key=lambda x: x[sortBy], reverse=True)
    json_data = json.dumps(result, ensure_ascii=False)

    filename = str(datetime.now()).split(".")[0] + '-page-' + str(start) + '-' + str(page - 1)
    file = open("./jsonOutput/" + filename + ".json", "w")
    file.write(json_data)
    file.close()

def main():
    page = START
    sortBy = 'view_count'
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
                result.append(parse_article_data(x))

            page += 1
            prev_page = move_page(prev_page)

    except KeyboardInterrupt:
        make_json(result, START,page, sortBy)
        exit()

    make_json(result, START,page, sortBy)

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