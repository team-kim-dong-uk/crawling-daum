from selenium import webdriver
from bs4 import BeautifulSoup
import configparser
import time
import json

driver = webdriver.Chrome('../driver/chromedriver')

def login():
    config = configparser.ConfigParser()
    config.read('./daum_config.ini')
    config = config['DAUM']
    # 카카오 로그인
    driver.get('https://accounts.kakao.com/login?continue=https%3A%2F%2Flogins.daum.net%2Faccounts%2Fksso.do%3Frescue%3Dtrue%26url%3Dhttp%253A%252F%252Fm.cafe.daum.net%252F-ohmygirl%252F_newmember%253Fnull')
    driver.find_element_by_id('id_email_2').send_keys(config['id'])
    driver.find_element_by_id('id_password_3').send_keys(config['pw'])
    driver.find_element_by_class_name('submit').click()

def get_articles(curr_driver):
    html = curr_driver.page_source
    page = BeautifulSoup(html, 'html.parser')
    return page.findAll('a', class_='#article_list')

def move_to_page(driver, url, page):
    print('move to page %d' % page)
    driver.get(url + '?page=' + str(page))
    time.sleep(2)

def get_article_data(driver, url, article):
    driver.get(url + '/' + article.attrs['href'].split("/")[-1])
    data = {}

    # TODO get data!
    # return data

def main():
    login()
    TARGET = 250
    # move to page
    photo_board = 'https://m.cafe.daum.net/-ohmygirl/XtXW'
    page = 1
    move_to_page(driver, photo_board, page)

    result = []
    while page <= TARGET:
        articles = get_articles(driver)

        for x in articles:
            # move to article page and get data
            result.append(get_article_data(driver, photo_board, x))

        page += 1
        move_to_page(driver, photo_board, page)

    json_data = json.dumps(result, ensure_ascii=False)
    # TODO how to set file name?
    filename = ''
    file = open("./jsonOutput/" + filename + ".json", "w")
    file.write(json_data)
    file.close()







main()