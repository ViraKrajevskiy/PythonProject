/**
 * Online Trello - Final JS Controller
 * Управление доской, задачами, комментариями и динамической загрузкой
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

    // Запрос HTML-контента задачи (View: task_detail_view)
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

            // Обновляем URL (для возможности поделиться ссылкой)
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
            // Включаем режим правки
            editDiv.classList.remove('d-none');
            textDiv.classList.add('d-none');

            const area = editDiv.querySelector('textarea');
            if (area) {
                area.focus();
                // Ставим курсор в конец текста
                const val = area.value;
                area.value = '';
                area.value = val;
            }
        } else {
            // Отмена
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

        // Визуальная блокировка кнопки
        const btn = event.currentTarget;
        btn.disabled = true;
        btn.innerHTML = '...';

        form.submit();
    }
}

// 4. ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ
document.addEventListener('DOMContentLoaded', () => {

    // 4.1. Проверка URL на наличие ID задачи (если перешли по ссылке)
    const urlParams = new URLSearchParams(window.location.search);
    const openTaskId = urlParams.get('open_task');
    if (openTaskId) {
        openTaskModal(openTaskId);
    }

    // 4.2. Очистка URL при закрытии модалки
    const modalEl = document.getElementById('universalTaskModal');
    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', () => {
            const url = new URL(window.location);
            url.searchParams.delete('open_task');
            window.history.replaceState({}, '', url);
        });
    }

    // 4.3. Обработка горячих клавиш (Ctrl + Enter для отправки)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const active = document.activeElement;
            if (active && active.tagName === 'TEXTAREA') {
                // Если это textarea в блоке редактирования комментария
                if (active.id.startsWith('edit-textarea-')) {
                    const id = active.id.split('-').pop();
                    submitEditComment(id);
                }
                // Если это обычная форма (например, описание или новый коммент)
                else {
                    const form = active.closest('form');
                    if (form) form.submit();
                }
            }
        }
    });
});