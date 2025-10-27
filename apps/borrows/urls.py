from django.urls import path
from . import views

urlpatterns = [
    path("all-history/", views.getAllBorrowHistory, name = 'getAllBorrowHistory'),
    path("my-history/", views.getMyBorrowHistory, name = 'getMyBorrowHistory'),
    path("approve/<int:borrow_id>/", views.approveBorrow, name='approveBorrow'),
    path("reject/<int:borrow_id>/", views.rejectBorrow, name='rejectBorrow'),
    path("return/<int:borrow_id>/", views.returnBook, name='returnBook'),
]