from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json


# 전체 페이지 수 가져오기
def get_page_num():
    url = 'https://www.pickuplimes.com/recipe/'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    page_nums = soup.find('div', {'class': 'pagination'})
    max_num = page_nums.find_all('span', {'class': 'page-text'})[1].text.split('of ')
    nums = list(range(1, int(max_num[1]) + 1))

    return nums

# 입력한 페이지의 전체 레시피 링크 가져오기
def get_links(i):
    link_list = list()
    url = 'https://www.pickuplimes.com/recipe/?page=' + str(i)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    lis = soup.find_all('li', {'class': 'flex-item slide-up-ani'})

    for li in lis:
        link_list.append('https://www.pickuplimes.com' + li.contents[1].get('href'))

    return link_list

# 입력한 링크의 출처(site), 레시피명(title), 재료 리스트(ingredients), 조리시간(time), 분량(serving), 레시피(recipe),
# 영양 성분(nutrition), 댓글 리스트(comments), 이미지(image) 가져오기
def get_contents(url):
    contents = dict()
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # 출처(site)
    # 함수에 입력받는 url 사용

    # 레시피명(title)
    title = soup.find('h1').text

    # 재료 리스트(ingredients),
    ingredients_raw = soup.find('section', {'style': 'position: sticky; top: 10rem;'})
    ingredients = ingredients_raw.find_all('div', {'class': 'ingredient-container'})
    ing_list = list()
    for ingredient in ingredients:
        ing_list.append(ingredient.text.replace('\n', ''))

    # 조리시간(time)
    time = soup.find('span', {'style': 'font-weight: 400;'}).text

    # 분량(serving)
    servings_raw = soup.find('div', {'class': 'col servings-scaling'}).find('div', {'class': 'input-group'})
    servings = servings_raw.find('input').get('value')
    serving = servings + ' serving'

    # 레시피(recipe)
    recipe_raw = soup.find('div', {'class': 'col-md-5 pt-4 directionlist'}).find('ol').find_all('li')
    recipe_list = list()
    for i in range(len(recipe_raw)):
        recipe_list.append(str(i + 1) + ". " + recipe_raw[i].text.replace('\n', ''))

    # 영양 성분(nutrition)
    nutrition = soup.find('div', {'id': 'nut-info'})

    calories = nutrition.find('p').text.split(' ')[1] + ' kcal'
    carbs = nutrition.find('div', {'class': 'row'}).find_all('td')[13].text
    protein = nutrition.find('div', {'class': 'row'}).find_all('td')[21].text
    total_fat = nutrition.find('div', {'class': 'row'}).find_all('td')[1].text

    # 댓글 리스트(comments) / 보류
    # comments = soup.select('div[class=comment] > p > p')
    # com_list = list()
    # for comment in comments:
    #     com_list.append(comment.text)

    # 이미지(image)
    image = soup.find('div', {'class': 'col-lg-5'}).find('img', {'class': 'img-fluid'}).get('src')

    contents['site'] = url
    contents['title'] = title
    contents['ingredients'] = ing_list
    contents['time'] = time
    contents['serving'] = serving
    contents['recipe'] = recipe_list
    contents['calories'] = calories
    contents['carbs'] = carbs
    contents['protein'] = protein
    contents['total_fat'] = total_fat
    # contents['comments'] = com_list
    contents['image'] = image

    return contents

# 전체 페이지 레시피 댓글 가져오기
def get_all_page_comment(nums):
    total = dict()
    title_comments = list()
    a = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        for num in nums:
            links = get_links(num)
            for link in links:
                content = executor.submit(get_contents, link)
                title_comments.append(content.result())

                a += 1
                print(a)

    total['pickuplimes'] = title_comments
    return total

# 메인에서 실행
if __name__ == '__main__':
    # json 저장
    nums = get_page_num()
    total = get_all_page_comment(nums)

    with open(r'C:\Users\workspaces\project_vegan\pickuplimes_all_v2.json', 'w', encoding='utf-8-sig') as file:
        json.dump(total, file, indent="\t")

