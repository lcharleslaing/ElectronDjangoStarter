const THEME_STORAGE_KEY = 'theme';

function getAllDaisyThemes() {
    return [
        "light", "dark", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", "retro",
        "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", "lofi", "pastel",
        "fantasy", "wireframe", "black", "luxury", "dracula", "cmyk", "autumn", "business",
        "acid", "lemonade", "night", "coffee", "winter", "dim", "nord", "sunset"
    ];
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

async function persistThemeServer(theme) {
    try {
        const res = await fetch('/api/preferences/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ theme })
        });
        if (!res.ok) throw new Error('Failed to persist theme');
    } catch (err) {
        console.warn('Theme persist skipped:', err);
    }
}

function setupThemeSelect() {
    const select = document.getElementById('theme-select');
    if (!select) return;
    const themes = getAllDaisyThemes();
    select.innerHTML = themes.map(t => `<option value="${t}">${t}</option>`).join('');
    const saved = localStorage.getItem(THEME_STORAGE_KEY) || themes[0];
    select.value = saved;
    applyTheme(saved);
    select.addEventListener('change', () => {
        const t = select.value;
        localStorage.setItem(THEME_STORAGE_KEY, t);
        applyTheme(t);
        persistThemeServer(t);
    });
}

function setupDrawers() {
    function closeDrawers() {
        const left = document.getElementById('left-drawer-toggle');
        const right = document.getElementById('right-drawer-toggle');
        if (left) left.checked = false;
        if (right) right.checked = false;
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeDrawers();
    });
}

function setupOnlineIndicator() {
    const badge = document.getElementById('online-indicator');
    const update = () => {
        if (!badge) return;
        const online = navigator.onLine;
        badge.classList.toggle('badge-success', online);
        badge.classList.toggle('badge-error', !online);
        badge.textContent = online ? 'Online' : 'Offline';
    };
    window.addEventListener('online', update);
    window.addEventListener('offline', update);
    update();
}

(function init() {
    setupThemeSelect();
    setupDrawers();
    setupOnlineIndicator();
})();
