from django.shortcuts import render

# Create your views here.
def splash_screen_view(request):
    return render(request, "main/splash_screen.html")