from django.shortcuts import render

def main(request):
    return render(request, 'main.html')

def main_login(request):
    return render(request, 'main_login.html')

def login(request):
    return render(request, 'login.html')

def recipe(request):
    return render(request, 'recipe.html')

def signup_1(request):
    return render(request, 'signup_1.html')

def signup_2(request):
    return render(request, 'signup_2.html')

def pinned_recipe(request):
    return render(request, 'pinned_recipe.html')

def search_result(request):
    return render(request, 'search_result.html')
