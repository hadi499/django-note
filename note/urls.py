from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.createNote, name='create'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('delete/<int:pk>/', views.deleteNote, name='delete'),
    path('update/<int:pk>/', views.updateNote, name='update'),
    path('categories/<int:pk>/',
         views.category_view, name='category'),
    path('categories/detai/<int:pk>/',
         views.category_view_detail, name='category-detail'),
    # path('fisika/', views.fisika, name='fisika'),
    # path('matematika/', views.matematika, name='matematika'),
]
