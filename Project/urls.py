from django.urls import path
from Project.views.profile import profile_view
from Project.views.registerviews import register_view, login_view, logout_view, edit_comment, delete_comment
from Project.views.views import index, board_detail, create_board, delete_board, update_board, add_comment, \
    get_task_details, serve_task_file, delete_task_file, delete_column, create_column, update_column, reorder_columns, invite_user, add_task, remove_member, \
    update_member_role, update_task, delete_task, toggle_task, archive_task, update_task_column, \
    add_poll_option, remove_poll_option, vote_poll

urlpatterns = [

    path('main/', index, name='index'),
    path('profile/', profile_view, name='profile'),

    path('update-task-column/', update_task_column, name='update_task_column'),
    path('board/<int:board_id>/', board_detail, name='board_detail'),
    path('board/create/', create_board, name='create_board'),
    path('board/delete/<int:board_id>/', delete_board, name='delete_board'),
    path('board/update/<int:board_id>/', update_board, name='update_board'),
    path('task/<int:task_id>/comment/', add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('task/<int:task_id>/get_details/', get_task_details, name='get_task_details'),
    path('task/file/<int:file_id>/', serve_task_file, name='serve_task_file'),
    path('task/file/<int:file_id>/delete/', delete_task_file, name='delete_task_file'),

    path('board/<int:board_id>/member/<int:member_id>/update_role/', update_member_role, name='update_member_role'),
    path('column/delete/<int:column_id>/', delete_column, name='delete_column'),
    path('board/<int:board_id>/column/create/', create_column, name='create_column'),
    path('column/update/<int:column_id>/', update_column, name='update_column'),
    path('board/<int:board_id>/columns/reorder/', reorder_columns, name='reorder_columns'),
    path('board/<int:board_id>/invite/', invite_user, name='invite_user'),
    path('board/<int:board_id>/member/remove/<int:member_id>/', remove_member, name='remove_member'),
    path('task/add/', add_task, name='add_task'),
    path('task/update/<int:task_id>/', update_task, name='update_task'),
    path('task/delete/<int:task_id>/', delete_task, name='delete_task'),
    path('task/<int:pk>/toggle/', toggle_task, name='toggle_task'),
    path('task/<int:pk>/archive/', archive_task, name='archive_task'),
    path('task/<int:task_id>/poll/option/add/', add_poll_option, name='add_poll_option'),
    path('task/poll/option/<int:option_id>/remove/', remove_poll_option, name='remove_poll_option'),
    path('task/<int:task_id>/poll/vote/', vote_poll, name='vote_poll'),
    path('register/', register_view, name='register'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]