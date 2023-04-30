from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json


# 전체 페이지 수 가져오기
def get_page_num():
    url = 'https://www.feastingathome.com/recipes/'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    max_num = soup.find('div', {'class': 'nav-links'}).contents[6].text
    nums = list(range(1, int(max_num) + 1))
    # nums = list(range(1, 3))

    return nums

# 입력한 페이지의 전체 레시피 링크 가져오기
def get_links(i):
    link_list = list()
    url = 'https://www.feastingathome.com/recipes/?fwp_paged=' + str(i)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    lis = soup.find_all('a', {'class': 'entry-image-link'})

    for li in lis:
        link_list.append(li.get('href'))

    return link_list

# 입력한 링크의 출처(site), 레시피명(title), 재료 리스트(ingredients), 조리시간(time), 분량(serving), 레시피(recipe),
# 영양 성분(nutrition), 댓글 리스트(comments), 이미지(image) 가져오기
def get_contents(url):
    global calories, carbs, protein, total_fat
    contents = dict()
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # 출처(site)
    # 함수에 입력받는 url 사용

    # 레시피명(title)
    title = soup.find('h1', {'class': 'entry-title'}).text

    # 재료 리스트(ingredients),
    ingredients_raw = soup.find('div', {'class': 'tasty-recipes-ingredients-body'})
    if ingredients_raw:
        ingredients = ingredients_raw.text.split('\n')
        ing_list = list()
        for ing in ingredients:
            if ing == '':
                pass
            else:
                ing_list.append(ing.replace('\xa0', ''))
    else:
        ing_list = []

    # 조리시간(time)
    cookTime_raw = soup.find('div', {'class': 'tasty-recipes-details'})
    if cookTime_raw:
        cookTimeText = cookTime_raw.text
        val = "Total Time:" not in cookTimeText
        if val:
            cookTime = ''
        else:
            cookTime = cookTime_raw.find('li', {'class': 'total-time'}).text.split('Total Time: ')[1]
        cookTime = str(cookTime)
    else:
        cookTime = ''

    # 분량(serving)
    servings_raw = soup.find('div', {'class': 'tasty-recipes-details'})
    if servings_raw:
        servingsText = servings_raw.text
        val = "Yield:" not in servingsText
        if val:
            serving = '1'
        else:
            serving = servings_raw.find('li', {'class': 'yield'}).text.split('Yield: ')[1]
        serving = str(serving) + ' serving'
    else:
        serving = ''

    # 레시피(recipe)
    recipes_raw = soup.find('div', {'class': 'tasty-recipes-instructions-body'})
    if recipes_raw:
        recipes = recipes_raw.text.split('\n')
        recipes_list = list()
        recipe_list = list()
        for recipe in recipes:
            if recipe == '':
                pass
            else:
                recipes_list.append(recipe.replace('\xa0', ''))
        for i in range(len(recipes_list)):
            recipe_list.append(str(i + 1) + ". " + recipes_list[i])
    else:
        recipe_list = []

    # 영양 성분(nutrition)
    nutrition_raw = soup.find('div', {'class': 'tasty-recipes-nutrition'})
    if nutrition_raw:
        nutrition_raw_text = nutrition_raw.text.split('\n')
        for nutrition in nutrition_raw_text:
            if 'Calories:' in nutrition:
                if nutrition.split('Calories: ')[1]:
                    cal = nutrition.split('Calories: ')[1]
                    calories = cal + ' Kcal'
                else:
                    calories = ''
            else:
                pass
        for nutrition in nutrition_raw_text:
            if 'Carbohydrates:' in nutrition:
                car = nutrition.split('Carbohydrates: ')[1]
                carbs = car
            else:
                pass
        for nutrition in nutrition_raw_text:
            if 'Protein:' in nutrition:
                prt = nutrition.split('Protein: ')[1]
                protein = prt
            else:
                pass
        for nutrition in nutrition_raw_text:
            if 'Fat:' in nutrition:
                fat = nutrition.split('Fat: ')[1]
                total_fat = fat
            else:
                pass
    else:
        pass

    # 댓글 리스트(comments) / 보류
    # comments = soup.select('ol[class=comment-list] > li > article > div[class=comment-content]')
    # com_list = list()
    # for comment in comments:
    #     com_list.append(comment.text.replace('\n', ''))

    # 이미지(image)
    images = soup.find('div', {'class': 'entry-content'}).find_all('img')
    imgs_list = list()
    img_list = list()
    for image in images:
        if image.get('src') == None:
            pass
        else:
            imgs_list.append(image.get('src'))
    for img in imgs_list:
        if 'https://www.feastingathom' in img:
            img_list.append(img)

    contents['site'] = url
    contents['title'] = title
    contents['ingredients'] = ing_list
    contents['time'] = cookTime
    contents['serving'] = serving
    contents['recipe'] = recipe_list
    contents['calories'] = calories
    contents['carbs'] = carbs
    contents['protein'] = protein
    contents['total_fat'] = total_fat
    # contents['comments'] = com_list
    contents['image'] = img_list[0]

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

    total['feastingathome'] = title_comments
    return total

# 메인에서 실행
if __name__ == '__main__':
    # json 저장
    nums = get_page_num()
    total = get_all_page_comment(nums)

    with open(r'C:\Users\workspaces\project_vegan\feastingathome_all_v2.json', 'w', encoding='utf-8-sig') as file:
        json.dump(total, file, indent="\t")
