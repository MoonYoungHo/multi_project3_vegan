from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep


def today_recipe():
    url = 'https://www.youtube.com/results?search_query=vegan+recipe&sp=CAMSBAgCEAE%253D'
    driver = webdriver.Chrome(service=Service('chromedriver.exe'))
    driver.get(url)
    sleep(5)
    
    v_list = list()

    for i in range(10):
        v_path = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[' + str(i+1) + ']/div[1]/ytd-thumbnail/a'
        v_list.append(driver.find_element(By.XPATH, v_path).get_attribute("href"))

    return v_list


if __name__ == '__main__':
    videos = today_recipe()
    
    print(videos)