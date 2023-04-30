from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json


# 전체 페이지 수 가져오기
def get_page_num():
    #url = 'https://www.bbcgoodfood.com/search/recipes?q=Vegan&sort=-popular'
    #resp = requests.get(url)
    #soup = BeautifulSoup(resp.text, 'html.parser')
    #page_nums = soup.find('div', {'class': 'pagination'})
    #max_num = page_nums.find('span', {'class': 'sr-only'})
    # 로딩 시간 너무 오래 걸려서 에러 발생 - 페이지 수 임의 지정
    nums = list(range(1, 31))

    return nums

# 입력한 페이지의 전체 레시피 링크 가져오기
def get_links(i):
    link_list = list()
    #url = 'https://www.bbcgoodfood.com/search/recipes/page/' + str(i) + '/?q=Vegan&sort=-date'
    url = 'https://www.bbcgoodfood.com/search/recipes/page/' + str(i) + '/?q=Vegan&sort=-popular'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    lis = soup.find_all('div', {'class': 'standard-card-new__thumbnail'})

    for li in lis:
        link_list.append('https://www.bbcgoodfood.com' + li.contents[1].get('href'))

    return link_list

# 입력한 링크의 출처(site), 레시피명(title), 재료 리스트(ingredients), 조리시간(time), 분량(serving), 레시피(recipe),
# 영양 성분(nutrition), 댓글 리스트(comments), 이미지(image) 가져오기
def get_contents(url):
    global cookTime, calories, carbs, protein, total_fat
    contents = dict()
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # 출처(site)
    # 함수에 입력받는 url 사용

    # 레시피명(title)
    title = soup.find('h1', {'class': 'heading-1'}).text

    # 재료 리스트(ingredients)
    ingredients = soup.find('section', {'class': 'recipe__ingredients col-12 mt-md col-lg-6'}).find_all('li')
    ing_list = list()
    for ingredient in ingredients:
        ing_list.append(ingredient.text)

    # 조리시간(time)
    cookTime_raw = soup.find_all('li', {'class': 'body-copy-small list-item'})
    if cookTime_raw:
        cookTime_list = list()
        for cookTime in cookTime_raw:
            cookTime_list.append(cookTime.text)
        for cookTime in cookTime_list:
            if 'Cook:' in cookTime:
                cookTime = cookTime.split('Cook:')[1]
            else:
                pass
    else:
        cookTime = ''

    # 분량(serving)
    servings = soup.find('ul', {'class': 'post-header__row post-header__planning list list--horizontal'}).text
    val = "Serves" not in servings
    if val:
        servings = '1'
    else:
        servings = servings.split('Serves')[1].split()[0]
    servings = str(servings)

    # 레시피(recipe)
    recipe_raw = soup.find('ul', {'class': 'grouped-list__list list'}).find_all('div', {'class': 'editor-content'})
    recipe_list = list()
    for i in range(len(recipe_raw)):
        recipe_list.append(str(i + 1) + ". " + recipe_raw[i].text.replace('\n', ''))

    # 영양 성분(nutrition)
    nutrition = soup.find('table', {'class': 'key-value-blocks hidden-print mt-xxs'})
    if nutrition == None:
        pass
    else:
        calories = nutrition.find_all('tr')[1].text.split('kcal')[1] + ' kcal'
        carbs = nutrition.find_all('tr')[4].text.split('carbs')[1]
        protein = nutrition.find_all('tr')[7].text.split('protein')[1]
        total_fat = nutrition.find_all('tr')[2].text.split('fat')[1]

    # 댓글 리스트(comments) / 보류
    # vegan_review = soup.find_all('p', {'class': 'mt-reset'})
    # com_list = list()
    # for comments in vegan_review:
    #     comments_raw = comments.text, comments.get_attribute('href')
    #     comments_list = comments_raw[0]
    #     com_list.append(comments_list)

    # 이미지(image)
    image = soup.find('div', {'class': 'image chromatic-ignore post-header-image image--fluid image--scaled-up'}) \
        .find('img', {'class': 'image__img'}).get('src')

    contents['site'] = url
    contents['title'] = title
    contents['ingredients'] = ing_list
    contents['time'] = cookTime
    contents['serving'] = servings + ' servings'
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

    total['bbcgoodfood'] = title_comments
    return total

# 메인에서 실행
if __name__ == '__main__':
    # json 저장
    nums = get_page_num()
    total = get_all_page_comment(nums)

    with open(r'C:\Users\workspaces\project_vegan\bbcgoodfood_all_v2.json', 'w', encoding='utf-8-sig') as file:
        json.dump(total, file, indent="\t")
