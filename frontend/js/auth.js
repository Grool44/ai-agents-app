const API_BASE = 'http://localhost:8000/api/v1';

function showToast(message, isError = false) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = 'toast' + (isError ? ' error' : '');
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

async function register(name, email, password) {
  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Ошибка регистрации');
    return data;
  } catch (error) {
    throw error;
  }
}

async function login(email, password) {
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Ошибка входа');
    localStorage.setItem('currentUser', JSON.stringify(data.user));
    return data;
  } catch (error) {
    throw error;
  }
}

function logout() {
  localStorage.removeItem('currentUser');
  window.location.href = '/login.html';
}

function getCurrentUser() {
  const user = localStorage.getItem('currentUser');
  return user ? JSON.parse(user) : null;
}

function requireAuth() {
  if (!getCurrentUser()) {
    window.location.href = '/login.html';
  }
}

async function trackVisit() {
  try {
    await fetch(`${API_BASE}/admin/track-visit`, { method: 'POST' });
  } catch (e) { console.log('Visit tracking error:', e); }
}

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      
      try {
        await login(email, password);
        showToast('Успешный вход!');
        window.location.href = '/dashboard.html';
      } catch (error) {
        showToast(error.message, true);
      }
    });
  }
  
  trackVisit();
});
