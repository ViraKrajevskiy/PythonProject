/**
 * Online Trello - Final JS Controller
 * Управление доской, задачами, комментариями, перемещением карточек и динамической загрузкой
 */

// 1. ОТКРЫТИЕ МОДАЛКИ ЗАДАЧИ ЧЕРЕЗ AJAX
function openTaskModal(taskId) {
    const contentDiv = document.getElementById('taskModalContent');
    const modalEl = document.getElementById('universalTaskModal');

    if (!contentDiv || !modalEl) return;

    // Показываем спиннер перед загрузкой
    contentDiv.innerHTML = `
        <div class="p-5 text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Загрузка данных карточки...</p>
        </div>
    `;

    // Инициализация модалки Bootstrap
    let modalInstance = bootstrap.Modal.getInstance(modalEl);
    if (!modalInstance) {
        modalInstance = new bootstrap.Modal(modalEl);
    }
    modalInstance.show();

    // Запрос HTML-контента задачи
    fetch(`/task/${taskId}/get_details/`)
        .then(response => {
            if (!response.ok) throw new Error('Ошибка сети');
            return response.text();
        })
        .then(html => {
            contentDiv.innerHTML = html;

            // Автоматический скролл комментариев вниз
            const scrollList = contentDiv.querySelector('.comments-list-scroll');
            if (scrollList) {
                scrollList.scrollTop = scrollList.scrollHeight;
            }

            // Обновляем URL
            const url = new URL(window.location);
            url.searchParams.set('open_task', taskId);
            window.history.pushState({}, '', url);
        })
        .catch(err => {
            console.error('Fetch Error:', err);
            contentDiv.innerHTML = `
                <div class="p-5 text-center text-danger">
                    <h5>Ошибка загрузки</h5>
                    <p>Не удалось получить данные задачи.</p>
                </div>
            `;
        });
}

// 2. УПРАВЛЕНИЕ РЕДАКТИРОВАНИЕМ КОММЕНТАРИЕВ
function toggleEditComment(id) {
    const textDiv = document.getElementById('comment-text-' + id);
    const editDiv = document.getElementById('edit-box-' + id);

    if (textDiv && editDiv) {
        if (editDiv.classList.contains('d-none')) {
            editDiv.classList.remove('d-none');
            textDiv.classList.add('d-none');

            const area = editDiv.querySelector('textarea');
            if (area) {
                area.focus();
                const val = area.value;
                area.value = '';
                area.value = val;
            }
        } else {
            editDiv.classList.add('d-none');
            textDiv.classList.remove('d-none');
        }
    }
}

// 3. ОТПРАВКА ОТРЕДАКТИРОВАННОГО КОММЕНТАРИЯ
function submitEditComment(id) {
    const textarea = document.getElementById('edit-textarea-' + id);
    const hiddenInput = document.getElementById('hidden-edit-input-' + id);
    const form = document.getElementById('editCommentForm' + id);

    if (form && textarea && hiddenInput) {
        const content = textarea.value.trim();
        if (content === "") return;

        hiddenInput.value = content;

        // Блокировка кнопки (ищем внутри edit-box)
        const editBox = document.getElementById('edit-box-' + id);
        const btn = editBox.querySelector('button.btn-success');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '...';
        }

        form.submit();
    }
}

// 4. ФУНКЦИЯ СОХРАНЕНИЯ ПЕРЕМЕЩЕНИЯ КАРТОЧКИ (AJAX)
function saveTaskMovement(taskId, columnId) {
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('column_id', columnId);

    // Получаем CSRF токен из любой формы на странице
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/update-task-column/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status !== 'success') {
            console.error('Ошибка сохранения:', data.message);
            // Если на сервере произошла ошибка, лучше перезагрузить страницу
            // location.reload();
        }
    })
    .catch(err => {
        console.error('Сетевая ошибка при перемещении:', err);
    });
}

// 5. ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ
document.addEventListener('DOMContentLoaded', () => {

    // 5.1. Подключение Drag-and-Drop (SortableJS)
    const taskContainers = document.querySelectorAll('.task-container');

    taskContainers.forEach(container => {
        new Sortable(container, {
            group: 'shared_tasks', // Позволяет перемещать между всеми колонками
            animation: 150,
            ghostClass: 'task-ghost',   // Класс для пустого места (добавь в CSS)
            chosenClass: 'task-chosen', // Класс при захвате (добавь в CSS)
            dragClass: 'task-drag',
            fallbackOnBody: true,
            swapThreshold: 0.65,

            // Срабатывает при завершении перетаскивания
            onEnd: function (evt) {
                const taskId = evt.item.getAttribute('data-task-id');
                const newColumnId = evt.to.getAttribute('data-column-id');

                // Отправляем на сервер только если колонка изменилась
                if (evt.from !== evt.to) {
                    saveTaskMovement(taskId, newColumnId);
                }
            }
        });
    });

    // 5.2. Установка цветов меток для задач
    document.querySelectorAll('.task-item[data-label-color]').forEach(taskItem => {
        const color = taskItem.getAttribute('data-label-color');
        if (color) {
            taskItem.style.borderLeft = `5px solid ${color} !important`;
        }
    });

    // 5.3. Проверка URL на наличие ID задачи
    const urlParams = new URLSearchParams(window.location.search);
    const openTaskId = urlParams.get('open_task');
    if (openTaskId) {
        openTaskModal(openTaskId);
    }

    // 5.4. Очистка URL при закрытии модалки
    const modalEl = document.getElementById('universalTaskModal');
    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', () => {
            const url = new URL(window.location);
            url.searchParams.delete('open_task');
            window.history.replaceState({}, '', url);
        });
    }

    // 5.5. Обработка горячих клавиш (Ctrl + Enter)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const active = document.activeElement;
            if (active && active.tagName === 'TEXTAREA') {
                if (active.id.startsWith('edit-textarea-')) {
                    const id = active.id.split('-').pop();
                    submitEditComment(id);
                } else {
                    const form = active.closest('form');
                    if (form) form.submit();
                }
            }
        }
    });
});