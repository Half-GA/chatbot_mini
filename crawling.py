import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import pandas as pd

##############################################################  ############
##################### variable related selenium ##########################
##########################################################################
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('lang=ko_KR')
chromedriver_path = "chromedriver"
driver = webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options=options)  # chromedriver 열기

duksung_list = []

def main():
    global driver, load_wb, review_num

    driver.implicitly_wait(4)  # 렌더링 될때까지 기다린다 4초
    driver.get('https://map.kakao.com/')  # 주소 가져오기

    # 검색할 목록
    place_infos = ['덕성여대 맛집']


    for i, place in enumerate(place_infos):
        # delay
        if i % 4 == 0 and i != 0:
            sleep(5)
        print("#####", i)
        search(place)

    driver.quit()

#추가한 부분(데이터 프레임 만들고 csv 파일로 저장)
    df = pd.DataFrame(duksung_list, columns=["맛집"])
    df.to_csv('file.csv',encoding='utf-8')


    print("finish")


def search(place):
    global driver
    search_area = driver.find_element(By.XPATH,'//*[@id="search.keyword.query"]')  # 검색 창
    search_area.send_keys(place)  # 검색어 입력
    driver.find_element(By.XPATH,'//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)  # Enter로 검색
    sleep(1)

    # 검색된 정보가 있는 경우에만 탐색
    # 1번 페이지 place list 읽기
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    place_lists = soup.select('.placelist > .PlaceItem') # 검색된 장소 목록

    # 검색된 첫 페이지 장소 목록 크롤링하기
    crawling(place, place_lists)
    search_area.clear()

    # 우선 더보기 클릭해서 2페이지
    try:
        driver.find_element(By.XPATH,'//*[@id="info.search.place.more"]').send_keys(Keys.ENTER)
        sleep(1)

        # 2~ 5페이지 읽기
        for i in range(2, 6):
            # 페이지 넘기기
            xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
            driver.find_element(By.XPATH,xPath).send_keys(Keys.ENTER)
            sleep(1)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            place_lists = soup.select('.placelist > .PlaceItem') # 장소 목록 list

            crawling(place, place_lists)

    except ElementNotInteractableException:
        print('not found')
    finally:
        search_area.clear()


def crawling(place, place_lists):
    """
    페이지 목록을 받아서 크롤링 하는 함수
    :param place:리뷰 정보 찾을 장소이름
    """

    while_flag = False
    for i, place in enumerate(place_lists):
        # 광고에 따라서 index 조정해야함
        #if i >= 3:
         #   i += 1

        place_name = place.select('.head_item > .tit_name > .link_name')[0].text  # place name
        place_address = place.select('.info_item > .addr > p')[0].text  # place address

        detail_page_xpath = '//*[@id="info.search.place.list"]/li[' + str(i + 1) + ']/div[5]/div[4]/a[1]'
        driver.find_element(By.XPATH,detail_page_xpath).send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])  # 상세정보 탭으로 변환
        sleep(1)

        print('####', place_name)
# 추가한 부분(이름 가져오기)
        duksung_list.append(place_name)


        # 첫 페이지

        # 2-5 페이지
        idx = 3
        try:
            page_num = len(driver.find_element(By.CLASS_NAME,'link_page')) # 페이지 수 찾기
            for i in range(page_num-1):
                # css selector를 이용해 페이지 버튼 누르기
                driver.find_element(By.CSS_SELECTOR,'#mArticle > div.cont_evaluation > div.evaluation_review > div > a:nth-child(' + str(idx) +')').send_keys(Keys.ENTER)
                sleep(1)

                idx += 1
            driver.find_element(By.LINK_TEXT,'다음').send_keys(Keys.ENTER) # 5페이지가 넘는 경우 다음 버튼 누르기
            sleep(1)

        except (NoSuchElementException, ElementNotInteractableException):
            print("no review in crawling")

        # 그 이후 페이지
        while True:
            idx = 4
            try:
                page_num = len(driver.find_element(By.CLASS_NAME,'link_page'))
                for i in range(page_num-1):
                    driver.find_element(By.CSS_SELECTOR,'#mArticle > div.cont_evaluation > div.evaluation_review > div > a:nth-child(' + str(idx) +')').send_keys(Keys.ENTER)
                    sleep(1)
                    idx += 1
                driver.find_element(By.LINK_TEXT,'다음').send_keys(Keys.ENTER) # 10페이지 이상으로 넘어가기 위한 다음 버튼 클릭
                sleep(1)
            except (NoSuchElementException, ElementNotInteractableException):
                print("no review in crawling")
                break

        driver.close()
        driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 전환


if __name__ == "__main__":
    main()