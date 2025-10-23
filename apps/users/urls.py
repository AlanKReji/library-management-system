from django.urls import path
from . import views
urlpatterns = [
    path("", views.getAllUsers, name = 'getAllUsers'),
    path("register/", views.register, name = 'register'),
    path("login/", views.loginView, name = 'login'),
    path("logout/", views.logoutView, name = 'logout'),
    path("details/<int:id>/", views.userDetails, name = 'userDetails'),
    path("edit/<int:id>/", views.editUser, name = 'editUser'),
    path("delete/<int:id>", views.deleteUser, name = 'deleteUser')
]
