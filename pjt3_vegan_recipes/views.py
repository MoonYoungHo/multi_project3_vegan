from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def recipe(request):
    return render(request, 'recipe.html')

def contact(request):
    return render(request, 'contact.html')

def blog(request):
    return render(request, 'blog.html')

def aboutme(request):
    return render(request, 'about-me.html')

def categories(request):
    return render(request, 'categories.html')

