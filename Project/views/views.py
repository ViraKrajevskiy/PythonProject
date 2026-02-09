from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.query_utils import Q
from django.shortcuts import render, get_object_or_404, redirect
from Project.Models_main.new import Board, Column, Task, BoardMember
from django.contrib import messages
from Project.models import User

def get_user_role(user, board):
    if board.owner == user:
        return 'owner'
    try:
        member = BoardMember.objects.get(board=board, user=user)
        return member.role
    except BoardMember.DoesNotExist:
        return None


@login_required
def index(request):
    # Показываем доски, где юзер владелец ИЛИ где он участник
    boards = Board.objects.filter(
        Q(owner=request.user) | Q(members__user=request.user)
    ).distinct().order_by('-created_at')

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
def remove_member(request, board_id, member_id):
    # Только владелец доски может выгонять людей
    board = get_object_or_404(Board, id=board_id, owner=request.user)
    member = get_object_or_404(BoardMember, id=member_id, board=board)
    member.delete()
    messages.success(request, "Участник удален.")
    return redirect('board_detail', board_id=board.id)

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    role = get_user_role(request.user, board)

    # Если доска приватная и ты не владелец/участник — доступ закрыт
    if not board.is_public and role is None:
        raise PermissionDenied

    columns = board.columns.all().order_by('order')
    return render(request, 'pageobject.html', {
        'board': board,
        'columns': columns,
        'role': role
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


def delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    board.delete()
    return redirect('index')

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
    # 1. Получаем задачу и её контекст (колонку и доску)
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board

    # 2. Проверяем глобальную роль пользователя на этой доске
    role = get_user_role(request.user, board)

    # 3. Если пользователь просто "viewer", запрещаем любые POST изменения
    if role == 'viewer':
        messages.error(request, "У вас нет прав для изменения этой задачи!")
        return redirect('board_detail', board_id=board.id)

    if request.method == 'POST':
        # Логика удаления задачи
        if 'delete' in request.POST:
            task.delete()
            messages.success(request, "Задача удалена")
            return redirect('board_detail', board_id=board.id)

        # Логика архивации задачи
        if 'archive' in request.POST:
            task.is_archived = True
            task.save()
            messages.success(request, "Задача перенесена в архив")
            return redirect('board_detail', board_id=board.id)

        # 4. Сбор данных из формы
        text = request.POST.get('text')
        description = request.POST.get('description')
        label_color = request.POST.get('label_color')
        due_date = request.POST.get('due_date')
        assigned_user_id = request.POST.get('assigned_to')

        # НОВОЕ: Тот самый кастомный тег-роль (например, "Backend", "Lead")
        task_role = request.POST.get('task_role')

        if text:
            task.text = text
            task.description = description

            # Сохраняем кастомный тег роли
            task.task_role = task_role

            # Исправляем цвет (если не выбран, ставим белый)
            task.label_color = label_color if label_color else "#ffffff"

            # Обработка дедлайна
            if due_date:
                task.due_date = due_date
            else:
                task.due_date = None

            # Логика назначения исполнителя
            if assigned_user_id:
                try:
                    # Проверяем, существует ли такой пользователь
                    assigned_user = User.objects.get(id=assigned_user_id)
                    task.assigned_to = assigned_user
                except User.DoesNotExist:
                    task.assigned_to = None
            else:
                # Если в списке выбрано "Не назначен"
                task.assigned_to = None

            task.save()
            messages.success(request, "Задача успешно обновлена")
        else:
            messages.error(request, "Название задачи не может быть пустым!")

    return redirect('board_detail', board_id=board.id)

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    board_id = task.column.board.id
    task.delete()
    return redirect('board_detail', board_id=board_id)

# Изменение названия доски
def update_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            board.title = new_title
            board.save()
    return redirect('board_detail', board_id=board.id)


def toggle_task(request, pk):
    task = get_object_or_404(Task, id=pk)
    role = get_user_role(request.user, task.column.board)

    if role != 'viewer':
        task.is_completed = not task.is_completed
        task.save()
    else:
        messages.error(request, "Вы не можете менять статус задач")

    return redirect('board_detail', board_id=task.column.board.id)


# Создание колонки внутри доски
def create_column(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            # Находим максимальный порядок, чтобы добавить в конец
            last_col = board.columns.order_by('-order').first()
            order = (last_col.order + 1) if last_col else 0
            Column.objects.create(board=board, title=title, order=order)
    return redirect('board_detail', board_id=board.id)


# views.py (правильный вариант)
def archive_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Сохраняем ID доски ДО того, как что-то пойдет не так (на всякий случай)
    board_id = task.column.board.id  # Убедись, что путь к ID доски верный (через колонку)

    task.is_archived = True
    task.save()  # Просто вызываем метод, НЕ присваиваем его переменной task

    # Перенаправляем обратно на страницу доски
    return redirect('board_detail', board_id=board_id)


@login_required
def board_page(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    role = get_user_role(request.user, board)

    # Если доска приватная и юзер не участник и не владелец
    if not board.is_public and role is None:
        raise PermissionDenied # Выкинет ошибку 403

    # Передаем роль в шаблон, чтобы скрыть/показать кнопки
    return render(request, 'pageobject.html', {
        'board': board,
        'role': role
    })
# Изменение названия колонки (списка)
def update_column(request, column_id):
    column = get_object_or_404(Column, id=column_id)
    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            column.title = new_title
            column.save()
    return redirect('board_detail', board_id=column.board.id)