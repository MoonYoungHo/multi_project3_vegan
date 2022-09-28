# 장고가 상대경로 잡는데 어려움이 있어 각자 pjt3_vegan_recipes 폴더 위치를 BASE_DIR로 넣어주세요
# BASE_DIR + '그 이후 접근하고자 하는 파일의 경로'로 경로형식을 작성하였습니다
BASE_DIR = 'C:\workspaces\project3\multi_project3_vegan\pjt3_vegan_recipes'


from django.conf import settings
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.shortcuts import render, redirect
from .models import *
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.db import connections
from django.utils.safestring import mark_safe
import requests
from datetime import datetime, timedelta
import random
# 로그인
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password  # 저장된 password 암호화

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import json
from time import sleep
import random

from .Recommender_Systems import *



# 로그인 전 메인
def main(request):
    category_region = dict()
    # category
    category_1_total = Recipe.objects.filter(category='1.India+South America+South Asia <Main ingredients: cumin/coriander/cilantro/lime/avocado/onion>')
    category_1_id_list = list()
    for data in category_1_total:
        category_1_id_list.append(data.recipe_id)
    c1_len = len(category_1_id_list)
    c1_id = random.choice(category_1_id_list)
    category_1 = Recipe.objects.get(recipe_id=c1_id)
    category_region['1'] = '1. India + South America + South Asia'


    category_2_total = Recipe.objects.filter(category='2.East Asia <Main ingredients: rice/soy/sesame/tofu>')
    category_2_id_list = list()
    for data in category_2_total:
        category_2_id_list.append(data.recipe_id)
    c2_len = len(category_2_id_list)
    c2_id = random.choice(category_2_id_list)
    category_2 = Recipe.objects.get(recipe_id=c2_id)
    category_region['2'] = '2. East Asia'


    category_3_total = Recipe.objects.filter(category='3.Dessert+ Bread <Main ingredients: sugar/milk/coconut/vanilla/butter/almond>')
    category_3_id_list = list()
    for data in category_3_total:
        category_3_id_list.append(data.recipe_id)
    c3_len = len(category_3_id_list)
    c3_id = random.choice(category_3_id_list)
    category_3 = Recipe.objects.get(recipe_id=c3_id)
    category_region['3'] = '3. Dessert + Bread'


    category_4_total = Recipe.objects.filter(category='4.West+Etc')
    category_4_id_list = list()
    for data in category_4_total:
        category_4_id_list.append(data.recipe_id)
    c4_len = len(category_4_id_list)
    c4_id = random.choice(category_4_id_list)
    category_4 = Recipe.objects.get(recipe_id=c4_id)
    category_region['4'] = '4. West + Etc'


    # youtube
    url = 'https://www.youtube.com/results?search_query=vegan+recipe&sp=CAMSBAgCEAE%253D'

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # service = Service('/home/ubuntu/Jupyter/chromedriver')
    service = Service(BASE_DIR+'/source/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    # sleep(2)

    v_list = list()
    for i in range(10):
        v_path = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[' + str(
            i + 1) + ']/div[1]/ytd-thumbnail/a'
        v_list.append(driver.find_element(By.XPATH, v_path).get_attribute("href"))

    ran_vid = random.choice(v_list)

    if "shorts" not in ran_vid:
        today_vid = ran_vid.replace('/watch?v=', '/embed/')
    else:
        today_vid = ran_vid.replace('shorts', 'embed')

    return render(request, 'main.html', {'category_1': category_1, 'category_2': category_2, 'category_3': category_3,
                                         'category_4': category_4, 'today_yt': today_vid, 'category_region' : category_region})
                                         # 'category_4': category_4, 'today_yt': today_vid, 'today_tw': today_twitter, 'category_region' : category_region})


def main_login(request):
    #user = request.session['user']
    #print(user)
    return render(request, 'main_login.html')


# 로그인
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        user_name = request.POST.get('user_name', None)
        user_pw = request.POST.get('user_pw', None)

        err_data = {}
        if not (user_name and user_pw):
            err_data['error'] = 'Please enter all fields'
            return render(request, 'login.html', err_data)
        else:
            user = UserInfo.objects.get(user_name=user_name)
            print(user)
            if user_pw == user.user_pw:
                request.session['user'] = user.user_id
                return redirect('/main_login')
            else:
                err_data['error'] = 'Wrong User_id or Password. Please Try Again.'
                return render(request, 'login.html', err_data)

# 로그아웃
def logout(request):
    if request.session.get('user'):
        del(request.session['user'])
    return redirect('/')


def recipe(request, id):

    recipe_one = Recipe.objects.get(recipe_id=id)
    user = request.session['user']
    rated_stars = Rating.objects.filter(user_id=user).filter(recipe_id=id)
    print('rated_stars', rated_stars)
    for data in rated_stars:
        print('stars: ', data.stars)

    pinned = PinnedRecipe.objects.filter(user_id=user).filter(recipe_id=id)
    print('pinned', pinned)
    for data in pinned:
        print('pinned', data.pin_id)


    print('rated', rated_stars)
    # 재료 덩어리 리스트로 만들기 #
    ingredients = recipe_one.ingredients
    ingredients = ingredients.split('[')[1]
    ingredients = ingredients.split(']')[0]
    ingredient_list = list()
    ingredient_list = ingredients.split(',')

    # 레시피 덩어리 리스트로 만들기 #
    recipe_bulk = recipe_one.recipe
    recipe_bulk = recipe_bulk.split('[')[1]
    recipe_bulk = recipe_bulk.split(']')[0]
    recipe_tmplist = list()
    # 레시피 방법 순으로 자르기 ('"' 기준으로 구분 > 홀수 요소만 추출)
    recipe_tmplist = recipe_bulk.split('"')
    recipe_tmplist = recipe_tmplist[1::2]
    # 숫자 표시 지우고 리스트에 담기
    recipe_list = list()
    for recipe_item in recipe_tmplist:

        point = recipe_item.index('.')
        recipe_item = recipe_item[(point + 2):]
        recipe_list.append(recipe_item)

    category_raw = recipe_one.category
    category_index = category_raw.find('<')
    if category_index != -1:
        category_region = category_raw[:category_index]
    else:
        category_region = category_raw

    return render(request, 'recipe.html', {'list': recipe_one, 'ingredient_list': ingredient_list, 'recipe_list': recipe_list, 'category_region': category_region, 'rated_stars': rated_stars})

def rate(request, id):
    recipe_one = Recipe.objects.get(recipe_id=id)
    user = request.session['user']
    stars = request.POST.get('ratingRadioOptions', None)
    print(user)
    print(stars)
    rating = Rating(
        user_id=user,
        recipe_id=id,
        selected_recipe_name=recipe_one.title,
        stars=stars
    )
    rated_stars = Rating.objects.filter(user_id=user).filter(recipe_id=id)
    print(rated_stars)
    if rated_stars != '<QuerySet []>':
        rating.save()
    else:
        pass
    return redirect('/recipe/'+str(id))

def signup_1(request):
    if request.method == 'GET':
        return render(request, 'signup_1.html')
    elif request.method == 'POST':
        user_name = request.POST.get('user_name', None)
        user_pw = request.POST.get('user_pw', None)
        re_user_pw = request.POST.get('re_user_pw', None)

        err_data = {}
        if not(user_name and user_pw and re_user_pw):
            err_data['error'] = 'Please enter all fields'
            return render(request, 'signup_1.html', err_data)
        elif user_pw != re_user_pw:
            err_data['error'] = 'Please check the password'
            return render(request, 'signup_1.html', err_data)
        else:
            user = UserInfo (
                user_name = user_name,
                user_pw = user_pw,
            )
            user.save()

            return redirect('/signup_2/')


def signup_2(request):
    # category
    category_1_total = Recipe.objects.filter(
        category='1.India+South America+South Asia <Main ingredients: cumin/coriander/cilantro/lime/avocado/onion>')
    category_1_id_list = list()
    for data in category_1_total:
        category_1_id_list.append(data.recipe_id)
    c1_len = len(category_1_id_list)
    c1_id = random.choice(category_1_id_list)
    category_1 = Recipe.objects.get(recipe_id=c1_id)

    return render(request, 'signup_2.html', {'category_1': category_1})

def signup_3(request):
    # category
    category_2_total = Recipe.objects.filter(category='2.East Asia <Main ingredients: rice/soy/sesame/tofu>')
    category_2_id_list = list()
    for data in category_2_total:
        category_2_id_list.append(data.recipe_id)
    c2_len = len(category_2_id_list)
    c2_id = random.choice(category_2_id_list)
    category_2 = Recipe.objects.get(recipe_id=c2_id)

    return render(request, 'signup_3.html', {'category_2': category_2})

def signup_4(request):
    # category
    category_3_total = Recipe.objects.filter(
        category='3.Dessert+ Bread <Main ingredients: sugar/milk/coconut/vanilla/butter/almond>')
    category_3_id_list = list()
    for data in category_3_total:
        category_3_id_list.append(data.recipe_id)
    c3_len = len(category_3_id_list)
    c3_id = random.choice(category_3_id_list)
    category_3 = Recipe.objects.get(recipe_id=c3_id)

    return render(request, 'signup_4.html', {'category_3': category_3})

def signup_5(request):
    # category
    category_4_total = Recipe.objects.filter(category='4.West+Etc')
    category_4_id_list = list()
    for data in category_4_total:
        category_4_id_list.append(data.recipe_id)
    c4_len = len(category_4_id_list)
    c4_id = random.choice(category_4_id_list)
    category_4 = Recipe.objects.get(recipe_id=c4_id)

    return render(request, 'signup_5.html', {'category_4': category_4})

def signup_rate_1(request, id):
    recipe_one = Recipe.objects.get(recipe_id=id)
    user = request.session['user']
    stars = request.POST.get('ratingRadioOptions', None)
    print(user)
    print(stars)
    rating = Rating(
        user_id=user,
        recipe_id=id,
        selected_recipe_name=recipe_one.title,
        stars=stars
    )
    rated_stars = Rating.objects.filter(user_id=user).filter(recipe_id=id)
    print(rated_stars)
    if rated_stars != '<QuerySet []>':
        rating.save()
    else:
        pass
    return redirect('/signup_3/')

def signup_rate_2(request, id):
    recipe_one = Recipe.objects.get(recipe_id=id)
    user = request.session['user']
    stars = request.POST.get('ratingRadioOptions', None)
    print(user)
    print(stars)
    rating = Rating(
        user_id=user,
        recipe_id=id,
        selected_recipe_name=recipe_one.title,
        stars=stars
    )
    rated_stars = Rating.objects.filter(user_id=user).filter(recipe_id=id)
    print(rated_stars)
    if rated_stars != '<QuerySet []>':
        rating.save()
    else:
        pass
    return redirect('/signup_4/')

def signup_rate_3(request, id):
    recipe_one = Recipe.objects.get(recipe_id=id)
    user = request.session['user']
    stars = request.POST.get('ratingRadioOptions', None)
    print(user)
    print(stars)
    rating = Rating(
        user_id=user,
        recipe_id=id,
        selected_recipe_name=recipe_one.title,
        stars=stars
    )
    rated_stars = Rating.objects.filter(user_id=user).filter(recipe_id=id)
    print(rated_stars)
    if rated_stars != '<QuerySet []>':
        rating.save()
    else:
        pass
    return redirect('/signup_5/')

def signup_rate_4(request, id):
    recipe_one = Recipe.objects.get(recipe_id=id)
    user = request.session['user']
    stars = request.POST.get('ratingRadioOptions', None)
    print(user)
    print(stars)
    rating = Rating(
        user_id=user,
        recipe_id=id,
        selected_recipe_name=recipe_one.title,
        stars=stars
    )
    rated_stars = Rating.objects.filter(user_id=user).filter(recipe_id=id)
    print(rated_stars)
    if rated_stars != '<QuerySet []>':
        rating.save()
    else:
        pass
    return redirect('/main_login/')


def about_us(request):
    return render(request, 'about_us.html')


def pinned_recipe(request):
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday_get = datetime.today() - timedelta(days=1)
    yesterday = yesterday_get.strftime('%Y-%m-%d')

    pinned_all = PinnedRecipe.objects.select_related('recipe')

    # Recipes_list = Recipe.objects.all()
    paginator = Paginator(pinned_all, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        Recipes = paginator.page(page)
    except(EmptyPage, InvalidPage):
        Recipes = paginator.page(paginator.num_pages)

    return render(request, 'pinned_recipe.html', {'list': Recipes})

def search_result(request):
    # sqlalchemy로 연결
    # df = Download_dataset('recipe')
    # print(df)

    # # models.py로 연결
    # queryset = Recipe.objects.all()
    # query, params = queryset.query.sql_with_params()
    # df = pd.read_sql_query(query, connections['default'], params=params)
    # print(df)

    Recipes_list = None

    Recipes_list = Recipe.objects.all()
    paginator = Paginator(Recipes_list, 12)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        Recipes = paginator.page(page)
    except(EmptyPage, InvalidPage):
        Recipes = paginator.page(paginator.num_pages)

    return render(request, 'search_result.html', {'Recipes': Recipes})


def search_result_q(request):
    Recipes = None
    query = None

    if 'q' in request.GET:
        query = request.GET.get('q')
        # __icontains : 대소문자 구분없이 필드값에 해당 query가 있는지 확인 가능
        Recipes = Recipe.objects.all().filter(Q(title__icontains=query) | Q(ingredients__icontains=query))

    paginator = Paginator(Recipes, 12)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        Recipes = paginator.page(page)
    except(EmptyPage, InvalidPage):
        Recipes = paginator.page(paginator.num_pages)

    return render(request, 'search_result_q.html', {'query': query, 'Recipes': Recipes})


# %% 알고리즘 테스트 영역


# %%
def algorithm(request):
    if request.method == 'GET':
        return render(request, 'algorithm.html')


# %%
def show_CBF(request):
    user_id = request.POST['user_id']
    print(user_id)
    CBF(int(user_id))

    # 2초안에 검색결과가 나오게 하고 안되면 2초를 더 줌
    try:
        sleep(2)
        with open(BASE_DIR + '/output/CBF_Recommender/' + 'User_ID_' + str(user_id) + '_CBF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

    except:
        sleep(2)
        with open(BASE_DIR + '/output/CBF_Recommender/' + 'User_ID_' + str(user_id) + '_CBF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

    # json에서 각 열을 list 형식으로 담아옴
    recommended_recipe = list(recommender_json['recommended_recipe'].values())
    user_preferred_recipe = list(recommender_json['user_preferred_recipe'].values())
    ingredients_cosine_similarity = list(recommender_json['ingredients_cosine_similarity'].values())

    return render(request, 'algorithm_manage/Show_CBF.html',
                  {'recommended_recipe': recommended_recipe,
                   'user_preferred_recipe': user_preferred_recipe,
                   'ingredients_cosine_similarity': ingredients_cosine_similarity})


# %%
def show_CF(request):
    user_id = request.POST['user_id']
    print(user_id)
    CF(int(user_id))

    # 2초안에 검색결과가 나오게 하고 안되면 2초를 더 줌
    try:
        sleep(2)
        with open(BASE_DIR + '/output/CF_Recommender/' + 'User_ID_' + str(user_id) + '_CF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

    except:
        sleep(2)
        with open(BASE_DIR + '/output/CF_Recommender/' + 'User_ID_' + str(user_id) + '_CF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

            # datafram에서 각 열을 list 형식으로 담아옴
    recommended_recipe = list(recommender_json['recommended_recipe'].values())
    user_preferred_recipe = list(recommender_json['user_preferred_recipe'].values())

    return render(request, 'algorithm_manage/Show_CF.html',
                  {'recommended_recipe': recommended_recipe,
                   'user_preferred_recipe': user_preferred_recipe})


def show_Rating(request):
    # user_idf를 정수로
    user_id = request.POST['user_id']
    user_id = int(user_id)
    # Rating 정보를 DB에서 불러옴
    Download_Rating()

    rating = pd.read_json(BASE_DIR + '/output/User_Dummy_data')

    # json에서 각 열을 list 형식으로 담아옴
    user_rating = rating[rating['user_id'] == user_id]
    selected_recipe_name = list(user_rating['selected_recipe_name'].tolist())
    stars = list(user_rating['stars'].tolist())

    return render(request, 'algorithm_manage/Show_Rating.html',
                  {'selected_recipe_name': selected_recipe_name,
                   'stars': stars})


# %% 모델 업데이트 및 더메 데이터 제작

# %% 클러스터링 업데이트
def update_cluster(request):
    Make_Clusters()
    return render(request, 'algorithm.html')


# %% CBF 모델 업데이트
def update_CBF(request):
    Make_CBF_model()
    return render(request, 'algorithm.html')


# %% CF 모델 업데이트
def Update_CF(request):
    Make_CF_model()
    return render(request, 'algorithm.html')


# %% 더미 데이터 제작하기
def make_dummy(request):
    Make_dummy_5stars()
    return render(request, 'algorithm.html')


# %% CBF 추천하기
# def Recommend_by_algorithm(request):
#     USER_ID = 230
#
#     #CBF
#
#
#     for i in range(len(recommended_recipe)):
#         globals()['recipe_{}'.format(i + 1)] = dict(
#             zip(list(recommended_recipe.columns), tuple(recommended_recipe.iloc[i])))
#
#         # 카테고리명을 category 지역구분과 재료 구분으로 분리함
#         globals()['recipe_{}'.format(i + 1)]['category_region'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[0].strip()
#         try:
#             globals()['recipe_{}'.format(i + 1)]['category_integredients'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[1].split(':')[1].replace('>', '').strip()
#         except:
#             globals()['recipe_{}'.format(i + 1)]['category_integredients'] = None
#
#     recipe_lists = []
#     for i in range(len(recommended_recipe)):
#         recipe_lists.append(globals()['recipe_{}'.format(i + 1)])
#
#     #CF
#     recommended_recipe = Make_Recommended_RecipeData(user_id=USER_ID, Recommender=CF)
#     recipe_lists2=[]
#     for i in range(len(recommended_recipe)):
#         globals()['recipe_{}'.format(i+1)]=dict(zip(list(recommended_recipe.columns),tuple(recommended_recipe.iloc[i])))
#
#
#         # 카테고리명을 category 지역구분과 재료 구분으로 분리함
#         globals()['recipe_{}'.format(i + 1)]['category_region'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[0].strip()
#         try:
#             globals()['recipe_{}'.format(i + 1)]['category_integredients'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[1].split(':')[1].replace('>', '').strip()
#         except:
#             globals()['recipe_{}'.format(i + 1)]['category_integredients'] = None
#
#     recipe_lists2 = []
#     for i in range(len(recommended_recipe)):
#         recipe_lists2.append(globals()['recipe_{}'.format(i + 1)])
#     print(recipe_lists2)
#
#     return render(request, 'main_login.html', {'recipe_lists':recipe_lists, 'recipe_lists2':recipe_lists2})

#%%
def Recommend_by_algorithm(request):
    USER_ID=230
    Recommended_Recipe_CBF= Recommended_RecipeData_by_CBF(user_id=USER_ID)
    Recommended_Recipe_CF= Recommended_RecipeData_by_CF(user_id=USER_ID)

    for i in range(len(Recommended_Recipe_CBF)):
        globals()['recipe_{}'.format(i+1)]=dict(zip(list(Recommended_Recipe_CBF.columns),tuple(Recommended_Recipe_CBF.iloc[i])))

        # 카테고리명을 category 지역구분과 재료 구분으로 분리함
        globals()['recipe_{}'.format(i + 1)]['category_region'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[0].strip()
        try:
            globals()['recipe_{}'.format(i + 1)]['category_integredients'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[1].split(':')[1].replace('>', '').strip()
        except:
            globals()['recipe_{}'.format(i + 1)]['category_integredients'] = None

    recipe_lists=[]
    for i in range(len(Recommended_Recipe_CBF)):
        recipe_lists.append(globals()['recipe_{}'.format(i+1)])

    for i in range(len(Recommended_Recipe_CF)):
        globals()['recipe_{}'.format(i+1)]=dict(zip(list(Recommended_Recipe_CF.columns),tuple(Recommended_Recipe_CF.iloc[i])))

        # 카테고리명을 category 지역구분과 재료 구분으로 분리함
        globals()['recipe_{}'.format(i + 1)]['category_region'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[0].strip()
        try:
            globals()['recipe_{}'.format(i + 1)]['category_integredients'] = globals()['recipe_{}'.format(i + 1)]['category'].split('<')[1].split(':')[1].replace('>', '').strip()
        except:
            globals()['recipe_{}'.format(i + 1)]['category_integredients'] = None

    recipe_lists2=[]
    for i in range(len(Recommended_Recipe_CF)):
        recipe_lists2.append(globals()['recipe_{}'.format(i+1)])


    return render(request, 'main_login.html', {'recipe_lists':recipe_lists, 'recipe_lists2':recipe_lists2})



#%%
#
# def Recommend_by_CF(request):
#     import time
#     USER_ID = 230
#     recommended_recipe = Make_Recommended_RecipeData(user_id=USER_ID, Recommender=CF)
#     recipe_lists2=[]
#     sleep(3)
#     for i in range(len(recommended_recipe)):
#         globals()['recipe_{}'.format(i+1)]=dict(zip(list(recommended_recipe.columns),tuple(recommended_recipe.iloc[i])))
#         recipe_lists2.append(globals()['recipe_{}'.format(i+1)])
#
#     return render(request, 'main_login.html', {'recipe_lists2':recipe_lists2})
#
# #%%
#%%

