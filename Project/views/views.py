from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse

from Project.Models_main.new import Board, Column, Task, BoardMember, Comment, TaskFile
from django.contrib import messages
from Project.models import User
from django.http import JsonResponse


@login_required
def update_task_column(request):
    """
    Обработчик AJAX для перемещения задачи между колонками (Drag-and-Drop)
    """
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        column_id = request.POST.get('column_id')

        # Получаем задачу и колонку
        task = get_object_or_404(Task, id=task_id)
        new_column = get_object_or_404(Column, id=column_id)

        # Проверка прав доступа: может ли пользователь менять что-то на этой доске
        role = get_user_role(request.user, new_column.board)

        if role == 'viewer' or role is None:
            return JsonResponse({
                'status': 'error',
                'message': 'У вас нет прав для перемещения задач'
            }, status=403)

        # Меняем колонку и сохраняем
        task.column = new_column
        task.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def get_user_role(user, board):
    if board.owner == user:
        return 'owner'
    try:
        member = BoardMember.objects.select_related('user').get(board=board, user=user)
        return member.role
    except BoardMember.DoesNotExist:
        return None


@login_required
def get_task_details(request, task_id):
    task = get_object_or_404(
        Task.objects.select_related('column__board', 'assigned_to').prefetch_related('files', 'comments__author'),
        id=task_id
    )
    board = task.column.board
    role = get_user_role(request.user, board)

    members_ids = BoardMember.objects.filter(board=board).values_list('user_id', flat=True)
    all_assignable_users = User.objects.filter(
        Q(id__in=members_ids) | Q(id=board.owner.id)
    ).distinct()

    return render(request, 'task_detail_content.html', {
        'task': task,
        'role': role,
        'all_users': all_assignable_users,
        'board': board
    })


@login_required
def update_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    role = get_user_role(request.user, board)

    if role not in ['owner', 'admin']:
        raise PermissionDenied

    if request.method == 'POST':
        title = request.POST.get('title')
        # Обрабатываем и заголовок, и переключатель комментов в одной функции
        enable_comments = request.POST.get('enable_comments') == 'on'

        if title:
            board.title = title
            board.enable_comments = enable_comments
            board.save()
            messages.success(request, "Настройки обновлены.")

    return redirect('board_detail', board_id=board.id)


@login_required
def index(request):
    boards = Board.objects.filter(
        Q(owner=request.user) | Q(members__user=request.user)
    ).select_related('owner').prefetch_related('members__user').distinct().order_by('-created_at')
    return render(request, 'main_page.html', {'boards': boards})


@login_required
def invite_user(request, board_id):
    board = get_object_or_404(Board, id=board_id, owner=request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'viewer')
        try:
            user_to_invite = User.objects.get(username=username)
            if user_to_invite != request.user:
                BoardMember.objects.update_or_create(
                    board=board,
                    user=user_to_invite,
                    defaults={'role': role}
                )
                messages.success(request, f"Пользователь {username} добавлен.")
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
    return redirect('board_detail', board_id=board.id)


@login_required
def update_member_role(request, board_id, member_id):
    # Только владелец доски может менять роли
    board = get_object_or_404(Board, id=board_id, owner=request.user)
    member = get_object_or_404(BoardMember, id=member_id, board=board)

    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['viewer', 'editor', 'admin']:
            member.role = new_role
            member.save()
            messages.success(request, f"Роль пользователя {member.user.username} изменена на {new_role}.")
        else:
            messages.error(request, "Некорректная роль.")

    return redirect('board_detail', board_id=board.id)


@login_required
def remove_member(request, board_id, member_id):
    # Только владелец доски может выгонять людей
    board = get_object_or_404(Board, id=board_id, owner=request.user)
    member = get_object_or_404(BoardMember, id=member_id, board=board)
    member.delete()
    messages.success(request, "Участник удален.")
    return redirect('board_detail', board_id=board.id)


@login_required
def board_detail(request, board_id):
    board = get_object_or_404(
        Board.objects.select_related('owner').prefetch_related('members__user'),
        id=board_id
    )
    role = get_user_role(request.user, board)

    if not board.is_public and role is None:
        raise PermissionDenied

    # Список всех участников для выбора ответственного (участники + владелец)
    members_ids = BoardMember.objects.filter(board=board).values_list('user_id', flat=True)
    all_assignable_users = User.objects.filter(
        Q(id__in=members_ids) | Q(id=board.owner.id)
    ).distinct()

    system_roles = User.ROLE_CHOICES
    columns = board.columns.prefetch_related(
        'tasks__assigned_to',
        'tasks__files'
    ).all().order_by('order')

    return render(request, 'pageobject.html', {
        'board': board,
        'columns': columns,
        'role': role,
        'all_users': all_assignable_users,
        'system_roles': system_roles
    })


@login_required
def create_board(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        # Проверяем галочку: если она нажата, придет 'on', если нет — None
        is_public_val = request.POST.get('is_public') == 'on'

        # Создаем доску и сразу привязываем владельца и статус публичности
        Board.objects.create(
            title=title,
            owner=request.user,
            is_public=is_public_val
        )
        return redirect('index')  # или как там у тебя называется главная


@login_required
def delete_column(request, column_id):
    # Находим колонку
    column = get_object_or_404(Column, id=column_id)
    board = column.board

    # Проверяем роль
    role = get_user_role(request.user, board)

    # Разрешаем удаление только тем, кто не "viewer"
    if role and role != 'viewer':
        column.delete()
        messages.success(request, f"Колонка '{column.title}' удалена.")
    else:
        messages.error(request, "У вас нет прав для удаления этой колонки.")

    return redirect('board_detail', board_id=board.id)


# Изменение названия доски
@login_required
def update_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    role = get_user_role(request.user, board)

    # Запрещаем всем, кто не владелец (или не админ доски)
    if role not in ['owner', 'admin']:
        messages.error(request, "Только владелец может менять настройки доски")
        return redirect('board_detail', board_id=board.id)

    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            board.title = new_title
            board.save()
    return redirect('board_detail', board_id=board.id)


# Удаление доски
@login_required
def delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    # Удалять может только хозяин
    if board.owner != request.user:
        messages.error(request, "Удалить доску может только её создатель")
        return redirect('index')

    board.delete()
    return redirect('index')


# Изменение названия колонки
@login_required
def update_column(request, column_id):
    column = get_object_or_404(Column, id=column_id)
    role = get_user_role(request.user, column.board)

    if role == 'viewer' or role is None:
        messages.error(request, "Нет прав для редактирования списков")
        return redirect('board_detail', board_id=column.board.id)

    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            column.title = new_title
            column.save()
    return redirect('board_detail', board_id=column.board.id)


# --- ЛОГИКА ЗАДАЧ ---

def add_task(request):
    if request.method == 'POST':
        column_id = request.POST.get('column_id')
        text = request.POST.get('text')
        column = get_object_or_404(Column, id=column_id)
        if text:
            Task.objects.create(column=column, text=text)
        return redirect('board_detail', board_id=column.board.id)
    return redirect('index')


@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board
    role = get_user_role(request.user, board)

    if role == 'viewer':
        messages.error(request, "У вас нет прав для редактирования этой задачи!")
        return redirect('board_detail', board_id=board.id)

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Удаление задачи
        if action == 'delete':
            task.delete()
            messages.success(request, "Задача удалена")
            return redirect('board_detail', board_id=board.id)

        # 2. Архивация задачи
        if action == 'archive':
            task.is_archived = True
            task.save()
            messages.success(request, "Задача перенесена в архив")
            return redirect('board_detail', board_id=board.id)

        # 3. Сохранение основных данных
        task.text = request.POST.get('text')
        task.description = request.POST.get('description')
        task.task_role = request.POST.get('task_role')

        # Сохраняем цвет метки
        task.label_color = request.POST.get('label_color', '#ffffff')

        # Сохраняем дедлайн (проверяем, не пустое ли поле)
        due_date = request.POST.get('due_date')
        if due_date:
            task.due_date = due_date
        else:
            task.due_date = None

        # Привязка ответственного
        assigned_id = request.POST.get('assigned_to')
        if assigned_id:
            task.assigned_to = User.objects.filter(id=assigned_id).first()
        else:
            task.assigned_to = None

        # 4. Логика вложений (файлов)
        # Если в форме поле называется 'attachment' (как в моем прошлом HTML)
        if 'attachment' in request.FILES:
            file = request.FILES['attachment']
            TaskFile.objects.create(task=task, file=file, original_name=file.name)

        # Если ты используешь множественную загрузку 'task_files'
        if 'task_files' in request.FILES:
            files = request.FILES.getlist('task_files')
            for f in files:
                TaskFile.objects.create(task=task, file=f, original_name=f.name)

        task.save()
        messages.success(request, "Изменения сохранены")

        # Возвращаемся на доску и открываем ту же задачу
        return redirect(f"{reverse('board_detail', args=[board.id])}?open_task={task.id}")

    return redirect('board_detail', board_id=board.id)


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board_id = task.column.board.id
    task.delete()
    return redirect('board_detail', board_id=board_id)


def toggle_task(request, pk):
    task = get_object_or_404(Task, id=pk)
    role = get_user_role(request.user, task.column.board)

    if role != 'viewer':
        task.is_completed = not task.is_completed
        task.save()
    else:
        messages.error(request, "Вы не можете менять статус задач")

    return redirect('board_detail', board_id=task.column.board.id)


@login_required
def create_column(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    # ПРОВЕРКА ПРАВ
    role = get_user_role(request.user, board)
    if role == 'viewer' or role is None:
        messages.error(request, "Только редакторы и владельцы могут создавать списки")
        return redirect('board_detail', board_id=board.id)

    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            last_col = board.columns.order_by('-order').first()
            order = (last_col.order + 1) if last_col else 0
            Column.objects.create(board=board, title=title, order=order)
    return redirect('board_detail', board_id=board.id)


@login_required
def archive_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    role = get_user_role(request.user, task.column.board)

    if role == 'viewer' or role is None:
        messages.error(request, "Вы не можете архивировать задачи")
        return redirect('board_detail', board_id=task.column.board.id)

    task.is_archived = True
    task.save()
    return redirect('board_detail', board_id=task.column.board.id)


@login_required
def board_page(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    role = get_user_role(request.user, board)

    # Если доска приватная и юзер не участник и не владелец
    if not board.is_public and role is None:
        raise PermissionDenied  # Выкинет ошибку 403

    # Передаем роль в шаблон, чтобы скрыть/показать кнопки
    return render(request, 'pageobject.html', {
        'board': board,
        'role': role
    })


@login_required
def add_task(request):
    if request.method == 'POST':
        column_id = request.POST.get('column_id')
        text = request.POST.get('text')
        column = get_object_or_404(Column, id=column_id)

        # ПРОВЕРКА ПРАВ
        role = get_user_role(request.user, column.board)
        if role == 'viewer' or role is None:
            messages.error(request, "У вас нет прав для добавления задач")
            return redirect('board_detail', board_id=column.board.id)

        if text:
            Task.objects.create(column=column, text=text)
        return redirect('board_detail', board_id=column.board.id)
    return redirect('index')


@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board

    if not board.enable_comments:
        messages.error(request, "Комментарии отключены.")
        return redirect('board_detail', board_id=board.id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(task=task, author=request.user, content=content)
        else:
            messages.warning(request, "Нельзя отправить пустой комментарий.")

    # Добавляем ?open_task, чтобы модалка не закрылась
    return redirect(f"{reverse('board_detail', args=[board.id])}?open_task={task.id}")
