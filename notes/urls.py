from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.index, name='index'),
    path('folder/create/', views.create_folder, name='create_folder'),
    path('folder/<int:pk>/', views.folder_detail, name='folder_detail'),
    path('folder/<int:pk>/delete/', views.delete_folder, name='delete_folder'),
    path('folder/<int:folder_id>/note/create/', views.create_note, name='create_note'),
    path('note/<int:pk>/', views.view_note, name='view_note'),
    path('note/<int:pk>/edit/', views.edit_note, name='edit_note'),
    path('note/<int:pk>/delete/', views.delete_note, name='delete_note'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('delete-image/', views.delete_image, name='delete_image'),
]
