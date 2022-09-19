from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

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

def categories(request):
    return render(request, 'categories.html')

