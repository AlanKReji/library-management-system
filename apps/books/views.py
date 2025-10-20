from django.shortcuts import render
from .models import Books

def home(request):
    """
    Displays all non-deleted books on the home page (acts as the main catalog view).
    """
    books = Books.objects.filter(isDeleted=False).order_by('title')
    return render(request, 'home.html', {'books': books})
