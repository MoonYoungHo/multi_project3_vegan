from django.shortcuts import render
from .models import *
import pandas as pd
from datetime import datetime, timedelta
from django.db import connections
from .Recommender_Systems import *

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

def algorithm(request):
    return render(request, 'algorithm.html')

def Show_CBF(request):
    if request.method == 'GET':
        user_id=request
        user_id2=request.GET['user_id']
        print(user_id)
        print(user_id2)
        return render(request, 'algorithm.html')
    else:
        user_id=request.POST['user_id']
        print(user_id)
        CBF(user_id)
        lists = json.loads('./Output/CBF_Recommender/User_ID_'+str(user_id)+'_CBF_results.json')
        return render(request, 'algorithm.html', { 'lists': lists})


#%%
