from django.urls import path
from . import views

urlpatterns = [
    path("all-history/", views.getAllBorrowHistory, name = 'getAllBorrowHistory'),
    path("my-history/", views.getMyBorrowHistory, name = 'getMyBorrowHistory'),
]