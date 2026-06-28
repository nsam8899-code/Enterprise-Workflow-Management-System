// Theme Switching
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

function toggleTheme() {
    if (document.body.classList.contains('dark-mode')) {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
    } else {
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
    }
}

// Sidebar toggling
function toggleSidebar() {
    const container = document.querySelector('.app-container');
    if (container) {
        container.classList.toggle('sidebar-collapsed');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }
});
