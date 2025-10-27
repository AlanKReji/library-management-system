from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Books
from django.contrib import messages
from apps.users.models import Users
from apps.borrows.models import Borrows
from .forms import BookForm 

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
    approved_borrows = Borrows.objects.filter(book=book, status='APPROVED').exists()
    if approved_borrows:
        messages.error(request, "Cannot edit book with active borrows.")
        return redirect('bookDetails', id=id)
    else:
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
        borrows_exist = Borrows.objects.filter(book=book).exists()
        if borrows_exist:
            messages.error(request, "Cannot delete book with borrow history.")
            return redirect('bookDetails', id=id)
        book.isDeleted = True
        book.deleted_by = request.user
        book.deleted_at = timezone.now()
        book.save()
        return redirect('getAllBooks')
    except Books.DoesNotExist:
        return redirect('getAllBooks')

@login_required
def borrowRequest(request, id):
    book = Books.objects.get(id=id, isDeleted=False)
    if request.user.role == Users.Role.ADMIN:
        messages.error(request, "You are not allowed to borrow books.")
        return redirect('bookDetails', id=id)
    if book.available_copies <= 0:
        messages.error(request, "Book is not available.")
        return redirect('bookDetails', id=id)
    approved_count = Borrows.objects.filter(user=request.user, status='APPROVED').count()
    if approved_count >= 5:
        messages.error(request, "You can have a maximum of 5 books in hand at a time.")
        return redirect('bookDetails', id=id)
    existing = Borrows.objects.filter(user=request.user, book=book, status__in=['PENDING', 'APPROVED']).exists()
    if existing:
        messages.error(request, "You already have a pending or approved request for this book.")
        return redirect('bookDetails', id=id)
    Borrows.objects.create(user=request.user, book=book, status='PENDING')
    messages.success(request, "Borrow request submitted.")
    return redirect('bookDetails', id=id)
