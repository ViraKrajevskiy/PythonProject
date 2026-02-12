from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404
from Project.Forms.register import RegisterForm

from django.urls import reverse

from Project.Models_main.new import Comment

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related('task__column__board', 'author'),
        id=comment_id
    )
    if comment.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()

    return redirect(f"{reverse('board_detail', args=[comment.task.column.board.id])}?open_task={comment.task.id}")

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related('task__column__board', 'author', 'task__column__board__owner'),
        id=comment_id
    )
    board = comment.task.column.board

    if comment.author == request.user or board.owner == request.user:
        comment.delete()
    else:
        raise PermissionDenied

    return redirect(f"{reverse('board_detail', args=[board.id])}?open_task={comment.task.id}")

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя
            user = form.save()
            # АВТОМАТИЧЕСКИЙ ЛОГИН: чтобы юзеру не пришлось вводить пароль снова
            login(request, user)
            # ПЕРЕАДРЕСАЦИЯ: отправляем на страницу с досками
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # форма сама проверила пароль и нашла юзера
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')