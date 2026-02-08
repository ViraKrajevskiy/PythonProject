from django.shortcuts import render, get_object_or_404, redirect
from Project.models import Board, Column, Task

# Главная со списком всех досок
def index(request):
    boards = Board.objects.all()
    return render(request, 'main_page.html', {'boards': boards})

# Страница конкретной доски
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    columns = board.columns.all().order_by('order')
    return render(request, 'pageobject.html', {'board': board, 'columns': columns})



def create_board(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Board.objects.create(title=title)
    return redirect('index')

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


def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        # Если нажата кнопка "Удалить" внутри модалки (через formaction)
        if 'delete' in request.POST:
            return delete_task(request, task_id)

        task.text = request.POST.get('text')
        task.description = request.POST.get('description')
        task.label_color = request.POST.get('label_color')

        due_date = request.POST.get('due_date')
        if due_date:
            task.due_date = due_date
        else:
            task.due_date = None

        task.save()
    return redirect('board_detail', board_id=task.column.board.id)

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
    task.is_completed = not task.is_completed  # Меняем на противоположное
    task.save()
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

# Изменение названия колонки (списка)
def update_column(request, column_id):
    column = get_object_or_404(Column, id=column_id)
    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            column.title = new_title
            column.save()
    return redirect('board_detail', board_id=column.board.id)