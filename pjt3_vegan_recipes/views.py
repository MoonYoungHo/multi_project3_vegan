# 장고가 상대경로 잡는거에 어려움이 있어 각자 pjt3_vegan_recipes 폴더 위치를 BASE_DIR로 넣어주세요
# BASE_DIR +'그 이후 접근하고자 하는 파일의 경로'로 경로형식을 작성하였습니다
BASE_DIR= '/Users/wooseongkyun/코드_아카이브/멀캠_프로젝트들/multi_project3_vegan/pjt3_vegan_recipes'


#%%
from django.shortcuts import render
from .models import *
import pandas as pd
from datetime import datetime, timedelta
from django.db import connections
from .Recommender_Systems import *

#기타 코드
import json
import time

def main(request):
    return render(request, 'main.html')

def main_login(request):

    return render(request, 'main_login.html')

def login(request):
    return render(request, 'login.html')

def recipe(request, id):

    recipe_one = Recipe.objects.get(recipe_id=id)

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
        recipe_item = recipe_item[(point+2):]
        recipe_list.append(recipe_item)

    return render(request, 'recipe.html', {'list': recipe_one, 'ingredient_list': ingredient_list, 'recipe_list': recipe_list})

def signup_1(request):
    return render(request, 'signup_1.html')

def signup_2(request):
    return render(request, 'signup_2.html')

def about_us(request):
    return render(request, 'about_us.html')

def pinned_recipe(request):

    today = datetime.today().strftime('%Y-%m-%d')
    yesterday_get = datetime.today() - timedelta(days=1)
    yesterday = yesterday_get.strftime('%Y-%m-%d')

    pinned_all = ViewPinnedRecipeRecipe.objects.all()

    for data in pinned_all:
        print(data)






    return render(request, 'pinned_recipe.html', {'list' : pinned_all})

def search_result(request):

    # sqlalchemy로 연결
    # df = Download_dataset('recipe')
    # print(df)

    # # models.py로 연결
    # queryset = Recipe.objects.all()
    # query, params = queryset.query.sql_with_params()
    # df = pd.read_sql_query(query, connections['default'], params=params)
    # print(df)



    return render(request, 'search_result.html')

def Make_dummy(request):
    Make_dummy_5stars()


    return render(request, 'search_result.html')


#%% 알고리즘 테스트 영역

#%%
def algorithm(request):
    if request.method == 'GET':
        return render(request, 'algorithm.html')

#%%
def Show_CBF(request):
    user_id=request.POST['user_id']
    print(user_id)
    CBF(int(user_id))

    #2초안에 검색결과가 나오게 하고 안되면 2초를 더 줌
    try:
        time.sleep(2)
        with open(BASE_DIR+'/Output/CBF_Recommender/'+'User_ID_'+str(user_id)+'_CBF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

    except:
        time.sleep(2)
        with open(BASE_DIR+'/Output/CBF_Recommender/'+'User_ID_'+str(user_id)+'_CBF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

    #json에서 각 열을 list 형식으로 담아옴
    recommended_recipe= list(recommender_json['recommended_recipe'].values())
    user_preferred_recipe= list(recommender_json['user_preferred_recipe'].values())
    ingredients_cosine_similarity= list(recommender_json['ingredients_cosine_similarity'].values())

    return render(request, 'algorithm_manage/Show_CBF.html',\
                  {'recommended_recipe': recommended_recipe,\
                   'user_preferred_recipe': user_preferred_recipe,\
                   'ingredients_cosine_similarity': ingredients_cosine_similarity})


#%%
def Show_CF(request):
    user_id=request.POST['user_id']
    print(user_id)
    CF(int(user_id))

    #2초안에 검색결과가 나오게 하고 안되면 2초를 더 줌
    try:
        time.sleep(2)
        with open(BASE_DIR+'/Output/CF_Recommender/'+'User_ID_'+str(user_id)+'_CF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

    except:
        time.sleep(2)
        with open(BASE_DIR+'/Output/CF_Recommender/'+'User_ID_'+str(user_id)+'_CF_results.json', 'r',
                  encoding='utf-8') as f:
            recommender_json = json.load(f)

            #datafram에서 각 열을 list 형식으로 담아옴
    recommended_recipe= list(recommender_json['recommended_recipe'].values())
    user_preferred_recipe= list(recommender_json['user_preferred_recipe'].values())

    return render(request, 'algorithm_manage/Show_CF.html', \
                  {'recommended_recipe': recommended_recipe, \
                   'user_preferred_recipe': user_preferred_recipe})

#%%
def Show_Rating(request):
    #user_idf를 정수로
    user_id=request.POST['user_id']
    user_id=int(user_id)
    #Rating 정보를 DB에서 불러옴
    Download_Rating()

    rating= pd.read_json(BASE_DIR+'/Output/User_Dummy_data')

    #json에서 각 열을 list 형식으로 담아옴
    user_rating= rating[rating['user_id']== user_id]
    selected_recipe_name= list(user_rating['selected_recipe_name'].tolist())
    stars= list(user_rating['stars'].tolist())

    return render(request, 'algorithm_manage/Show_Rating.html', \
                  {'selected_recipe_name': selected_recipe_name,\
                   'stars':stars})

#%% 모델 업데이트 및 더메 데이터 제작

#%% 클러스터링 업데이트
def Update_Cluster(request):
    Make_Clusters()
    return render(request, 'algorithm.html')

#%% CBF 모델 업데이트
def Update_CBF(request):
    Make_CBF_model()
    return render(request, 'algorithm.html')

#%% CF 모델 업데이트
def Update_CF(request):
    Make_CF_model()
    return render(request, 'algorithm.html')

#%% 더미 데이터 제작하기
def Make_Dummy(request):
    Make_dummy_5stars()
    return render(request, 'algorithm.html')

#%%

