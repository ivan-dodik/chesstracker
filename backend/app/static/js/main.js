/**
 * Chess Tracker — Main JavaScript
 * HTMX initialization, Alpine.js components, auth helpers
 */

// ============================================================
// Auth Helpers
// ============================================================

const Auth = {
  getToken() {
    return localStorage.getItem('jwt_token');
  },

  setToken(token) {
    localStorage.setItem('jwt_token', token);
  },

  clearToken() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user');
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  getUser() {
    try {
      return JSON.parse(localStorage.getItem('user') || 'null');
    } catch {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  },

  isAdmin() {
    const user = this.getUser();
    return user && user.role === 'admin';
  },

  getAuthHeaders() {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  },

  logout() {
    this.clearToken();
    window.location.href = '/login';
  }
};

// ============================================================
// HTMX Configuration
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  // Auto-add Authorization header to all HTMX requests
  document.body.addEventListener('htmx:configRequest', (e) => {
    const token = Auth.getToken();
    if (token) {
      e.detail.headers['Authorization'] = `Bearer ${token}`;
    }
  });

  // Handle HTMX errors globally
  document.body.addEventListener('htmx:responseError', (e) => {
    if (e.detail.xhr.status === 401) {
      Auth.clearToken();
      window.location.href = '/login';
    }
  });

  // After HTMX swap, reinitialize components
  document.body.addEventListener('htmx:afterSwap', () => {
    initComponents();
  });

  // Initial component init
  initComponents();
});

// ============================================================
// Component Initialization
// ============================================================

function initComponents() {
  initFlashMessages();
  initMobileMenu();
}

// Flash message auto-dismiss
function initFlashMessages() {
  document.querySelectorAll('.flash-message').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(100%)';
      setTimeout(() => el.remove(), 300);
    }, 4000);
    el.addEventListener('click', () => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(100%)';
      setTimeout(() => el.remove(), 300);
    });
  });
}

// Mobile menu toggle
function initMobileMenu() {
  const toggle = document.querySelector('.navbar-toggle');
  const links = document.querySelector('.navbar-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
    });
  }
}

// ============================================================
// Alpine.js Components (if Alpine is loaded)
// ============================================================

if (typeof Alpine !== 'undefined') {
  // Auth state component
  Alpine.data('authState', () => ({
    isAuth: Auth.isAuthenticated(),
    user: Auth.getUser(),

    init() {
      this.$watch('isAuth', () => {
        this.user = Auth.getUser();
      });
    },

    logout() {
      Auth.logout();
    }
  }));

  // Login form component
  Alpine.data('loginForm', () => ({
    username: '',
    password: '',
    error: '',
    loading: false,

    async submit() {
      this.error = '';
      this.loading = true;

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });

        if (!response.ok) {
          const data = await response.json();
          this.error = data.detail || 'Invalid credentials';
          this.loading = false;
          return;
        }

        const data = await response.json();
        Auth.setToken(data.access_token);

        // Fetch user info
        const meResponse = await fetch('/api/auth/me', {
          headers: Auth.getAuthHeaders()
        });
        if (meResponse.ok) {
          const user = await meResponse.json();
          Auth.setUser(user);
        }

        window.location.href = '/';
      } catch (err) {
        this.error = 'Network error. Please try again.';
        this.loading = false;
      }
    }
  }));

  // Pagination component
  Alpine.data('pagination', () => ({
    page: 1,
    total: 0,
    perPage: 20,

    get totalPages() {
      return Math.ceil(this.total / this.perPage) || 1;
    },

    get pages() {
      const pages = [];
      const total = this.totalPages;
      const current = this.page;

      pages.push(1);

      let start = Math.max(2, current - 1);
      let end = Math.min(total - 1, current + 1);

      if (start > 2) pages.push('...');
      for (let i = start; i <= end; i++) pages.push(i);
      if (end < total - 1) pages.push('...');

      if (total > 1) pages.push(total);

      return pages;
    },

    goTo(page) {
      if (page < 1 || page > this.totalPages) return;
      this.page = page;
      this.$dispatch('page-change', { page });
    }
  }));
}

// ============================================================
// Utility Functions
// ============================================================

function showFlash(message, type = 'info') {
  const container = document.querySelector('.flash-messages');
  if (!container) return;

  const el = document.createElement('div');
  el.className = `flash-message flash-${type}`;
  el.textContent = message;
  container.appendChild(el);

  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(100%)';
    setTimeout(() => el.remove(), 300);
  }, 4000);

  el.addEventListener('click', () => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(100%)';
    setTimeout(() => el.remove(), 300);
  });
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

function formatRating(rating) {
  if (rating == null) return '—';
  return rating.toString();
}