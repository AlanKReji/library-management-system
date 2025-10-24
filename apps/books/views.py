from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Books
from apps.users.models import Users
from .forms import BookForm  # Added import

def isAdmin(user):
    return user.is_authenticated and user.role == Users.Role.ADMIN

def isLibrarian(user):
    return user.is_authenticated and user.role == Users.Role.LIBRARIAN

def isAdminOrLibrarian(user):
    return isAdmin(user) or isLibrarian(user)

@login_required
def home(request):
    books = Books.objects.filter(isDeleted=False).order_by('title')
    return render(request, 'home.html', {'books': books})

@login_required
def getAllBooks(request):
    books = Books.objects.filter(isDeleted=False).order_by('title')
    return render(request, 'books.html', {'books': books})

@login_required
@user_passes_test(isAdminOrLibrarian)
def addBook(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.total_copies
            book.created_by = request.user
            book.save()
            return redirect('bookDetails', id=book.id)
    else:
        form = BookForm()
    return render(request, 'addBook.html', {'form': form})

@login_required
def bookDetails(request, id):
    book = Books.objects.get(id=id, isDeleted=False)
    return render(request, 'bookDetails.html', {'book': book})

@login_required
@user_passes_test(isAdminOrLibrarian)
def editBook(request, id):
    book = Books.objects.get(id=id, isDeleted=False)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            old_total = Books.objects.get(id=id).total_copies  # Get old total for difference
            book = form.save(commit=False)
            difference = book.total_copies - old_total
            book.available_copies += difference
            book.updated_by = request.user
            book.updated_at = timezone.now()
            book.save()
            return redirect('bookDetails', id=book.id)
    else:
        form = BookForm(instance=book)
    return render(request, 'editBook.html', {'form': form, 'book': book})

@login_required
@user_passes_test(isAdminOrLibrarian)
def deleteBook(request, id):
    try:
        book = Books.objects.get(id=id, isDeleted=False)
        book.isDeleted = True
        book.deleted_by = request.user
        book.deleted_at = timezone.now()
        book.save()
        return redirect('getAllBooks')
    except Books.DoesNotExist:
        return redirect('getAllBooks')
