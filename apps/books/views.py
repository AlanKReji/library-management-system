from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Books
from django.contrib import messages
from apps.users.models import Users
from apps.borrows.models import Borrows
from .forms import BookForm 
from django.core.paginator import Paginator
from django.db.models import Q


def isAdmin(user):
    return user.is_authenticated and user.role == Users.Role.ADMIN

def isLibrarian(user):
    return user.is_authenticated and user.role == Users.Role.LIBRARIAN

def isAdminOrLibrarian(user):
    return isAdmin(user) or isLibrarian(user)

@login_required
def home(request):
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '')
    books = Books.objects.filter(isDeleted=False).order_by('title')
    if search:
        books = books.filter(
            Q(title__icontains=search) | Q(author__icontains=search)
        )
    if category:
        books = books.filter(category__icontains=category)
    books = books.order_by('title')
    paginator = Paginator(books, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    categories = set()
    for cat in Books.objects.values_list('category', flat=True).distinct().exclude(category__isnull=True).exclude(category=''):
        categories.update(cat.split('/'))
    categories = sorted(list(categories))
    return render(request, 'home.html', {'books': page, 'search': search, 'category': category, 'categories': categories})

@login_required
def getAllBooks(request):
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')
    books = Books.objects.filter(isDeleted=False)
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | Q(author__icontains=search_query)
        )
    if category_filter:
        books = books.filter(category__icontains=category_filter)
    books = books.order_by('title')
    paginator = Paginator(books, 10)  # 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Extract unique categories by splitting on '/'
    categories = set()
    for cat in Books.objects.values_list('category', flat=True).distinct().exclude(category__isnull=True).exclude(category=''):
        if cat:
            categories.update(cat.split('/'))
    categories = sorted(list(categories))
    return render(request, 'books.html', {'books': page_obj, 'search_query': search_query, 'category_filter': category_filter, 'categories': categories})

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
