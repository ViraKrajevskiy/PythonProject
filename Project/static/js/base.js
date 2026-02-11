/**
 * 1. РАБОТА С КУКИ (Для Google Translate)
 */
function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    // SameSite=Lax необходим для работы в современных браузерах
    document.cookie = `${name}=${value};expires=${d.toUTCString()};path=/;SameSite=Lax`;
}

/**
 * 2. ЛОГИКА ПЕРЕВОДА ЯЗЫКА
 */
function changeLang(langCode) {
    // Сохраняем код языка для иконки на кнопке
    localStorage.setItem('userLang', langCode);

    if (langCode === 'ru') {
        // Очистка куки для возврата к исходному языку
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=" + location.hostname;
    } else {
        // Формат куки Google Translate: /исходный_язык/целевой_язык
        setCookie('googtrans', `/ru/${langCode}`, 1);
    }

    // Перезагрузка для применения изменений
    location.reload();
}

/**
 * 3. УПРАВЛЕНИЕ ТЕМАМИ ОФОРМЛЕНИЯ
 */
function setTheme(themeName) {
    const themes = ['theme-purple', 'theme-green', 'theme-orange', 'theme-red', 'theme-pink', 'theme-dark'];

    // Удаляем все предыдущие классы тем с <html> и <body>
    document.documentElement.classList.remove(...themes);
    document.body.classList.remove(...themes);

    if (themeName !== 'default') {
        const className = 'theme-' + themeName;
        document.documentElement.classList.add(className);
        document.body.classList.add(className);
    }

    // Запоминаем выбор пользователя
    localStorage.setItem('selectedTheme', themeName);
}

/**
 * 4. УПРАВЛЕНИЕ АНИМАЦИЕЙ ФОНА
 */
function toggleAnimation() {
    const isActive = document.body.classList.toggle('animated-bg');
    document.documentElement.classList.toggle('animated-bg');

    // Сохраняем состояние (строкой, так как localStorage хранит только строки)
    localStorage.setItem('bgAnimation', isActive ? 'true' : 'false');
}

/**
 * 5. ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ
 */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Применяем сохраненную тему
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) {
        setTheme(savedTheme);
    }

    // 2. Применяем анимацию фона
    const savedAnim = localStorage.getItem('bgAnimation');
    if (savedAnim === 'true') {
        document.body.classList.add('animated-bg');
        document.documentElement.classList.add('animated-bg');
    }

    // 3. Обновляем текстовую метку текущего языка на кнопке
    const savedLang = localStorage.getItem('userLang');
    const label = document.getElementById('current-lang-label');

    if (label && savedLang) {
        let displayLang = savedLang.toUpperCase();
        // Красивое сокращение для китайского
        if (displayLang === 'ZH-CN') displayLang = 'CN';
        label.innerText = displayLang;
    }

    // 4. Автоматическое скрытие алертов (сообщений) через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});