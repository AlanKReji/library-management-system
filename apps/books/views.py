from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Books
from apps.users.models import Users

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
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn') or None
        category = request.POST.get('category')
        publisher = request.POST.get('publisher')
        published_at = request.POST.get('published_at') or None
        total_copies = int(request.POST.get('total_copies', 0))

        book = Books(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            publisher=publisher,
            published_at=published_at,
            total_copies=total_copies,
            available_copies=total_copies,
            created_by = request.user
        )

        book.full_clean()
        book.save()
        return render(request, 'addBook.html', {'book': book})
    return render(request, 'addBook.html')

@login_required
def bookDetails(request, id):
    book = Books.objects.get(id = id, isDeleted = False)
    return render(request, 'bookDetails.html', {'book': book})

@login_required
@user_passes_test(isAdminOrLibrarian)
def editBook(request, id):
    book = Books.objects.get(id=id, isDeleted=False)
    success = False
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn') or None
        book.category = request.POST.get('category')
        book.publisher = request.POST.get('publisher')
        book.published_at = request.POST.get('published_at') or None
        total_copies = int(request.POST.get('total_copies', book.total_copies))
        difference = total_copies - book.total_copies
        book.total_copies = total_copies
        book.available_copies += difference
        book.updated_by = request.user
        book.updated_at = timezone.now()
        book.full_clean()
        book.save()

        success = True
    return render(request, 'editBook.html', {'book': book, 'success': success })

@login_required
@user_passes_test(isAdminOrLibrarian)
def deleteBook(request, id):
    try:
        book = Books.objects.get(id = id , isDeleted = False)        
        book.isDeleted = True
        book.deleted_by = request.user 
        book.deleted_at = timezone.now()
        book.save() 
        return redirect('getAllBooks')
    except Books.DoesNotExist:
        return redirect('getAllBooks')