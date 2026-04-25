/* ======================================
   Rising Star Todo - Application Logic
   ====================================== */

(() => {
    'use strict';

    // ---- Configuration ----
    const API_BASE = window.location.origin;
    const STORAGE_KEYS = {
        token: 'rs_todo_token',
        user: 'rs_todo_user',
        theme: 'rs_todo_theme',
        localTasks: 'rs_todo_tasks'
    };

    // ---- State ----
    let state = {
        token: localStorage.getItem(STORAGE_KEYS.token) || null,
        user: JSON.parse(localStorage.getItem(STORAGE_KEYS.user) || 'null'),
        tasks: JSON.parse(localStorage.getItem(STORAGE_KEYS.localTasks) || '[]'),
        currentFilter: 'all',
        searchQuery: '',
        sortBy: 'newest',
        editingTaskId: null,
        draggedItem: null
    };

    // ---- DOM References ----
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const DOM = {
        // Landing + Auth Modal
        landingPage: $('#landing-page'),
        authModal: $('#auth-modal'),
        authModalClose: $('#auth-modal-close'),
        loginScreen: $('#login-screen'),
        signupScreen: $('#signup-screen'),
        loginForm: $('#login-form'),
        signupForm: $('#signup-form'),
        loginError: $('#login-error'),
        signupError: $('#signup-error'),
        signupSuccess: $('#signup-success'),
        showSignup: $('#show-signup'),
        showLogin: $('#show-login'),
        loginBtn: $('#login-btn'),
        signupBtn: $('#signup-btn'),

        // App
        appContainer: $('#app-container'),
        sidebar: $('#sidebar'),
        sidebarOverlay: $('#sidebar-overlay'),
        sidebarCloseBtn: $('#sidebar-close-btn'),
        menuToggleBtn: $('#menu-toggle-btn'),
        themeToggleBtn: $('#theme-toggle-btn'),
        logoutBtn: $('#logout-btn'),

        // User display
        userAvatar: $('#user-avatar'),
        userDisplayName: $('#user-display-name'),

        // Content
        pageTitle: $('#page-title'),
        pageSubtitle: $('#page-subtitle'),
        searchInput: $('#search-input'),
        sortSelect: $('#sort-select'),
        addTaskBtn: $('#add-task-btn'),
        emptyAddBtn: $('#empty-add-btn'),
        taskList: $('#task-list'),
        emptyState: $('#empty-state'),
        taskListTitle: $('#task-list-title'),

        // Stats
        statTotal: $('#stat-total'),
        statActive: $('#stat-active'),
        statDone: $('#stat-done'),
        statHigh: $('#stat-high'),

        // Badges
        badgeAll: $('#badge-all'),
        badgeActive: $('#badge-active'),
        badgeCompleted: $('#badge-completed'),
        badgeHigh: $('#badge-high'),
        badgeMedium: $('#badge-medium'),
        badgeLow: $('#badge-low'),

        // Modal
        modalOverlay: $('#task-modal'),
        modalTitle: $('#modal-title'),
        modalCloseBtn: $('#modal-close-btn'),
        modalCancelBtn: $('#modal-cancel-btn'),
        modalSaveBtn: $('#modal-save-btn'),
        taskForm: $('#task-form'),
        taskEditId: $('#task-edit-id'),
        taskTitleInput: $('#task-title-input'),
        taskNotesInput: $('#task-notes-input'),
        taskDueInput: $('#task-due-input'),
        subtaskInput: $('#subtask-input'),
        subtaskList: $('#subtask-list'),
        addSubtaskBtn: $('#add-subtask-btn'),

        // Toast
        toastContainer: $('#toast-container'),

        // Info Modal
        infoModal: $('#info-modal'),
        infoModalClose: $('#info-modal-close'),
        infoModalIcon: $('#info-modal-icon'),
        infoModalTitle: $('#info-modal-title'),
        infoModalDesc: $('#info-modal-desc')
    };

    // ======================================
    // UTILITIES
    // ======================================

    function generateId() {
        return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        const now = new Date();
        const diff = Math.ceil((d - now) / (1000 * 60 * 60 * 24));
        if (diff === 0) return 'Today';
        if (diff === 1) return 'Tomorrow';
        if (diff === -1) return 'Yesterday';
        if (diff < -1) return 'Overdue';
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    function isOverdue(dateStr) {
        if (!dateStr) return false;
        return new Date(dateStr) < new Date(new Date().toDateString());
    }

    function saveTasks() {
        localStorage.setItem(STORAGE_KEYS.localTasks, JSON.stringify(state.tasks));
    }

    // ======================================
    // API LAYER
    // ======================================

    async function apiRequest(endpoint, options = {}) {
        const headers = { 'Content-Type': 'application/json', ...options.headers };
        if (state.token) {
            headers['Authorization'] = `Bearer ${state.token}`;
        }
        const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            // If 401, token expired — log out
            if (res.status === 401 && state.token) {
                logout();
                throw new Error('Session expired. Please login again.');
            }
            throw new Error(err.detail || `Request failed (${res.status})`);
        }
        return await res.json();
    }

    async function apiLogin(username, password) {
        return apiRequest('/auth/token', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    async function apiRegister(username, email, password) {
        return apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password_hash: password })
        });
    }

    async function apiListTodos() {
        return apiRequest('/todo/listall');
    }

    async function apiCreateTodo(task) {
        return apiRequest('/todo/create', {
            method: 'POST',
            body: JSON.stringify({ task, user_id: state.user?.user_id || 0 })
        });
    }

    async function apiDeleteTodo(todoId) {
        return apiRequest(`/todo/delete/${todoId}`, { method: 'DELETE' });
    }

    async function apiEditTodo(todoId, task) {
        return apiRequest(`/todo/edit/${todoId}`, {
            method: 'PUT',
            body: JSON.stringify({ task, user_id: state.user?.user_id || 0 })
        });
    }

    // ======================================
    // THEME
    // ======================================

    function initTheme() {
        const saved = localStorage.getItem(STORAGE_KEYS.theme) || 'light';
        document.documentElement.setAttribute('data-theme', saved);
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem(STORAGE_KEYS.theme, next);
    }

    // ======================================
    // TOAST NOTIFICATIONS
    // ======================================

    function showToast(message, type = 'success') {
        const icons = {
            success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
            error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
            info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<div class="toast-icon">${icons[type]}</div><span>${message}</span>`;
        DOM.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('leaving');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ======================================
    // AUTH
    // ======================================

    function showAuth() {
        DOM.landingPage.classList.remove('hidden');
        DOM.appContainer.classList.add('hidden');
        DOM.authModal.classList.add('hidden');
        initCarousel();
    }

    function showApp() {
        DOM.landingPage.classList.add('hidden');
        DOM.authModal.classList.add('hidden');
        DOM.appContainer.classList.remove('hidden');
        updateUserDisplay();
        loadTodosFromAPI();
        renderAll();
    }

    function openAuthModal() {
        DOM.authModal.classList.remove('hidden');
        DOM.loginScreen.classList.remove('hidden');
        DOM.signupScreen.classList.add('hidden');
        DOM.loginError.classList.add('hidden');
        DOM.signupError.classList.add('hidden');
        DOM.signupSuccess.classList.add('hidden');
    }

    function closeAuthModal() {
        DOM.authModal.classList.add('hidden');
    }

    function openInfoModal(title, icon, desc) {
        DOM.infoModalIcon.textContent = icon;
        DOM.infoModalTitle.textContent = title;
        DOM.infoModalDesc.textContent = desc;
        DOM.infoModal.classList.remove('hidden');
    }

    function closeInfoModal() {
        DOM.infoModal.classList.add('hidden');
    }

    function updateUserDisplay() {
        if (state.user) {
            const name = state.user.username || 'User';
            DOM.userDisplayName.textContent = name;
            DOM.userAvatar.textContent = name.charAt(0).toUpperCase();
        }
    }

    async function loadTodosFromAPI() {
        try {
            const apiTodos = await apiListTodos();
            if (apiTodos && Array.isArray(apiTodos)) {
                // Merge API todos into local tasks
                apiTodos.forEach(apiTodo => {
                    const exists = state.tasks.find(t => t.apiId === apiTodo.id);
                    if (!exists) {
                        // Parse task data — the task field may be JSON string with metadata
                        let taskData = {
                            id: generateId(),
                            title: apiTodo.task,
                            notes: '',
                            priority: 'medium',
                            dueDate: '',
                            subtasks: [],
                            completed: false,
                            createdAt: Date.now(),
                            apiId: apiTodo.id
                        };

                        // Try parsing if task is a JSON string with metadata
                        try {
                            const parsed = JSON.parse(apiTodo.task);
                            if (parsed && parsed.title) {
                                taskData.title = parsed.title;
                                taskData.notes = parsed.notes || '';
                                taskData.priority = parsed.priority || 'medium';
                                taskData.dueDate = parsed.dueDate || '';
                                taskData.subtasks = parsed.subtasks || [];
                            }
                        } catch (e) {
                            // Task is a plain string, use as-is
                        }

                        state.tasks.push(taskData);
                    }
                });
                saveTasks();
                renderAll();
            }
        } catch (e) {
            console.log('Could not sync with API:', e.message);
        }
    }

    function logout() {
        state.token = null;
        state.user = null;
        state.tasks = [];
        localStorage.removeItem(STORAGE_KEYS.token);
        localStorage.removeItem(STORAGE_KEYS.user);
        localStorage.removeItem(STORAGE_KEYS.localTasks);
        showAuth();
        showToast('Logged out successfully', 'info');
    }

    function setBtnLoading(btn, loading) {
        const text = btn.querySelector('.btn-text');
        const loader = btn.querySelector('.btn-loader');
        if (loading) {
            text?.classList.add('hidden');
            loader?.classList.remove('hidden');
            btn.disabled = true;
        } else {
            text?.classList.remove('hidden');
            loader?.classList.add('hidden');
            btn.disabled = false;
        }
    }

    async function handleLogin(e) {
        e.preventDefault();
        const username = $('#login-username').value.trim();
        const password = $('#login-password').value;

        if (!username || !password) {
            DOM.loginError.textContent = 'Please enter both username and password.';
            DOM.loginError.classList.remove('hidden');
            return;
        }

        DOM.loginError.classList.add('hidden');
        setBtnLoading(DOM.loginBtn, true);

        try {
            const data = await apiLogin(username, password);
            state.token = data.access_token;
            state.user = { username: data.username || username, user_id: data.user_id };
            state.tasks = []; // Clear old tasks, will reload from API
            localStorage.setItem(STORAGE_KEYS.token, state.token);
            localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(state.user));
            localStorage.removeItem(STORAGE_KEYS.localTasks);
            showToast(`Welcome back, ${username}!`);
            showApp();
        } catch (err) {
            DOM.loginError.textContent = err.message || 'Invalid credentials. Please try again.';
            DOM.loginError.classList.remove('hidden');
        } finally {
            setBtnLoading(DOM.loginBtn, false);
        }
    }

    async function handleSignup(e) {
        e.preventDefault();
        const username = $('#signup-username').value.trim();
        const email = $('#signup-email').value.trim();
        const password = $('#signup-password').value;

        if (!username || !email || !password) {
            DOM.signupError.textContent = 'Please fill in all fields.';
            DOM.signupError.classList.remove('hidden');
            return;
        }

        if (password.length < 6) {
            DOM.signupError.textContent = 'Password must be at least 6 characters.';
            DOM.signupError.classList.remove('hidden');
            return;
        }

        DOM.signupError.classList.add('hidden');
        DOM.signupSuccess.classList.add('hidden');
        setBtnLoading(DOM.signupBtn, true);

        try {
            await apiRegister(username, email, password);
            DOM.signupSuccess.textContent = 'Account created! You can now sign in.';
            DOM.signupSuccess.classList.remove('hidden');
            showToast('Account created successfully!');
            // Clear signup fields
            $('#signup-username').value = '';
            $('#signup-email').value = '';
            $('#signup-password').value = '';
            setTimeout(() => switchToLogin(), 1500);
        } catch (err) {
            DOM.signupError.textContent = err.message || 'Registration failed. Try a different username.';
            DOM.signupError.classList.remove('hidden');
        } finally {
            setBtnLoading(DOM.signupBtn, false);
        }
    }

    function switchToSignup() {
        DOM.loginScreen.classList.add('hidden');
        DOM.signupScreen.classList.remove('hidden');
        DOM.signupScreen.style.animation = 'slideUpFade 0.4s ease-out';
        DOM.signupError.classList.add('hidden');
        DOM.signupSuccess.classList.add('hidden');
    }

    function switchToLogin() {
        DOM.signupScreen.classList.add('hidden');
        DOM.loginScreen.classList.remove('hidden');
        DOM.loginScreen.style.animation = 'slideUpFade 0.4s ease-out';
        DOM.loginError.classList.add('hidden');
    }

    // ======================================
    // CAROUSEL
    // ======================================

    let carouselInterval = null;

    function initCarousel() {
        const track = document.getElementById('carousel-track');
        const dots = document.querySelectorAll('.carousel-dots .dot');
        if (!track || dots.length === 0) return;

        let current = 0;
        const total = dots.length;

        function goToSlide(idx) {
            current = idx;
            track.style.transform = `translateX(-${current * 100}%)`;
            dots.forEach((d, i) => d.classList.toggle('active', i === current));
        }

        dots.forEach(d => d.addEventListener('click', () => goToSlide(parseInt(d.dataset.slide))));

        if (carouselInterval) clearInterval(carouselInterval);
        carouselInterval = setInterval(() => goToSlide((current + 1) % total), 4000);
    }

    // ======================================
    // SIDEBAR
    // ======================================

    function openSidebar() {
        DOM.sidebar.classList.add('open');
        DOM.sidebarOverlay.classList.add('active');
    }

    function closeSidebar() {
        DOM.sidebar.classList.remove('open');
        DOM.sidebarOverlay.classList.remove('active');
    }

    function setFilter(filter) {
        state.currentFilter = filter;
        $$('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.filter === filter);
        });
        const titles = {
            all: 'All Tasks',
            active: 'Active Tasks',
            completed: 'Completed Tasks',
            high: 'High Priority',
            medium: 'Medium Priority',
            low: 'Low Priority'
        };
        DOM.pageTitle.textContent = titles[filter] || 'All Tasks';
        DOM.taskListTitle.textContent = titles[filter] || 'All Tasks';
        closeSidebar();
        renderTasks();
    }

    // ======================================
    // TASK MANAGEMENT (Local + API Sync)
    // ======================================

    function getFilteredTasks() {
        let tasks = [...state.tasks];

        // Search filter
        if (state.searchQuery) {
            const q = state.searchQuery.toLowerCase();
            tasks = tasks.filter(t =>
                t.title.toLowerCase().includes(q) ||
                (t.notes && t.notes.toLowerCase().includes(q))
            );
        }

        // Category filter
        switch (state.currentFilter) {
            case 'active':
                tasks = tasks.filter(t => !t.completed);
                break;
            case 'completed':
                tasks = tasks.filter(t => t.completed);
                break;
            case 'high':
                tasks = tasks.filter(t => t.priority === 'high');
                break;
            case 'medium':
                tasks = tasks.filter(t => t.priority === 'medium');
                break;
            case 'low':
                tasks = tasks.filter(t => t.priority === 'low');
                break;
        }

        // Sort
        switch (state.sortBy) {
            case 'newest':
                tasks.sort((a, b) => b.createdAt - a.createdAt);
                break;
            case 'oldest':
                tasks.sort((a, b) => a.createdAt - b.createdAt);
                break;
            case 'priority': {
                const order = { high: 0, medium: 1, low: 2 };
                tasks.sort((a, b) => (order[a.priority] || 2) - (order[b.priority] || 2));
                break;
            }
            case 'alpha':
                tasks.sort((a, b) => a.title.localeCompare(b.title));
                break;
            case 'dueDate':
                tasks.sort((a, b) => {
                    if (!a.dueDate) return 1;
                    if (!b.dueDate) return -1;
                    return new Date(a.dueDate) - new Date(b.dueDate);
                });
                break;
        }

        return tasks;
    }

    function createTaskObject(title, notes, priority, dueDate, subtasks) {
        return {
            id: generateId(),
            title,
            notes: notes || '',
            priority: priority || 'medium',
            dueDate: dueDate || '',
            subtasks: subtasks || [],
            completed: false,
            createdAt: Date.now(),
            apiId: null
        };
    }

    async function addTask(taskData) {
        state.tasks.unshift(taskData);
        saveTasks();

        // Sync with API
        try {
            const taskStr = JSON.stringify({
                title: taskData.title,
                notes: taskData.notes,
                priority: taskData.priority,
                dueDate: taskData.dueDate,
                subtasks: taskData.subtasks
            });
            const result = await apiCreateTodo(taskStr);
            if (result && result.id) {
                taskData.apiId = result.id;
                saveTasks();
            }
        } catch (e) {
            console.log('Task saved locally, API sync pending:', e.message);
        }

        renderAll();
        showToast('Task created successfully!');
    }

    async function deleteTask(id) {
        const task = state.tasks.find(t => t.id === id);
        state.tasks = state.tasks.filter(t => t.id !== id);
        saveTasks();

        if (task && task.apiId) {
            try {
                await apiDeleteTodo(task.apiId);
            } catch (e) {
                console.log('API delete pending:', e.message);
            }
        }

        renderAll();
        showToast('Task deleted', 'info');
    }

    function toggleComplete(id) {
        const task = state.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            saveTasks();
            renderAll();

            if (task.completed) {
                showToast('Task completed! 🎉');
            }
        }
    }

    async function updateTask(id, updates) {
        const task = state.tasks.find(t => t.id === id);
        if (task) {
            Object.assign(task, updates);
            saveTasks();

            if (task.apiId) {
                try {
                    const taskStr = JSON.stringify({
                        title: task.title,
                        notes: task.notes,
                        priority: task.priority,
                        dueDate: task.dueDate,
                        subtasks: task.subtasks
                    });
                    await apiEditTodo(task.apiId, taskStr);
                } catch (e) {
                    console.log('API update pending:', e.message);
                }
            }

            renderAll();
            showToast('Task updated!');
        }
    }

    // ======================================
    // RENDERING
    // ======================================

    function renderAll() {
        renderTasks();
        updateStats();
        updateBadges();
    }

    function renderTasks() {
        const tasks = getFilteredTasks();
        DOM.taskList.innerHTML = '';

        if (tasks.length === 0) {
            DOM.emptyState.classList.remove('hidden');
            DOM.taskList.classList.add('hidden');
            return;
        }

        DOM.emptyState.classList.add('hidden');
        DOM.taskList.classList.remove('hidden');

        tasks.forEach(task => {
            DOM.taskList.appendChild(createTaskElement(task));
        });

        initDragAndDrop();
    }

    function createTaskElement(task) {
        const el = document.createElement('div');
        el.className = `task-item${task.completed ? ' completed' : ''}`;
        el.dataset.taskId = task.id;
        el.draggable = true;

        const dueDateStr = formatDate(task.dueDate);
        const overdue = !task.completed && isOverdue(task.dueDate);
        const completedSubtasks = task.subtasks ? task.subtasks.filter(s => s.done).length : 0;
        const totalSubtasks = task.subtasks ? task.subtasks.length : 0;

        el.innerHTML = `
            <div class="priority-indicator priority-${task.priority}"></div>
            <label class="task-checkbox">
                <input type="checkbox" ${task.completed ? 'checked' : ''} aria-label="Mark task complete">
                <div class="checkmark">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
            </label>
            <div class="task-body">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span class="task-tag tag-${task.priority}">
                        ${task.priority === 'high' ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>' : ''}
                        ${capitalize(task.priority)}
                    </span>
                    ${dueDateStr ? `<span class="task-tag ${overdue ? 'tag-overdue' : 'tag-due'}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                        ${dueDateStr}
                    </span>` : ''}
                    ${totalSubtasks > 0 ? `<span class="task-subtask-count">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
                        ${completedSubtasks}/${totalSubtasks}
                    </span>` : ''}
                    ${task.notes ? `<span class="task-notes-preview">${escapeHtml(task.notes)}</span>` : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="icon-btn icon-btn-sm edit-task-btn" title="Edit task" aria-label="Edit task">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <button class="icon-btn icon-btn-sm delete-task-btn" title="Delete task" aria-label="Delete task">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
            </div>
        `;

        // Event listeners
        el.querySelector('input[type="checkbox"]').addEventListener('change', () => toggleComplete(task.id));
        el.querySelector('.edit-task-btn').addEventListener('click', () => openEditModal(task));
        el.querySelector('.delete-task-btn').addEventListener('click', () => deleteTask(task.id));

        return el;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function updateStats() {
        const total = state.tasks.length;
        const active = state.tasks.filter(t => !t.completed).length;
        const done = state.tasks.filter(t => t.completed).length;
        const high = state.tasks.filter(t => t.priority === 'high' && !t.completed).length;

        animateCounter(DOM.statTotal, total);
        animateCounter(DOM.statActive, active);
        animateCounter(DOM.statDone, done);
        animateCounter(DOM.statHigh, high);
    }

    function animateCounter(el, target) {
        const current = parseInt(el.textContent) || 0;
        if (current === target) return;
        el.textContent = target;
        el.style.transform = 'scale(1.15)';
        el.style.transition = 'transform 0.2s ease';
        setTimeout(() => {
            el.style.transform = 'scale(1)';
        }, 200);
    }

    function updateBadges() {
        DOM.badgeAll.textContent = state.tasks.length;
        DOM.badgeActive.textContent = state.tasks.filter(t => !t.completed).length;
        DOM.badgeCompleted.textContent = state.tasks.filter(t => t.completed).length;
        DOM.badgeHigh.textContent = state.tasks.filter(t => t.priority === 'high').length;
        DOM.badgeMedium.textContent = state.tasks.filter(t => t.priority === 'medium').length;
        DOM.badgeLow.textContent = state.tasks.filter(t => t.priority === 'low').length;
    }

    // ======================================
    // MODAL
    // ======================================

    let currentSubtasks = [];
    let currentPriority = 'medium';

    function openCreateModal() {
        state.editingTaskId = null;
        DOM.taskEditId.value = '';
        DOM.taskTitleInput.value = '';
        DOM.taskNotesInput.value = '';
        DOM.taskDueInput.value = '';
        currentSubtasks = [];
        currentPriority = 'medium';

        DOM.modalTitle.textContent = 'New Task';
        DOM.modalSaveBtn.querySelector('.btn-text').textContent = 'Create Task';

        updatePriorityUI();
        renderSubtasks();

        DOM.modalOverlay.classList.remove('hidden');
        DOM.taskTitleInput.focus();
    }

    function openEditModal(task) {
        state.editingTaskId = task.id;
        DOM.taskEditId.value = task.id;
        DOM.taskTitleInput.value = task.title;
        DOM.taskNotesInput.value = task.notes || '';
        DOM.taskDueInput.value = task.dueDate || '';
        currentSubtasks = task.subtasks ? task.subtasks.map(s => ({...s})) : [];
        currentPriority = task.priority || 'medium';

        DOM.modalTitle.textContent = 'Edit Task';
        DOM.modalSaveBtn.querySelector('.btn-text').textContent = 'Save Changes';

        updatePriorityUI();
        renderSubtasks();

        DOM.modalOverlay.classList.remove('hidden');
        DOM.taskTitleInput.focus();
    }

    function closeModal() {
        DOM.modalOverlay.classList.add('hidden');
        state.editingTaskId = null;
    }

    function updatePriorityUI() {
        $$('.priority-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.priority === currentPriority);
        });
    }

    function renderSubtasks() {
        DOM.subtaskList.innerHTML = '';
        currentSubtasks.forEach((sub, idx) => {
            const item = document.createElement('div');
            item.className = `subtask-item${sub.done ? ' done' : ''}`;
            item.innerHTML = `
                <input type="checkbox" ${sub.done ? 'checked' : ''}>
                <span>${escapeHtml(sub.text)}</span>
                <div class="subtask-remove" data-idx="${idx}">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </div>
            `;
            item.querySelector('input').addEventListener('change', () => {
                currentSubtasks[idx].done = !currentSubtasks[idx].done;
                renderSubtasks();
            });
            item.querySelector('.subtask-remove').addEventListener('click', () => {
                currentSubtasks.splice(idx, 1);
                renderSubtasks();
            });
            DOM.subtaskList.appendChild(item);
        });
    }

    function addSubtask() {
        const text = DOM.subtaskInput.value.trim();
        if (!text) return;
        currentSubtasks.push({ text, done: false });
        DOM.subtaskInput.value = '';
        renderSubtasks();
        DOM.subtaskInput.focus();
    }

    async function handleTaskSubmit(e) {
        e.preventDefault();
        const title = DOM.taskTitleInput.value.trim();
        if (!title) return;

        const notes = DOM.taskNotesInput.value.trim();
        const dueDate = DOM.taskDueInput.value;

        setBtnLoading(DOM.modalSaveBtn, true);

        try {
            if (state.editingTaskId) {
                // Edit mode
                await updateTask(state.editingTaskId, {
                    title,
                    notes,
                    priority: currentPriority,
                    dueDate,
                    subtasks: currentSubtasks.map(s => ({...s}))
                });
            } else {
                // Create mode
                const taskData = createTaskObject(title, notes, currentPriority, dueDate, currentSubtasks.map(s => ({...s})));
                await addTask(taskData);
            }
            closeModal();
        } catch (err) {
            showToast(err.message || 'Something went wrong', 'error');
        } finally {
            setBtnLoading(DOM.modalSaveBtn, false);
        }
    }

    // ======================================
    // DRAG & DROP
    // ======================================

    function initDragAndDrop() {
        const items = $$('.task-item');
        items.forEach(item => {
            item.addEventListener('dragstart', handleDragStart);
            item.addEventListener('dragend', handleDragEnd);
            item.addEventListener('dragover', handleDragOver);
            item.addEventListener('drop', handleDrop);
        });
    }

    function handleDragStart(e) {
        state.draggedItem = this;
        this.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    }

    function handleDragEnd() {
        this.classList.remove('dragging');
        state.draggedItem = null;
        $$('.task-item').forEach(i => i.style.borderTop = '');
    }

    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        if (this !== state.draggedItem) {
            this.style.borderTop = '2px solid var(--primary)';
        }
    }

    function handleDrop(e) {
        e.preventDefault();
        this.style.borderTop = '';
        if (this === state.draggedItem) return;

        const fromId = state.draggedItem.dataset.taskId;
        const toId = this.dataset.taskId;
        const fromIdx = state.tasks.findIndex(t => t.id === fromId);
        const toIdx = state.tasks.findIndex(t => t.id === toId);

        if (fromIdx !== -1 && toIdx !== -1) {
            const [moved] = state.tasks.splice(fromIdx, 1);
            state.tasks.splice(toIdx, 0, moved);
            saveTasks();
            renderTasks();
        }
    }

    // ======================================
    // SEARCH & SORT
    // ======================================

    let searchTimeout;
    function handleSearch() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            state.searchQuery = DOM.searchInput.value.trim();
            renderTasks();
        }, 250);
    }

    function handleSort() {
        state.sortBy = DOM.sortSelect.value;
        renderTasks();
    }

    // ======================================
    // EVENT BINDING
    // ======================================

    function bindEvents() {
        // Auth
        DOM.loginForm.addEventListener('submit', handleLogin);
        DOM.signupForm.addEventListener('submit', handleSignup);
        DOM.showSignup.addEventListener('click', (e) => { e.preventDefault(); switchToSignup(); });
        DOM.showLogin.addEventListener('click', (e) => { e.preventDefault(); switchToLogin(); });

        // Auth Modal
        DOM.authModalClose.addEventListener('click', closeAuthModal);
        DOM.authModal.addEventListener('click', (e) => { if (e.target === DOM.authModal) closeAuthModal(); });

        // Get Started buttons
        ['#hero-get-started', '.hero-get-started', '#landing-get-started-nav', '#footer-get-started'].forEach(sel => {
            document.querySelectorAll(sel).forEach(btn => {
                btn.addEventListener('click', openAuthModal);
            });
        });

        // Info Modal (Feature boxes)
        $$('[data-modal="true"]').forEach(box => {
            box.addEventListener('click', () => {
                openInfoModal(box.dataset.title, box.dataset.icon, box.dataset.desc);
            });
        });
        DOM.infoModalClose.addEventListener('click', closeInfoModal);
        DOM.infoModal.addEventListener('click', (e) => { if (e.target === DOM.infoModal) closeInfoModal(); });

        // Sidebar
        DOM.menuToggleBtn.addEventListener('click', openSidebar);
        DOM.sidebarCloseBtn.addEventListener('click', closeSidebar);
        DOM.sidebarOverlay.addEventListener('click', closeSidebar);
        $$('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                setFilter(item.dataset.filter);
            });
        });

        // Actions
        DOM.themeToggleBtn.addEventListener('click', toggleTheme);
        DOM.logoutBtn.addEventListener('click', logout);
        DOM.searchInput.addEventListener('input', handleSearch);
        DOM.sortSelect.addEventListener('change', handleSort);

        // Task creation
        DOM.addTaskBtn.addEventListener('click', openCreateModal);
        DOM.emptyAddBtn.addEventListener('click', openCreateModal);

        // Modal
        DOM.modalCloseBtn.addEventListener('click', closeModal);
        DOM.modalCancelBtn.addEventListener('click', closeModal);
        DOM.modalOverlay.addEventListener('click', (e) => {
            if (e.target === DOM.modalOverlay) closeModal();
        });
        DOM.taskForm.addEventListener('submit', handleTaskSubmit);

        // Priority buttons
        $$('.priority-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                currentPriority = btn.dataset.priority;
                updatePriorityUI();
            });
        });

        // Subtasks
        DOM.addSubtaskBtn.addEventListener('click', addSubtask);
        DOM.subtaskInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); addSubtask(); }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeModal();
                closeSidebar();
                closeAuthModal();
                closeInfoModal();
            }
            if (e.key === 'n' && !e.ctrlKey && !e.metaKey && !isInputFocused()) {
                e.preventDefault();
                openCreateModal();
            }
        });
    }

    function isInputFocused() {
        const tag = document.activeElement?.tagName;
        return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
    }

    // ======================================
    // CHATBOT
    // ======================================

    const chatbotDOM = {
        fab: $('#chatbot-fab'),
        modal: $('#chatbot-modal'),
        messages: $('#chatbot-messages'),
        form: $('#chatbot-form'),
        input: $('#chatbot-input'),
        sendBtn: $('#chatbot-send-btn'),
        clearBtn: $('#chatbot-clear-btn')
    };

    let chatOpen = false;
    let chatSending = false;

    function toggleChatbot() {
        chatOpen = !chatOpen;
        chatbotDOM.fab.classList.toggle('active', chatOpen);
        if (chatOpen) {
            chatbotDOM.modal.classList.remove('hidden');
            chatbotDOM.modal.style.animation = 'chatOpen 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)';
            chatbotDOM.input.focus();
            scrollChat();
        } else {
            chatbotDOM.modal.classList.add('hidden');
        }
    }

    function scrollChat() {
        setTimeout(() => {
            chatbotDOM.messages.scrollTop = chatbotDOM.messages.scrollHeight;
        }, 50);
    }

    function getTimeStr() {
        return new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    }

    function addChatBubble(content, type, isHtml = false) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${type}`;
        bubble.innerHTML = `
            <div class="bubble-content">${isHtml ? content : escapeHtml(content)}</div>
            <div class="bubble-time">${getTimeStr()}</div>
        `;
        chatbotDOM.messages.appendChild(bubble);
        scrollChat();
        return bubble;
    }

    function showTypingIndicator() {
        const typing = document.createElement('div');
        typing.className = 'chat-bubble bot';
        typing.id = 'typing-bubble';
        typing.innerHTML = `
            <div class="bubble-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatbotDOM.messages.appendChild(typing);
        scrollChat();
    }

    function removeTypingIndicator() {
        const el = document.getElementById('typing-bubble');
        if (el) el.remove();
    }

    // ---- Todo Creation via Chat ----

    // Patterns that indicate the user wants to create a todo
    const TODO_PATTERNS = [
        /^(?:add\s+(?:a\s+)?task|create\s+(?:a\s+)?(?:todo|task)|new\s+(?:todo|task)|remind\s+me\s+to|todo|make\s+(?:a\s+)?(?:todo|task)|set\s+(?:a\s+)?(?:reminder|task))[\s:]*(.+)/i,
        /^(?:i\s+need\s+to|i\s+have\s+to|i\s+should|don'?t\s+forget\s+to|remember\s+to)[\s:]*(.+)/i
    ];

    // Date patterns to extract from the task text
    const DATE_PATTERNS = [
        // YYYY-MM-DD
        { regex: /\b(?:by|on|due|before|until|at)\s+(\d{4}-\d{2}-\d{2})\b/i, extract: (m) => m[1] },
        // "by tomorrow"
        { regex: /\b(?:by|on|due|before)\s+tomorrow\b/i, extract: () => {
            const d = new Date(); d.setDate(d.getDate() + 1);
            return d.toISOString().split('T')[0];
        }},
        // "by today"
        { regex: /\b(?:by|on|due|before)\s+today\b/i, extract: () => {
            return new Date().toISOString().split('T')[0];
        }},
        // "by next week" (7 days)
        { regex: /\b(?:by|on|before)\s+next\s+week\b/i, extract: () => {
            const d = new Date(); d.setDate(d.getDate() + 7);
            return d.toISOString().split('T')[0];
        }},
        // "by DD/MM/YYYY" or "by MM/DD/YYYY"
        { regex: /\b(?:by|on|due|before)\s+(\d{1,2})\/(\d{1,2})\/(\d{4})\b/i, extract: (m) => {
            return `${m[3]}-${m[1].padStart(2,'0')}-${m[2].padStart(2,'0')}`;
        }},
        // "by Jan 15" or "by January 15"
        { regex: /\b(?:by|on|due|before)\s+(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?\b/i, extract: (m) => {
            const months = {jan:1,feb:2,mar:3,apr:4,may:5,jun:6,jul:7,aug:8,sep:9,oct:10,nov:11,dec:12};
            const key = m[1].slice(0,3).toLowerCase();
            const month = months[key];
            const year = new Date().getFullYear();
            return `${year}-${String(month).padStart(2,'0')}-${m[2].padStart(2,'0')}`;
        }},
        // standalone YYYY-MM-DD anywhere in the text
        { regex: /(\d{4}-\d{2}-\d{2})/, extract: (m) => m[1] }
    ];

    function parseTodoFromMessage(message) {
        let taskText = null;

        for (const pattern of TODO_PATTERNS) {
            const match = message.match(pattern);
            if (match) {
                taskText = match[1].trim();
                break;
            }
        }

        if (!taskText) return null;

        // Extract date if present
        let dueDate = '';
        for (const dp of DATE_PATTERNS) {
            const dateMatch = taskText.match(dp.regex);
            if (dateMatch) {
                dueDate = dp.extract(dateMatch);
                // Remove the date portion from the task title
                taskText = taskText.replace(dp.regex, '').trim();
                break;
            }
        }

        // Clean up the task text
        taskText = taskText.replace(/^[\s:,\-]+|[\s:,\-]+$/g, '').trim();

        if (!taskText) return null;

        // Capitalize first letter
        taskText = taskText.charAt(0).toUpperCase() + taskText.slice(1);

        return { title: taskText, dueDate };
    }

    function buildTodoCardHtml(title, dueDate) {
        const dateDisplay = dueDate
            ? `<div class="chat-todo-date">📅 Due: ${formatDate(dueDate) || dueDate}</div>`
            : '';
        return `
            ✅ <b>Todo created!</b>
            <div class="chat-todo-card">
                <div class="chat-todo-title">${escapeHtml(title)}</div>
                ${dateDisplay}
            </div>
            Your task has been added to your list.
        `;
    }

    async function handleChatTodoCreate(parsed) {
        const taskData = createTaskObject(
            parsed.title,
            '',
            'medium',
            parsed.dueDate,
            []
        );
        await addTask(taskData);
        return buildTodoCardHtml(parsed.title, parsed.dueDate);
    }

    async function sendChatMessage(message) {
        if (!message.trim() || chatSending) return;

        chatSending = true;
        chatbotDOM.sendBtn.disabled = true;

        // Add user bubble
        addChatBubble(message, 'user');
        chatbotDOM.input.value = '';

        // Check if it's a todo-creation request
        const todoData = parseTodoFromMessage(message);

        if (todoData) {
            // Show typing briefly
            showTypingIndicator();
            await new Promise(r => setTimeout(r, 600));
            removeTypingIndicator();

            try {
                const cardHtml = await handleChatTodoCreate(todoData);
                addChatBubble(cardHtml, 'bot', true);
            } catch (err) {
                addChatBubble('⚠️ Sorry, I couldn\'t create that todo. Please try again.', 'bot');
            }
        } else {
            // Regular AI chat — send to Nivdia
            showTypingIndicator();
            try {
                const res = await fetch(`${API_BASE}/v1/Nivdia`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ BOT: message })
                });

                removeTypingIndicator();

                if (!res.ok) {
                    throw new Error('Failed to get response');
                }

                const data = await res.json();
                const reply = data.Responses || 'Sorry, I could not process that.';
                addChatBubble(reply, 'bot');
            } catch (err) {
                removeTypingIndicator();
                addChatBubble('⚠️ Sorry, I\'m having trouble connecting. Please try again.', 'bot');
            }
        }

        chatSending = false;
        chatbotDOM.sendBtn.disabled = false;
        chatbotDOM.input.focus();
    }

    function clearChat() {
        chatbotDOM.messages.innerHTML = '';
        const welcome = document.createElement('div');
        welcome.className = 'chat-bubble bot';
        welcome.innerHTML = `
            <div class="bubble-content">👋 Hi! I'm your AI assistant. I can help you create todos!<br><br>💡 Try saying:<br>• <b>"Add task: Buy groceries by 2026-05-01"</b><br>• <b>"Create todo: Meeting with team"</b><br>• <b>"Remind me to submit report by tomorrow"</b><br><br>Or just ask me anything!</div>
            <div class="bubble-time">Just now</div>
        `;
        chatbotDOM.messages.appendChild(welcome);
    }

    function bindChatbotEvents() {
        chatbotDOM.fab.addEventListener('click', toggleChatbot);

        chatbotDOM.form.addEventListener('submit', (e) => {
            e.preventDefault();
            sendChatMessage(chatbotDOM.input.value);
        });

        chatbotDOM.clearBtn.addEventListener('click', clearChat);
    }

    // ======================================
    // INIT
    // ======================================

    function init() {
        initTheme();
        bindEvents();
        bindChatbotEvents();

        if (state.token && state.user) {
            showApp();
        } else {
            showAuth();
        }
    }

    // Boot
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
