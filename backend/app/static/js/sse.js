// SPDX-FileCopyrightText: 2026 Ivan Dodik
// SPDX-License-Identifier: AGPL-3.0-only

/**
 * Chess Tracker — SSE Client
 * Real-time event streaming with toast notifications
 */

class SSEClient {
  constructor() {
    this.eventSource = null;
    this.reconnectDelay = 3000;
    this.maxReconnectDelay = 30000;
    this.currentDelay = this.reconnectDelay;
    this._externalListeners = {};
    this.connect();
  }

  connect() {
    if (this.eventSource) {
      this.eventSource.close();
    }

    this.eventSource = new EventSource('/api/events');

    this.eventSource.addEventListener('game_created', (e) => {
      try {
        const data = JSON.parse(e.data);
        this.showNotification(
          `🎮 Новая партия: ${data.white_player_name || '?'} vs ${data.black_player_name || '?'} (${data.result || '?'})`,
          'info'
        );
      } catch (err) {
        console.error('SSE: failed to parse game_created', err);
      }
    });

    this.eventSource.addEventListener('game_updated', (e) => {
      try {
        const data = JSON.parse(e.data);
        this.showNotification(
          `🔄 Результат обновлён: ${data.white_player_name || '?'} vs ${data.black_player_name || '?'} — ${data.result || '?'}`,
          'warning'
        );
      } catch (err) {
        console.error('SSE: failed to parse game_updated', err);
      }
    });

    this.eventSource.addEventListener('rating_updated', (e) => {
      try {
        const data = JSON.parse(e.data);
        this.showNotification(
          `📈 Рейтинг обновлён: ${data.player_name || 'Игрок'} — ${data.new_rating || '?'}`,
          'success'
        );
      } catch (err) {
        console.error('SSE: failed to parse rating_updated', err);
      }
    });

    this.eventSource.addEventListener('ping', () => {
      // Keepalive — do nothing
    });

    this.eventSource.onopen = () => {
      this.currentDelay = this.reconnectDelay;  // Reset delay on successful connection
      this._reconnectExternalListeners();
    };

    this.eventSource.onerror = () => {
      console.warn('SSE: connection lost, reconnecting...');
      this.eventSource.close();
      this.eventSource = null;
      setTimeout(() => {
        this.currentDelay = Math.min(this.currentDelay * 1.5, this.maxReconnectDelay);
        this.connect();
      }, this.currentDelay);
    };
  }

  showNotification(message, type = 'info') {
    // Use the same flash message system from main.js
    if (typeof showFlash === 'function') {
      showFlash(message, type);
    }
  }

  on(eventName, callback) {
    if (!this._externalListeners[eventName]) {
      this._externalListeners[eventName] = [];
    }
    this._externalListeners[eventName].push(callback);
    // Register on current EventSource if connected
    if (this.eventSource) {
      this._addListener(this.eventSource, eventName, callback);
    }
  }

  _addListener(eventSource, eventName, callback) {
    eventSource.addEventListener(eventName, (e) => {
      try {
        const data = JSON.parse(e.data);
        callback(data);
      } catch (err) {
        console.error('SSE on(): failed to parse', eventName, err);
      }
    });
  }

  _reconnectExternalListeners() {
    if (!this.eventSource) return;
    for (const [eventName, callbacks] of Object.entries(this._externalListeners)) {
      for (const cb of callbacks) {
        this._addListener(this.eventSource, eventName, cb);
      }
    }
  }

  close() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

// Auto-initialize on DOM ready (singleton — guard against duplicate connections)
document.addEventListener('DOMContentLoaded', () => {
  if (!window.sseClient) {
    window.sseClient = new SSEClient();
  }
});

// After HTMX swap, ensure SSE connection is alive (only reconnect if closed)
document.addEventListener('htmx:afterSwap', () => {
  if (window.sseClient && !window.sseClient.eventSource) {
    window.sseClient.connect();
  }
});

// Disconnect SSE when leaving the app (prevents orphaned connections)
window.addEventListener('beforeunload', () => {
  if (window.sseClient) {
    window.sseClient.close();
  }
});
