from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import random


def today_recipe():
    url = 'https://www.youtube.com/results?search_query=vegan+recipe&sp=CAMSBAgCEAE%253D'
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service('/home/ubuntu/Jupyter/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    sleep(3)
    
    v_list = list()

    for i in range(10):
        v_path = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[' + str(i+1) + ']/div[1]/ytd-thumbnail/a'
        v_list.append(driver.find_element(By.XPATH, v_path).get_attribute("href"))

    ran_vid = random.choice(v_list)

    if "shorts" not in ran_vid:
        today_vid = ran_vid.replace('/watch?v=','/embed/')
    else:
        today_vid = ran_vid.replace('shorts','embed')
        
    return today_vid


if __name__ == '__main__':
    videos = today_recipe()
    
    print(videos)