// SPDX-FileCopyrightText: 2026 Ivan Dodik
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Chess Tracker — Main JavaScript
 * HTMX initialization, Alpine.js components, auth helpers
 */

// ============================================================
// Auth Helpers
// ============================================================

const DEBUG = window.location.hostname === 'localhost';

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
// Alpine.js Components — register via alpine:init event
// Per Alpine docs: extension script (defer) BEFORE alpine CDN (defer) guarantees
// that alpine:init listener fires before Alpine scans the DOM.
// ============================================================

// Alpine docs: register extensions inside alpine:init (see https://alpinejs.dev/essentials/lifecycle)
document.addEventListener('alpine:init', () => {
  // Shared players store (avoids duplicate fetch in ratingChart + overallStatsChart)
  Alpine.store('players', {
    items: [],
    loaded: false,
    async load() {
      if (this.loaded) return;
      try {
        const resp = await fetch('/api/players?per_page=100', { headers: Auth.getAuthHeaders() });
        const data = await resp.json();
        this.items = data.items || [];
        this.loaded = true;
      } catch(e) {
        this.items = [];
      }
    }
  });

  // Auth state (for navbar)
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

  // Login form
  Alpine.data('loginForm', () => ({
    username: '',
    password: '',
    error: '',
    loading: false,

    async submit() {
      this.error = '';
      this.loading = true;

      if (DEBUG) console.log('[Login] Attempting login for user:', this.username);

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });

        if (DEBUG) console.log('[Login] Login response status:', response.status);

        if (!response.ok) {
          const data = await response.json();
          if (DEBUG) console.error('[Login] Login failed:', data);
          this.error = data.detail || 'Invalid credentials';
          this.loading = false;
          return;
        }

        const data = await response.json();
        if (DEBUG) console.log('[Login] Login successful, token received');

        // Save token to localStorage (cookie is set by server with HttpOnly flag)
        Auth.setToken(data.access_token);

        // Try to get user info, but don't block navigation if it fails
        try {
          const meResponse = await fetch('/api/auth/me', {
            headers: Auth.getAuthHeaders()
          });
          if (meResponse.ok) {
            const user = await meResponse.json();
            Auth.setUser(user);
            if (DEBUG) console.log('[Login] User info loaded:', user);
          } else {
            if (DEBUG) console.warn('[Login] Failed to load user info, status:', meResponse.status);
          }
        } catch (meErr) {
          console.warn('[Login] Error fetching user info:', meErr);
          // Don't fail the login if me endpoint fails
        }

        if (DEBUG) console.log('[Login] Redirecting to dashboard...');
        // Use a small delay to ensure localStorage is updated
        setTimeout(() => {
          window.location.href = '/';
        }, 100);
      } catch (err) {
        if (DEBUG) console.error('[Login] Network error:', err);
        this.error = 'Network error. Please try again.';
        this.loading = false;
      }
    }
  }));

  // Pagination
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

  // Rating chart
  Alpine.data('ratingChart', () => ({
    selectedPlayerId: '',
    players: [],
    chart: null,

    async init() {
      await Alpine.store('players').load();
      this.players = Alpine.store('players').items;
    },

    async loadChart() {
      if (!this.selectedPlayerId) return;
      this.destroyChart();
      try {
        const resp = await fetch(`/api/players/${this.selectedPlayerId}/rating-history`, { headers: Auth.getAuthHeaders() });
        const data = await resp.json();
        this.renderChart(data);
      } catch(e) {
        console.error('Failed to load rating history', e);
      }
    },

    renderChart(data) {
      const canvas = this.$refs.ratingCanvas;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const labels = data.map(r => new Date(r.date).toLocaleDateString('ru-RU'));
      const ratings = data.map(r => r.rating);

      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Рейтинг',
            data: ratings,
            borderColor: '#3498db',
            backgroundColor: 'rgba(52,152,219,0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 3,
            pointHoverRadius: 5,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: false,
              ticks: { precision: 0 }
            }
          }
        }
      });
    },

    destroyChart() {
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    }
  }));

  // Overall stats doughnut chart
  Alpine.data('overallStatsChart', () => ({
    selectedPlayerId: '',
    players: [],
    chart: null,

    async init() {
      await Alpine.store('players').load();
      this.players = Alpine.store('players').items;
    },

    async loadStats() {
      if (!this.selectedPlayerId) return;
      this.destroyChart();
      try {
        const resp = await fetch(`/api/stats/overall/${this.selectedPlayerId}`, { headers: Auth.getAuthHeaders() });
        const data = await resp.json();
        this.renderChart(data);
      } catch(e) {
        console.error('Failed to load stats', e);
      }
    },

    renderChart(data) {
      const canvas = this.$refs.statsCanvas;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      this.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Победы', 'Поражения', 'Ничьи'],
          datasets: [{
            data: [data.wins, data.losses, data.draws],
            backgroundColor: ['#27ae60', '#e74c3c', '#f39c12'],
            borderWidth: 2,
            borderColor: '#fff',
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { font: { size: 11 } }
            }
          }
        }
      });
    },

    destroyChart() {
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    }
  }));
});

// ============================================================
// HTMX Configuration
// NOTE: htmx:configRequest and htmx:responseError handlers are registered
// in base.html BEFORE htmx loads, to ensure the Authorization header is added
// to early HTMX requests (hx-trigger="load" elements processed via MutationObserver).
// ============================================================

// After HTMX swap, reinitialize components + Alpine.js re-scan
document.addEventListener('htmx:afterSwap', (event) => {
  initComponents();
  // Force Alpine.js to re-scan new DOM elements after HTMX swap
  if (window.Alpine) {
    Alpine.initTree(event.detail.target);
  }
});

// Initial component init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
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

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
