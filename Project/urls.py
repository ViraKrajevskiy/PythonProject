from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('board/create/', views.create_board, name='create_board'),
    path('board/delete/<int:board_id>/', views.delete_board, name='delete_board'),
    path('board/update/<int:board_id>/', views.update_board, name='update_board'),
    path('board/<int:board_id>/column/create/', views.create_column, name='create_column'),
    path('task/add/', views.add_task, name='add_task'),
    path('task/update/<int:task_id>/', views.update_task, name='update_task'),
    path('task/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('task/<int:pk>/toggle/', views.toggle_task, name='toggle_task'),
    path('column/update/<int:column_id>/', views.update_column, name='update_column'),
    path('task/<int:pk>/archive/', views.archive_task, name='archive_task'),
]