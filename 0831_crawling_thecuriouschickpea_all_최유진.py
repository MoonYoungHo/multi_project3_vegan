from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json
import re


# 전체 페이지 수 가져오기
def get_page_num():
    url = 'https://www.thecuriouschickpea.com/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    max_num = soup.find('div', {'class': 'nav-links'}).contents[-3].text
    nums = list(range(1, int(max_num)+1))

    return nums


# 입력한 페이지의 전체 레시피 링크 가져오기
def get_links(i):
    link_list = list()
    url = 'https://www.thecuriouschickpea.com/page/' + str(i)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    titles = soup.find_all('h2', {'class': 'excerpt-title'})
    
    for title in titles:
        link_list.append(title.contents[0].get('href'))
    
    return link_list


# 입력한 링크의 제목, 댓글(후기) 가져오기
def get_contents(url):
    try:
        contents = dict()
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')

        # 제목
        title = soup.select('h1')[0].text
        contents['title'] = title

        # 재료
        ing_div = soup.find('div', {'class': 'mv-create-ingredients'})
        ing_list = list()

        if ing_div.h4:
            # h4: 소제목
            for h4 in ing_div.find_all('h4'):
                temp = dict()
                ing_temp = list()
                # li: 각 소제목 아래 재료들
                for li in h4.find_next_siblings()[0].contents:
                    if li != '\n':
                        ing_temp.append(li.text.strip())
                temp[h4.text] = ing_temp
                ing_list.append(temp)
        else:
            for li in ing_div.find_all('li'):
                ing_list.append(li.text.strip())

        contents['ingredients'] = ing_list

        # 조리시간
        contents['time'] = soup.find('div', {'class': 'mv-create-time mv-create-time-total'}).find('span').text.strip()

        # 분량
        contents['serving'] = soup.find('div', {'class': 'mv-create-time mv-create-time-yield'}).find('span').text.strip()

        # 레시피
        instr = soup.find('div', {'class': 'mv-create-instructions'}).find_all('li')
        instr_list = list()

        for i in range(len(instr)):
            instr_list.append(str(i+1) + ". " + instr[i].text)

        contents['recipe'] = instr_list

        # 영양정보
        nutri = soup.find('div', {'class': 'mv-create-nutrition-box'})
        nutri_dict = dict()

        nutri_dict['calories'] = nutri.find('span', {'class': 'mv-create-nutrition-calories'}).text.replace('Calories: ','') + 'kcal'
        nutri_dict['carbs'] = nutri.find('span', {'class': 'mv-create-nutrition-carbohydrates'}).text.replace('Carbohydrates: ','')
        nutri_dict['protein'] = nutri.find('span', {'class': 'mv-create-nutrition-protein'}).text.replace('Protein: ','')
        nutri_dict['total fat'] = nutri.find('span', {'class': 'mv-create-nutrition-total-fat'}).text.replace('Total Fat: ','')

        contents['nutrition'] = nutri_dict

        # 댓글
        page_num = soup.find('link', {'rel': 'shortlink'}).get('href')[-4:]
        comm_url = 'https://www.thecuriouschickpea.com/wp-json/wp/v2/comments?post=' + page_num +'&per_page=100'

        comments = requests.get(comm_url).json()    
        comm_list = list()
        for comment in comments:
            try:
                if (comment['author_name'] != 'thecuriouschickpea') and (comment['author_name'] != 'Eva Agha'):
                    comm_list.append(re.sub('(<([^>]+)>)', '', comment['content']['rendered']).strip())
            except:
                pass

        contents['comments'] = comm_list

        return contents
    
    except:
        pass


# 전체 페이지 레시피 가져오기
def get_all_page_comment(nums):
    total = dict()
    title_comments = list()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for num in nums:
            links = get_links(num)
            for link in links:
                content = executor.submit(get_contents, link)
                title_comments.append(content.result())
    
    total['thecuriouschickpea'] = title_comments
    return total


# 메인에서 실행
if __name__ == '__main__':
    nums = get_page_num()
    total = get_all_page_comment(nums)

    with open('/home/ubuntu/crawling/raw_data/thecuriouschickpea_review_all.json', 'w', encoding='utf-8-sig') as file:
        json.dump(total, file, indent="\t")
        
    print("done")