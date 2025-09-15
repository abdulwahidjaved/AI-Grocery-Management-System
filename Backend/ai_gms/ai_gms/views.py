from django.shortcuts import render


def home(request):
    return render(request, "home/home.html")
    
def features(request):
    return render(request, "features/features.html")
    
def about(request):
    return render(request, "about/about.html")
    
def contact(request):
    return render(request, "contact/contact.html")
    
