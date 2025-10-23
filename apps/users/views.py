from django.shortcuts import render, redirect
from .models import Users
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegistrationForm, UserLoginForm
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
        users = Users.objects.filter(isDeleted=False, role__in = [Users.Role.LIBRARIAN, Users.Role.USER])
    elif isLibrarian(loggedIn):
        users = Users.objects.filter(isDeleted=False, role=Users.Role.USER )
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
    userView = Users.objects.get(id = id, isDeleted = False)
    return render(request, 'userDetails.html', {'userView': userView})

@login_required
@user_passes_test(isAdminOrLibrarian)
def editUser(request, id):
    editUser = Users.objects.get(id=id, isDeleted=False)
    success = False
    if request.method == 'POST':
        editUser.first_name = request.POST.get('first_name')
        editUser.last_name = request.POST.get('last_name')
        editUser.username = request.POST.get('username')
        editUser.email = request.POST.get('email')
        if isAdmin(request.user):
            editUser.role = request.POST.get('role')
        editUser.updated_by = request.user
        editUser.updated_at = timezone.now()
        editUser.full_clean()
        editUser.save()
        success = True
    # Context for role dropdown
    is_admin = isAdmin(request.user)
    role_choices = [(Users.Role.LIBRARIAN, 'Librarian'), (Users.Role.USER, 'User')]
    can_admin_edit_role = is_admin and editUser.role in [Users.Role.LIBRARIAN, Users.Role.USER]
    return render(request, 'editUser.html', {'editUser': editUser, 'success': success, 'isAdmin': is_admin, 'role_choices': role_choices, 'can_admin_edit_role': can_admin_edit_role})

@login_required
@user_passes_test(isAdmin)
def deleteUser(request, id):
    if request.user.id == id:
        return redirect('getAllUsers')
    try:
        user = Users.objects.get(id = id , isDeleted = False)
        user.isDeleted = True
        user.is_active = False
        user.deleted_by = request.user
        user.deleted_at = timezone.now()
        user.save()
        return redirect('getAllUsers')
    except Users.DoesNotExist:
        return redirect('getAllUsers')
