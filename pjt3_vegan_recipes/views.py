# 장고가 상대경로 잡는거에 어려움이 있어 각자 pjt3_vegan_recipes 폴더 위치를 BASE_DIR로 넣어주세요
# BASE_DIR +'그 이후 접근하고자 하는 파일의 경로'로 경로형식을 작성하였습니다
BASE_DIR= '/Users/wooseongkyun/코드_아카이브/멀캠_프로젝트들/multi_project3_vegan/pjt3_vegan_recipes'


#%%
from django.conf import settings
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.shortcuts import render, redirect
from .models import *
from datetime import datetime, timedelta
from .Recommender_Systems import *
import random
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
# 로그인
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password  # 저장된 password 암호화



#기타 코드
import json
import time

# 로그인 전 메인
def main(request):

    category_1_total = Recipe.objects.filter(category='1.India+South America+South Asia <Main ingredients: cumin/coriander/cilantro/lime/avocado/onion>')
    category_1_id_list = list()
    for data in category_1_total:
        category_1_id_list.append(data.recipe_id)
    c1_len = len(category_1_id_list)
    c1_id = random.choice(category_1_id_list)
    category_1 = Recipe.objects.get(recipe_id=c1_id)

    category_2_total = Recipe.objects.filter(category='2.East Asia <Main ingredients: rice/soy/sesame/tofu>')
    category_2_id_list = list()
    for data in category_2_total:
        category_2_id_list.append(data.recipe_id)
    c2_len = len(category_2_id_list)
    c2_id = random.choice(category_2_id_list)
    category_2 = Recipe.objects.get(recipe_id=c2_id)

    category_3_total = Recipe.objects.filter(category='3.Dessert+ Bread <Main ingredients: sugar/milk/coconut/vanilla/butter/almond>')
    category_3_id_list = list()
    for data in category_3_total:
        category_3_id_list.append(data.recipe_id)
    c3_len = len(category_3_id_list)
    c3_id = random.choice(category_3_id_list)
    category_3 = Recipe.objects.get(recipe_id=c3_id)

    category_4_total = Recipe.objects.filter(category='4.West+Etc')
    category_4_id_list = list()
    for data in category_4_total:
        category_4_id_list.append(data.recipe_id)
    c4_len = len(category_4_id_list)
    c4_id = random.choice(category_4_id_list)
    category_4 = Recipe.objects.get(recipe_id=c4_id)


    return render(request, 'main.html', {'category_1': category_1, 'category_2': category_2, 'category_3': category_3, 'category_4': category_4})

class MainLoginView(LoginRequiredMixin, TemplateView):
    template_name = 'main_login.html'


main_login = MainLoginView.as_view()

user = get_user_model()


class SignupView(CreateView):
    model = User
    form_class = UserCreationForm
    success_url = settings.LOGIN_REDIRECT_URL
    template_name = 'signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        users = self.object
        auth_login(self.request, users)
        return response


signup = SignupView.as_view()


def signup_info(request):
    return render(request, 'signup_info.html')


def signup_recipe(request):
    return render(request, 'signup_recipe.html')


def main_login(request):

    return render(request, 'main_login.html')

# 로그인
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    elif request.method == 'POST':
        user_id = request.POST.get('user_id', None)
        user_pw = request.POST.get('user_pw', None)
        res_data = {}
        if not (user_id and user_pw):
            res_data['error'] = 'Please enter ID and Password!'
        else:
            user_check = UserInfo.objects.get(user_id=user_id)
            if check_password(user_pw, user_check.password):
                user_id = UserInfo.user_id
                request.session['user'] = user_id
                return redirect('/main_login')
            else:
                res_data['error'] = 'Wrong ID or Password'
        return render(request, 'login.html', res_data)
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

    category_raw = recipe_one.category
    category_index = category_raw.find('<')
    if category_index != -1:
        category_region = category_raw[:category_index]
    else:
        category_region = category_raw

    return render(request, 'recipe.html', {'list': recipe_one, 'ingredient_list': ingredient_list, 'recipe_list': recipe_list, 'category_region': category_region})

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
    paginator = Paginator(Recipes_list, 10)
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

    paginator = Paginator(Recipes, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        Recipes = paginator.page(page)
    except(EmptyPage, InvalidPage):
        Recipes = paginator.page(paginator.num_pages)

    return render(request, 'search_result_q.html', {'query': query, 'Recipes': Recipes})

def Make_dummy(request):
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

