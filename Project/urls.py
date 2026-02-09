from django.urls import path
# Убедись, что импорты правильные
from Project.views.profile import profile_view
from Project.views.registerviews import register_view, login_view, logout_view
from Project.views.views import (
    index, board_detail, create_board, delete_board, update_board,
    create_column, add_task, update_task, delete_task, toggle_task,
    update_column, archive_task, invite_user, remove_member, delete_column
)

urlpatterns = [
    # Главная и профиль
    path('main/', index, name='index'),
    path('profile/', profile_view, name='profile'),

    # Доски (Board)
    path('board/<int:board_id>/', board_detail, name='board_detail'), # Это наша главная вьюха доски
    path('board/create/', create_board, name='create_board'),
    path('board/delete/<int:board_id>/', delete_board, name='delete_board'),
    path('board/update/<int:board_id>/', update_board, name='update_board'),


    # Колонки
    path('column/delete/<int:column_id>/', delete_column, name='delete_column'),
    path('board/<int:board_id>/column/create/', create_column, name='create_column'),
    path('column/update/<int:column_id>/', update_column, name='update_column'),
    path('board/<int:board_id>/invite/', invite_user, name='invite_user'),
    path('board/<int:board_id>/member/remove/<int:member_id>/', remove_member, name='remove_member'),
    path('task/add/', add_task, name='add_task'),
    path('task/update/<int:task_id>/', update_task, name='update_task'),
    path('task/delete/<int:task_id>/', delete_task, name='delete_task'),
    path('task/<int:pk>/toggle/', toggle_task, name='toggle_task'),
    path('task/<int:pk>/archive/', archive_task, name='archive_task'),
    path('register/', register_view, name='register'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]