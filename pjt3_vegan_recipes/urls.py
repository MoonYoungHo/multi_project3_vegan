"""pjt3_vegan_recipes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recipe/<int:id>', views.recipe, name='recipe'),
    path('signup_1/', views.signup_1, name='signup_1'),
    path('signup_2/', views.signup_2, name='signup_2'),
    path('signup/', views.signup, name='signup'),
    path('signup_info/', views.signup_info, name='signup_info'),
    path('signup_recipe/', views.signup_recipe, name='signup_recipe'),
    path('', views.main, name='main'),
    path('main_login/', views.main_login, name='main_login'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('pinned_recipe/', views.pinned_recipe, name='pinned_recipe'),
    path('search_result/', views.search_result, name='search_result'),
    path('search_result_q/', views.search_result_q, name='search_result_q'),
    path('about_us/', views.about_us, name='about_us'),
    path('algorithm/', views.algorithm, name='algorithm'),
    #알고리즘 작동 확인용
    path('Show_CBF/', views.show_CBF, name='Show_CBF'),
    path('Show_CF/', views.show_CF, name='Show_CF'),
    path('Show_Rating/', views.show_Rating, name='Show_Rating'),
    #모델 업데이트 및 더미데이터 제작
    path('Update_Cluster/', views.update_cluster, name='Update_Cluster'),
    path('Update_CBF/', views.update_CBF, name='Update_CBF'),
    path('Update_CF/', views.Update_CF, name='Update_CF'),
    path('Make_Dummy/', views.make_dummy, name='Make_Dummy'),
    path('Recommend_by_CBF/', views.recommend_by_CBF, name='Recommend_by_CBF'),
]
