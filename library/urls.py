from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('add/', views.book_add, name='book_add'),
    path('<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('trash/', views.trash_list, name='trash_list'),
    path('<int:pk>/restore/', views.book_restore, name='book_restore'),
    path('<int:pk>/hard-delete/', views.book_hard_delete, name='book_hard_delete'),
]