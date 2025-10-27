from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name = 'home'),
    path("", views.getAllBooks, name = 'getAllBooks'),
    path("add/", views.addBook, name = 'addBook'),
    path("details/<int:id>/", views.bookDetails, name  = 'bookDetails'),
    path("edit/<int:id>/", views.editBook, name = 'editBook'),
    path("delete/<int:id>/", views.deleteBook, name = "deleteBook"),
    path("borrow/<int:id>/", views.borrowRequest, name = "borrowRequest")
]