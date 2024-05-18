from django.shortcuts import render


def home_page(request):
    context = {
        "title": "Agroparser",
        "content": "Home page",
    }

    return render(request, "home.html", context)
