/**
 * 1. РАБОТА С КУКИ (Исправлено для Google Translate)
 */
function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    // Устанавливаем SameSite=Lax и путь, чтобы кука была видна везде
    document.cookie = `${name}=${value};expires=${d.toUTCString()};path=/;SameSite=Lax`;
}

/**
 * 2. ЛОГИКА ПЕРЕВОДА
 */
function clearGoogtransCookie() {
    var expire = 'expires=Thu, 01 Jan 1970 00:00:00 GMT';
    document.cookie = 'googtrans=;' + expire + ';path=/';
    document.cookie = 'googtrans=;' + expire + ';path=/;domain=' + location.hostname;
}

function changeLang(langCode) {
    // Базовый = оригинал без перевода
    if (langCode === '' || langCode === 'base') {
        localStorage.setItem('userLang', 'base');
        clearGoogtransCookie();
        location.reload();
        return;
    }

    localStorage.setItem('userLang', langCode);
    var toLang = (langCode === 'zh-CN' || langCode === 'zh_CN') ? 'zh-CN' : langCode;
    setCookie('googtrans', '/auto/' + toLang, 1);
    const domain = location.hostname;
    document.cookie = 'googtrans=/auto/' + toLang + ';path=/;domain=' + domain + ';SameSite=Lax';
    location.reload();
}

/**
 * 3. ОТКРЫТИЕ МОДАЛКИ ЗАДАЧИ (AJAX)
 */
function openTaskModal(taskId) {
    const contentDiv = document.getElementById('taskModalContent');
    const modalEl = document.getElementById('universalTaskModal');

    if (!contentDiv || !modalEl) return;

    // Спиннер загрузки
    contentDiv.innerHTML = `
        <div class="p-5 text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">Загрузка задачи...</p>
        </div>
    `;

    let modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
    modalInstance.show();

    // Запрос к серверу
    fetch(`/task/${taskId}/get_details/`)
        .then(response => {
            if (!response.ok) throw new Error('Ошибка при загрузке данных');
            return response.text();
        })
        .then(html => {
            contentDiv.innerHTML = html;
        })
        .catch(err => {
            contentDiv.innerHTML = `
                <div class="p-5 text-center">
                    <h5 class="text-danger">Ошибка</h5>
                    <p>${err.message}</p>
                    <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Закрыть</button>
                </div>
            `;
        });
}

/**
 * 4. РЕДАКТИРОВАНИЕ КОММЕНТАРИЕВ
 */
function toggleEditComment(commentId) {
    const textDiv = document.getElementById(`comment-text-${commentId}`);
    const editBox = document.getElementById(`edit-box-${commentId}`);
    if (textDiv && editBox) {
        textDiv.classList.toggle('d-none');
        editBox.classList.toggle('d-none');
    }
}

function submitEditComment(commentId) {
    const textarea = document.getElementById(`edit-textarea-${commentId}`);
    const hiddenInput = document.getElementById(`hidden-edit-input-${commentId}`);
    const form = document.getElementById(`editCommentForm${commentId}`);

    if (textarea && hiddenInput && form) {
        if (textarea.value.trim() === "") return;
        hiddenInput.value = textarea.value;
        form.submit();
    }
}

/**
 * 5. ТЕМЫ И АНИМАЦИИ
 */
function setTheme(themeName) {
    const themes = ['theme-purple', 'theme-green', 'theme-orange', 'theme-red', 'theme-pink', 'theme-dark'];
    document.documentElement.classList.remove(...themes);
    document.body.classList.remove(...themes);

    if (themeName !== 'default') {
        document.documentElement.classList.add('theme-' + themeName);
        document.body.classList.add('theme-' + themeName);
    }
    localStorage.setItem('selectedTheme', themeName);
}

function toggleAnimation() {
    const isActive = document.body.classList.toggle('animated-bg');
    document.documentElement.classList.toggle('animated-bg');
    localStorage.setItem('bgAnimation', isActive ? 'true' : 'false');
}

/**
 * 6. ИНИЦИАЛИЗАЦИЯ
 */
document.addEventListener('DOMContentLoaded', () => {
    // Тема
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) setTheme(savedTheme);

    // Анимация
    if (localStorage.getItem('bgAnimation') === 'true') {
        document.body.classList.add('animated-bg');
        document.documentElement.classList.add('animated-bg');
    }

    // Текст на кнопке языка
    const savedLang = localStorage.getItem('userLang');
    const label = document.getElementById('current-lang-label');
    if (label) {
        if (savedLang === 'base' || savedLang === '' || !savedLang) label.innerText = 'Баз';
        else if (savedLang === 'zh-CN' || savedLang === 'zh_CN') label.innerText = 'CN';
        else label.innerText = savedLang.toUpperCase().slice(0, 2);
    }

    // Авто-скрытие уведомлений через 5 сек, чтобы не зависали на досках
    document.querySelectorAll('.messages-alert').forEach(function(alertEl) {
        setTimeout(function() {
            const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
            if (alertEl.parentNode) alert.close();
        }, 5000);
    });
});