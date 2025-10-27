from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Users
from apps.borrows.models import Borrows
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegistrationForm, UserLoginForm, UserEditForm  # Added UserEditForm
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def isAdmin(user):
    return user.is_authenticated and user.role == Users.Role.ADMIN

def isLibrarian(user):
    return user.is_authenticated and user.role == Users.Role.LIBRARIAN

def isAdminOrLibrarian(user):
    return isAdmin(user) or isLibrarian(user)

@login_required
@user_passes_test(isAdminOrLibrarian)
def getAllUsers(request):
    loggedIn = request.user
    if isAdmin(loggedIn):
        users = Users.objects.filter(isDeleted=False, role__in=[Users.Role.LIBRARIAN, Users.Role.USER])
    elif isLibrarian(loggedIn):
        users = Users.objects.filter(isDeleted=False, role=Users.Role.USER)
    users = users | Users.objects.filter(pk=loggedIn.pk)
    users = users.distinct().order_by('username')
    return render(request, 'users.html', {'users': users})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def loginView(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def logoutView(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(isAdminOrLibrarian)
def userDetails(request, id):
    userView = Users.objects.get(id=id, isDeleted=False)
    return render(request, 'userDetails.html', {'userView': userView})

@login_required
@user_passes_test(isAdminOrLibrarian)
def editUser(request, id):
    editUser = Users.objects.get(id=id, isDeleted=False)
    active_borrows = Borrows.objects.filter(user=editUser, status='APPROVED').exists()
    if active_borrows:
        messages.error(request, "Cannot edit user with active borrows.")
        return redirect('userDetails', id=id)
    if request.user.role == Users.Role.ADMIN:
        if editUser.role not in [Users.Role.LIBRARIAN, Users.Role.USER] and editUser.id != request.user.id:
            return redirect('getAllUsers')  # Can't edit other admins, but can edit self
    elif request.user.role == Users.Role.LIBRARIAN:
        if editUser.role != Users.Role.USER and editUser.id != request.user.id:
            return redirect('getAllUsers')  # Can't edit non-users
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=editUser, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.updated_by = request.user
            user.updated_at = timezone.now()
            user.save()
            return redirect('userDetails', id=user.id)
    else:
        form = UserEditForm(instance=editUser, user=request.user)
    # Context for role dropdown
    is_admin = isAdmin(request.user)
    role_choices = [(Users.Role.LIBRARIAN, 'Librarian'), (Users.Role.USER, 'User')]
    can_admin_edit_role = is_admin and editUser.role in [Users.Role.LIBRARIAN, Users.Role.USER] and editUser.id != request.user.id  # Can't edit own role
    return render(request, 'editUser.html', {'form': form, 'editUser': editUser, 'isAdmin': is_admin, 'role_choices': role_choices, 'can_admin_edit_role': can_admin_edit_role})

@login_required
@user_passes_test(isAdmin)
def deleteUser(request, id):
    if request.user.id == id:
        return redirect('getAllUsers')
    user = Users.objects.get(id=id, isDeleted=False)
    active_borrows = Borrows.objects.filter(user=user, status='APPROVED').exists()
    if active_borrows:
        messages.error(request, "Cannot edit user with active borrows.")
        return redirect('userDetails', id=id)
    try:
        user.isDeleted = True
        user.is_active = False
        user.deleted_by = request.user
        user.deleted_at = timezone.now()
        user.save()
        return redirect('getAllUsers')
    except Users.DoesNotExist:
        return redirect('getAllUsers')
