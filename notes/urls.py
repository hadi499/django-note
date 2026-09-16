from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.index, name='index'),
    path('note/create/', views.create_note, name='create_note'),
    path('note/<int:pk>/', views.view_note, name='view_note'),
    path('note/<int:pk>/edit/', views.edit_note, name='edit_note'),
    path('note/<int:pk>/delete/', views.delete_note, name='delete_note'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('delete-image/', views.delete_image, name='delete_image'),
]
