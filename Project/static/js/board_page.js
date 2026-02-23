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

            // Превью выбранных файлов перед отправкой
            initTaskFilePreview(contentDiv);

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

// Превью выбранных файлов в форме задачи
function initTaskFilePreview(container) {
    if (!container) return;
    const input = container.querySelector('#taskFileInput');
    const previewArea = container.querySelector('#filePreviewArea');
    if (!input || !previewArea) return;
    input.addEventListener('change', function () {
        previewArea.innerHTML = '';
        const files = Array.from(this.files || []);
        files.forEach(function (file) {
            const wrap = document.createElement('div');
            wrap.className = 'border rounded p-1 bg-white';
            if (file.type.indexOf('image/') === 0) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.alt = file.name;
                img.style.maxWidth = '80px';
                img.style.maxHeight = '60px';
                img.style.objectFit = 'cover';
                img.className = 'rounded';
                wrap.appendChild(img);
            } else {
                const span = document.createElement('span');
                span.className = 'small text-muted';
                span.textContent = '📎 ' + file.name;
                wrap.appendChild(span);
            }
            previewArea.appendChild(wrap);
        });
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
    if (typeof Sortable === 'undefined') return;

    // 5.0. Перетаскивание колонок (только за шапку колонки)
    const boardCanvas = document.getElementById('boardCanvas');
    if (boardCanvas) {
        const boardId = boardCanvas.getAttribute('data-board-id');
        new Sortable(boardCanvas, {
            draggable: '.column-wrapper',
            handle: '.column-card .card-header',
            group: 'columns',
            animation: 150,
            ghostClass: 'column-ghost',
            chosenClass: 'column-chosen',
            onEnd: function () {
                if (!boardId) return;
                const wrappers = boardCanvas.querySelectorAll('.column-wrapper');
                const columnIds = Array.from(wrappers).map(w => w.getAttribute('data-column-id')).filter(Boolean);
                if (columnIds.length === 0) return;
                const formData = new FormData();
                columnIds.forEach(id => formData.append('column_ids[]', id));
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfToken) formData.append('csrfmiddlewaretoken', csrfToken.value);
                fetch(`/board/${boardId}/columns/reorder/`, {
                    method: 'POST',
                    headers: csrfToken ? { 'X-CSRFToken': csrfToken.value } : {},
                    body: formData
                }).then(r => r.json()).catch(() => {});
            }
        });
    }

    // 5.1. Подключение Drag-and-Drop карточек (SortableJS)
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

    // 5.6. Опрос: добавление варианта, голос, удаление (без вложенных форм)
    document.addEventListener('click', (e) => {
        const addBtn = e.target.closest('.poll-add-option-btn');
        if (addBtn) {
            const block = addBtn.closest('[data-poll-add-url]');
            const input = block?.querySelector('.poll-new-option-input');
            const text = input?.value?.trim();
            if (!text) return;
            const url = block.getAttribute('data-poll-add-url');
            const csrf = block.getAttribute('data-poll-add-csrf');
            const fd = new FormData();
            fd.append('csrfmiddlewaretoken', csrf);
            fd.append('text', text);
            fetch(url, { method: 'POST', body: fd, redirect: 'follow' })
                .then(r => { if (r.redirected) location.assign(r.url); });
            return;
        }
        const removeBtn = e.target.closest('.poll-remove-option-btn');
        if (removeBtn && confirm('Удалить вариант?')) {
            const row = removeBtn.closest('[data-remove-url]');
            const url = row.getAttribute('data-remove-url');
            const csrf = row.getAttribute('data-csrf');
            const fd = new FormData();
            fd.append('csrfmiddlewaretoken', csrf);
            fetch(url, { method: 'POST', body: fd, redirect: 'follow' })
                .then(r => { if (r.redirected) location.assign(r.url); });
        }
    });
    function submitPollVote(row) {
        const url = row.getAttribute('data-vote-url');
        const optionId = row.getAttribute('data-option-id');
        const csrf = row.getAttribute('data-csrf');
        if (!url || !optionId || !csrf) return;
        const fd = new FormData();
        fd.append('csrfmiddlewaretoken', csrf);
        fd.append('option_id', optionId);
        fetch(url, { method: 'POST', body: fd, redirect: 'follow' })
            .then(r => { if (r.redirected) location.assign(r.url); });
    }

    document.addEventListener('change', (e) => {
        if (!e.target.classList.contains('poll-vote-radio') || !e.target.checked) return;
        const row = e.target.closest('[data-vote-url]');
        if (row) submitPollVote(row);
    });

    document.addEventListener('click', (e) => {
        const optionRow = e.target.closest('.poll-option-row');
        if (optionRow && !e.target.closest('.poll-remove-option-btn')) {
            e.preventDefault();
            const radio = optionRow.querySelector('.poll-vote-radio');
            if (radio && !radio.checked) {
                radio.checked = true;
                submitPollVote(optionRow);
            }
        }
    });

    // 5.7. Голосование с карточки (на доске, без открытия модалки)
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.poll-vote-btn-card');
        if (!btn) return;
        e.preventDefault();
        e.stopPropagation();
        const block = btn.closest('.poll-on-card');
        const url = block.getAttribute('data-vote-url');
        const optionId = btn.getAttribute('data-option-id');
        const csrf = block.getAttribute('data-csrf');
        if (!url || !optionId || !csrf) return;
        const fd = new FormData();
        fd.append('csrfmiddlewaretoken', csrf);
        fd.append('option_id', optionId);
        fetch(url, { method: 'POST', body: fd, redirect: 'follow' })
            .then(r => { if (r.redirected) location.assign(r.url); });
    });
});