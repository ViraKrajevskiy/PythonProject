/**
 * 1. РАБОТА С КУКИ (Для Google Translate)
 */
function setCookie(name, value, days) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${d.toUTCString()};path=/`;
}

/**
 * 2. ЛОГИКА ПЕРЕВОДА
 */
function changeLang(langCode) {
    // Сохраняем выбор в localStorage для обновления текста на кнопке
    localStorage.setItem('userLang', langCode);

    if (langCode === 'ru') {
        // Удаляем куки перевода для возврата к оригиналу
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=" + location.hostname;
    } else {
        // Устанавливаем куку формата /исходный/целевой
        setCookie('googtrans', `/ru/${langCode}`, 1);
    }

    // Перезагружаем страницу, чтобы Google Translate подхватил настройки
    location.reload();
}

// Коллбэк для инициализации Google Translate
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'ru',
        includedLanguages: 'ru,en,zh-CN,uz',
        autoDisplay: false
    }, 'google_translate_element');
}

/**
 * 3. УПРАВЛЕНИЕ ТЕМАМИ И АНИМАЦИЕЙ
 */
function setTheme(themeName) {
    const themes = ['theme-purple', 'theme-green', 'theme-orange', 'theme-red', 'theme-pink', 'theme-dark'];

    // Чистим классы с html и body
    document.documentElement.classList.remove(...themes);
    document.body.classList.remove(...themes);

    if (themeName !== 'default') {
        const className = 'theme-' + themeName;
        document.documentElement.classList.add(className);
        document.body.classList.add(className);
    }
    localStorage.setItem('selectedTheme', themeName);
}

function toggleAnimation() {
    const isAnimated = document.body.classList.toggle('animated-bg');
    document.documentElement.classList.toggle('animated-bg');
    localStorage.setItem('bgAnimation', isAnimated);
}

/**
 * 4. ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ DOM
 */
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('selectedTheme');
    if (savedTheme) setTheme(savedTheme);
    if (localStorage.getItem('bgAnimation') === 'true') {
        document.body.classList.add('animated-bg');
        document.documentElement.classList.add('animated-bg');
    }
   const savedLang = localStorage.getItem('userLang');
    if (savedLang) {
        const label = document.getElementById('current-lang-label');
        if (label) {
            label.innerText = savedLang.split('-')[0].toUpperCase();
        }
    }
});