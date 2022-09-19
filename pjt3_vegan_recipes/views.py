from django.shortcuts import render

def main(request):
    return render(request, 'main.html')

def main_login(request):
    return render(request, 'main_login.html')

def login(request):
    return render(request, 'login.html')

# def recipe(request):
#     return render(request, 'recipe.html')

def contact(request):
    return render(request, 'contact.html')

def blog(request):
    return render(request, 'blog.html')

def categories(request):
    return render(request, 'categories.html')

