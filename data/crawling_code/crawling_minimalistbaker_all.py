from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import json

# 전체 페이지 수 가져오기
def get_page_num():
    max_num = 80
    nums = list(range(1, (int(max_num) + 1)))

    return nums

# 입력한 페이지의 전체 레시피 링크 가져오기
def get_links(i):
    link_list = list()
    url = 'https://minimalistbaker.com/recipe-index/?fwp_special-diet=vegetarian&fwp_paged=' + str(i)
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    articles = soup.find_all('a', {'class': 'post-summary__image'})
    for article in articles:
        try:
            link_list.append(article.get('href'))
        except:
            pass

    return link_list

# 입력한 링크의 제목, 댓글, 레시피, 재료, 조리시간, 분량, 영양정보, 이미지 가져오기
def get_contents(url):
    global calories, carbs, protein, total_fat
    contents = dict()
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # 제목
    title = soup.find('h1', {'class': 'entry-title'})
    if title:
        title = title.text
    else:
        pass

    # 댓글
    com_list = list()

    comments = soup.find_all('ol', {'class': 'comment-list'})
    for comment in comments:
        for c_num in range(1, 10000, 3):
            try:
                com_list.append((comment.contents[c_num].contents[1].contents[3].text).strip('\n'))
            except:
                pass

    # 댓글의 갯수
    comments_num = len(com_list) + 1

    # 레시피 내용
    recipes_list = list()
    recipe = soup.find('ul', {'class': 'wprm-recipe-instructions'})

    if recipe:
        # 레시피 단계
        steps = int(recipe.contents[-1].get('id').split('-')[-1])
        for step in range(0, (steps + 1)):
            recipes_list.append(str(step + 1) + '. ' + recipe.contents[step].text)
    else:
        pass

    # 재료
    ingredients_list = list()
    ingredients = soup.find_all('li', {'class': 'wprm-recipe-ingredient'})
    for ingredient in ingredients:
        if ingredient:
            ingredients_list.append(ingredient.text)
        else:
            pass

    # 조리시간
    cooktime = ''
    cooktimes = soup.find_all('div', {
        'class': 'wprm-recipe-meta-container wprm-recipe-times-container wprm-recipe-details-container wprm-recipe-details-container-columns wprm-block-text-normal'})
    for cooktime in cooktimes:
        if cooktime:
            cooktime = cooktime.contents[-1].contents[-1].text
        else:
            pass

    # 분량
    servings = soup.find('span', {'class': 'wprm-recipe-servings-with-unit'})
    if servings:
        servings = servings.text
    else:
        pass

    # 영양정보
    nut_list = list()
    nutrients = soup.find_all('div', {
        'class': 'wprm-nutrition-label-container wprm-nutrition-label-container-simple wprm-block-text-normal'})
    for nutrient in nutrients:
        if nutrient:
            for n_num in range(0, 30):
                try:
                    nut_list.append(nutrient.contents[n_num].text)
                except:
                    pass
        else:
            pass

    if nut_list:
        if nut_list[2].split(' ')[0] == 'Calories:':
            calories = nut_list[2].split(' ')[1] + 'kcal'
        else:
            calories = ''

        if nut_list[4].split(' ')[0] == 'Carbohydrates:':
            carbs = nut_list[4].split(' ')[1] + 'g'
        else:
            carbs = ''

        if nut_list[6].split(' ')[0] == 'Protein:':
            protein = nut_list[6].split(' ')[1] + 'g'
        else:
            protein = ''

        if nut_list[8].split(' ')[0] == 'Fat:':
            total_fat = nut_list[8].split(' ')[1] + 'g'
        else:
            total_fat = ''
    else:
        pass

    # 이미지
    image = soup.find('figure', {'class': 'wp-block-image size-full'})
    if image:
        image = image.contents[0].get('src')
    else:
        pass

    try:
        if recipes_list == [] or title.lower().find('recipe') != -1:
            pass
        else:
            if comments_num > 4:
                # 주소 (사이트)
                contents['site'] = url
                # 제목
                contents['title'] = title
                # 재료
                contents['ingredients'] = ingredients_list
                # 조리시간
                contents['time'] = cooktime
                # 분량
                contents['serving'] = servings
                # 레시피 내용
                contents['recipe'] = recipes_list
                # 칼로리
                contents['calories'] = calories
                # 탄수화물
                contents['carbs'] = carbs
                # 단백질
                contents['protein'] = protein
                # 지방
                contents['total_fat'] = total_fat
                # 댓글
                # contents['comments'] = com_list
                # 이미지
                contents['image'] = image
            else:
                pass
    except:
        pass

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

    total['minimalistbaker'] = title_comments
    return total


# 메인에서 실행
if __name__ == '__main__':
    nums = get_page_num()
    total = get_all_page_comment(nums)

    with open(r'C:\Users\workspaces\project_vegan\minimalistbaker_all_v2.json', 'w', encoding='utf-8-sig') as file:
        json.dump(total, file, indent="\t")

