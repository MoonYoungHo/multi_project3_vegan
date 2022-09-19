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

def blog(request):
    return render(request, 'blog.html')

def aboutme(request):
    return render(request, 'about-me.html')

def pinned_recipe(request):
    return render(request, 'pinned_recipe.html')

