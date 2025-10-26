from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.books.models import Books
from apps.users.models import Users
from .models import Borrows
from django.utils import timezone
# Create your views here.
def isAdmin(user):
    return user.is_authenticated and user.role == Users.Role.ADMIN

def isLibrarian(user):
    return user.is_authenticated and user.role == Users.Role.LIBRARIAN

def isAdminOrLibrarian(user):
    return isAdmin(user) or isLibrarian(user)

@login_required
def getMyBorrowHistory(request):
    myBorrows = Borrows.objects.filter(user = request.user).order_by('-borrow_date')
    return render(request, 'myBorrowHistory.html', {'myBorrows': myBorrows})

@login_required
@user_passes_test(isAdminOrLibrarian)
def getAllBorrowHistory(request):
    if isAdmin(request.user):
        allBorrows = Borrows.objects.filter(user__role__in=[Users.Role.LIBRARIAN, Users.Role.USER]).order_by('-borrow_date')
    elif isLibrarian(request.user):
        allBorrows = Borrows.objects.filter(user__role__in = Users.Role.USER).order_by('-borrow_date')
    return render(request, 'allBorrowHistory.html', {'allBorrows': allBorrows})    