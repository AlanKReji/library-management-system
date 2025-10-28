from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from apps.books.models import Books
from apps.users.models import Users
from .models import Borrows
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.
def isAdmin(user):
    return user.is_authenticated and user.role == Users.Role.ADMIN

def isLibrarian(user):
    return user.is_authenticated and user.role == Users.Role.LIBRARIAN

def isAdminOrLibrarian(user):
    return isAdmin(user) or isLibrarian(user)

@login_required
def getMyBorrowHistory(request):
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    myBorrows = Borrows.objects.filter(user=request.user)

    if search:
        myBorrows = myBorrows.filter(
            Q(book__title__icontains=search) | Q(book__author__icontains=search)
        )

    if status:
        myBorrows = myBorrows.filter(status=status)

    myBorrows = myBorrows.order_by('-borrow_date')
    paginator = Paginator(myBorrows, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    status_choices = Borrows.STATUS_CHOICES
    return render(request, 'myBorrowHistory.html', {
        'myBorrows': page,
        'search_query': search,
        'status_filter': status,
        'status_choices': status_choices
    })

@login_required
@user_passes_test(isAdminOrLibrarian)
def getAllBorrowHistory(request):
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    if isAdmin(request.user):
        allBorrows = Borrows.objects.filter(user__role__in=[Users.Role.LIBRARIAN, Users.Role.USER])
    elif isLibrarian(request.user):
        allBorrows = Borrows.objects.filter(user__role__in=Users.Role.USER)
    if search:
        allBorrows = allBorrows.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(book__title__icontains=search) |
            Q(book__author__icontains=search)
        )

    if status:
        allBorrows = allBorrows.filter(status=status)
    allBorrows = allBorrows.order_by('-borrow_date')
    paginator = Paginator(allBorrows, 5)  
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    status_choices = Borrows.STATUS_CHOICES
    return render(request, 'allBorrowHistory.html', {
        'allBorrows': page,
        'search_query': search,
        'status_filter': status,
        'status_choices': status_choices
    })

@login_required
@user_passes_test(isAdminOrLibrarian)
def approveBorrow(request, borrow_id):
    borrow = Borrows.objects.get( id=borrow_id, status='PENDING')
    if isLibrarian(request.user) and borrow.user == request.user:
        messages.error(request, "You cannot approve your own borrow request.")
        return redirect('getAllBorrowHistory')
    approved_count = Borrows.objects.filter(user=borrow.user, status='APPROVED').count()
    if approved_count >= 5:
        messages.error(request, "User already has 5 books in hand. Cannot approve.")
        return redirect('getAllBorrowHistory')
    borrow.status = 'APPROVED'
    borrow.book.available_copies -= 1
    borrow.book.save()
    borrow.save()
    messages.success(request, "Borrow request approved.")
    return redirect('getAllBorrowHistory')

@login_required
@user_passes_test(isAdminOrLibrarian)
def rejectBorrow(request, borrow_id):
    borrow = Borrows.objects.get( id=borrow_id, status='PENDING')
    if isLibrarian(request.user) and borrow.user == request.user:
        messages.error(request, "You cannot reject your own borrow request.")
        return redirect('getAllBorrowHistory')
    borrow.status = 'REJECTED'
    borrow.save()
    messages.success(request, "Borrow request rejected.")
    return redirect('getAllBorrowHistory')

@login_required
def returnBook(request, borrow_id):
    borrow = Borrows.objects.get( id=borrow_id,  user=request.user, status='APPROVED')
    borrow.return_date = timezone.now()
    borrow.calculate_fine()
    borrow.status = 'RETURNED'
    borrow.book.available_copies += 1
    borrow.book.save()
    borrow.save()
    messages.success(request, f"Book returned. Fine: ₹{borrow.fine_amount}")
    return redirect('getMyBorrowHistory')    