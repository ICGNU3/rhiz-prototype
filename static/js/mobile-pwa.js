/**
 * Enhanced Mobile PWA Functionality for Rhiz
 * Advanced mobile-first features for the Progressive Web App
 */

class RhizMobilePWA {
  constructor() {
    this.isOnline = navigator.onLine;
    this.quickActionsExpanded = false;
    this.voiceRecording = false;
    this.pullToRefreshActive = false;
    this.swipeThreshold = 100;
    this.tapThreshold = 10;
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupPullToRefresh();
    this.setupQuickActions();
    this.setupVoiceCommands();
    this.setupSwipeGestures();
    this.setupPWAInstallPrompt();
    this.setupOfflineHandling();
    this.setupPushNotifications();
    this.setupMobileTouch();
  }

  setupEventListeners() {
    // Network status
    window.addEventListener('online', () => this.handleOnlineStatus(true));
    window.addEventListener('offline', () => this.handleOnlineStatus(false));
    
    // PWA lifecycle
    window.addEventListener('beforeinstallprompt', (e) => this.handleInstallPrompt(e));
    window.addEventListener('appinstalled', () => this.handleAppInstalled());
    
    // Background sync
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      this.setupBackgroundSync();
    }
    
    // Visibility change for performance
    document.addEventListener('visibilitychange', () => this.handleVisibilityChange());
  }

  setupPullToRefresh() {
    let startY = 0;
    let currentY = 0;
    let isPulling = false;
    
    const container = document.querySelector('.pull-to-refresh-container') || document.body;
    const indicator = this.createPullToRefreshIndicator();
    
    container.addEventListener('touchstart', (e) => {
      if (window.scrollY === 0) {
        startY = e.touches[0].clientY;
        isPulling = true;
      }
    }, { passive: true });
    
    container.addEventListener('touchmove', (e) => {
      if (!isPulling) return;
      
      currentY = e.touches[0].clientY;
      const diff = currentY - startY;
      
      if (diff > 0 && diff < 150) {
        indicator.style.top = `${-60 + (diff * 0.4)}px`;
        indicator.classList.add('pulling');
        
        if (diff > 80) {
          indicator.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
        } else {
          indicator.innerHTML = '<i class="bi bi-arrow-down"></i>';
        }
      }
    }, { passive: true });
    
    container.addEventListener('touchend', () => {
      if (isPulling && currentY - startY > 80) {
        this.triggerRefresh();
      }
      
      isPulling = false;
      indicator.style.top = '-60px';
      indicator.classList.remove('pulling');
    });
  }

  createPullToRefreshIndicator() {
    let indicator = document.querySelector('.pull-to-refresh-indicator');
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.className = 'pull-to-refresh-indicator';
      indicator.innerHTML = '<i class="bi bi-arrow-down"></i>';
      document.body.insertBefore(indicator, document.body.firstChild);
    }
    return indicator;
  }

  async triggerRefresh() {
    const indicator = document.querySelector('.pull-to-refresh-indicator');
    indicator.classList.add('refreshing');
    indicator.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
    
    try {
      // Refresh current page data
      if (window.location.pathname === '/') {
        await this.refreshDashboard();
      } else if (window.location.pathname.includes('/contacts')) {
        await this.refreshContacts();
      } else if (window.location.pathname.includes('/goals')) {
        await this.refreshGoals();
      } else {
        window.location.reload();
      }
      
      this.showToast('Content refreshed!', 'success');
    } catch (error) {
      this.showToast('Refresh failed', 'error');
    } finally {
      setTimeout(() => {
        indicator.classList.remove('refreshing');
        indicator.style.top = '-60px';
      }, 1000);
    }
  }

  setupQuickActions() {
    const quickActionsGroup = this.createQuickActionsGroup();
    
    // Load quick actions from server
    fetch('/api/mobile/quick-actions')
      .then(response => response.json())
      .then(data => {
        this.renderQuickActions(data.actions);
      })
      .catch(error => {
        console.error('Failed to load quick actions:', error);
      });
  }

  createQuickActionsGroup() {
    let quickActions = document.querySelector('.quick-action-group');
    if (!quickActions) {
      quickActions = document.createElement('div');
      quickActions.className = 'quick-action-group';
      
      // Main action button
      const mainBtn = document.createElement('button');
      mainBtn.className = 'quick-action-main-btn';
      mainBtn.innerHTML = '<i class="bi bi-plus"></i>';
      mainBtn.addEventListener('click', () => this.toggleQuickActions());
      
      const mainItem = document.createElement('div');
      mainItem.className = 'quick-action-item main';
      mainItem.appendChild(mainBtn);
      
      quickActions.appendChild(mainItem);
      document.body.appendChild(quickActions);
    }
    return quickActions;
  }

  renderQuickActions(actions) {
    const quickActions = document.querySelector('.quick-action-group');
    
    // Remove existing action items (except main)
    const existingItems = quickActions.querySelectorAll('.quick-action-item:not(.main)');
    existingItems.forEach(item => item.remove());
    
    // Add new action items
    actions.forEach((action, index) => {
      const item = document.createElement('div');
      item.className = 'quick-action-item';
      item.style.transitionDelay = `${(index + 1) * 0.1}s`;
      
      if (action.url) {
        const link = document.createElement('a');
        link.href = action.url;
        link.className = 'quick-action-btn';
        link.innerHTML = `<i class="bi bi-${action.icon}"></i>`;
        item.appendChild(link);
      } else if (action.action) {
        const btn = document.createElement('button');
        btn.className = 'quick-action-btn';
        btn.innerHTML = `<i class="bi bi-${action.icon}"></i>`;
        btn.addEventListener('click', () => this.handleQuickAction(action.action));
        item.appendChild(btn);
      }
      
      const label = document.createElement('span');
      label.className = 'quick-action-label';
      label.textContent = action.label;
      
      if (action.badge) {
        const badge = document.createElement('span');
        badge.className = 'badge bg-danger ms-2';
        badge.textContent = action.badge;
        label.appendChild(badge);
      }
      
      item.appendChild(label);
      quickActions.insertBefore(item, quickActions.firstChild);
    });
  }

  toggleQuickActions() {
    const quickActions = document.querySelector('.quick-action-group');
    const mainBtn = quickActions.querySelector('.quick-action-main-btn');
    
    this.quickActionsExpanded = !this.quickActionsExpanded;
    
    if (this.quickActionsExpanded) {
      quickActions.classList.add('expanded');
      mainBtn.classList.add('expanded');
    } else {
      quickActions.classList.remove('expanded');
      mainBtn.classList.remove('expanded');
    }
  }

  handleQuickAction(action) {
    switch (action) {
      case 'voice_record':
        this.startVoiceRecording();
        break;
      default:
        console.log('Unknown quick action:', action);
    }
  }

  setupVoiceCommands() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.log('Speech recognition not supported');
      return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.lang = 'en-US';
    
    this.recognition.onstart = () => {
      this.showVoiceIndicator(true);
    };
    
    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      this.processVoiceCommand(transcript);
    };
    
    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      this.showVoiceIndicator(false);
      this.showToast('Voice recognition failed', 'error');
    };
    
    this.recognition.onend = () => {
      this.showVoiceIndicator(false);
      this.voiceRecording = false;
    };
  }

  startVoiceRecording() {
    if (this.voiceRecording || !this.recognition) return;
    
    this.voiceRecording = true;
    this.toggleQuickActions(); // Close quick actions
    this.recognition.start();
  }

  showVoiceIndicator(show) {
    let indicator = document.querySelector('.voice-indicator');
    
    if (show) {
      if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'voice-indicator';
        indicator.innerHTML = 'Listening...';
        document.body.appendChild(indicator);
      }
      indicator.classList.add('active');
    } else if (indicator) {
      indicator.classList.remove('active');
      setTimeout(() => {
        if (indicator && indicator.parentNode) {
          indicator.parentNode.removeChild(indicator);
        }
      }, 300);
    }
  }

  processVoiceCommand(transcript) {
    const command = transcript.toLowerCase();
    
    if (command.includes('add contact') || command.includes('new contact')) {
      window.location.href = '/contacts/new';
    } else if (command.includes('new goal') || command.includes('create goal')) {
      window.location.href = '/goals/new';
    } else if (command.includes('dashboard') || command.includes('home')) {
      window.location.href = '/';
    } else if (command.includes('contacts')) {
      window.location.href = '/contacts';
    } else if (command.includes('goals')) {
      window.location.href = '/goals';
    } else {
      // Send to voice memo processing
      this.sendVoiceMemo(transcript);
    }
    
    this.showToast(`Voice command: "${transcript}"`, 'info');
  }

  async sendVoiceMemo(transcript) {
    try {
      const response = await fetch('/api/mobile/voice-memo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          transcript: transcript,
          timestamp: new Date().toISOString()
        })
      });
      
      const data = await response.json();
      
      if (data.success && data.contact_info) {
        // Navigate to new contact form with pre-filled info
        const params = new URLSearchParams(data.contact_info);
        window.location.href = `/contacts/new?${params.toString()}`;
      }
    } catch (error) {
      console.error('Voice memo processing failed:', error);
      this.showToast('Failed to process voice memo', 'error');
    }
  }

  setupSwipeGestures() {
    let startX = 0;
    let startY = 0;
    let endX = 0;
    let endY = 0;
    
    document.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    }, { passive: true });
    
    document.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].clientX;
      endY = e.changedTouches[0].clientY;
      
      const diffX = endX - startX;
      const diffY = endY - startY;
      
      // Only process significant horizontal swipes
      if (Math.abs(diffX) > this.swipeThreshold && Math.abs(diffY) < this.swipeThreshold) {
        if (diffX > 0) {
          this.handleSwipeRight();
        } else {
          this.handleSwipeLeft();
        }
      }
    });
  }

  handleSwipeRight() {
    // Swipe right: Go back or show navigation
    if (window.history.length > 1) {
      this.showSwipeIndicator('left', 'Back');
      setTimeout(() => window.history.back(), 300);
    }
  }

  handleSwipeLeft() {
    // Swipe left: Show quick actions or next page
    if (!this.quickActionsExpanded) {
      this.showSwipeIndicator('right', 'Quick Actions');
      setTimeout(() => this.toggleQuickActions(), 300);
    }
  }

  showSwipeIndicator(side, text) {
    const indicator = document.createElement('div');
    indicator.className = `swipe-indicator ${side}`;
    indicator.textContent = text;
    document.body.appendChild(indicator);
    
    setTimeout(() => indicator.classList.add('show'), 10);
    
    setTimeout(() => {
      indicator.classList.remove('show');
      setTimeout(() => {
        if (indicator.parentNode) {
          indicator.parentNode.removeChild(indicator);
        }
      }, 300);
    }, 1000);
  }

  setupPWAInstallPrompt() {
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      
      // Track install prompt shown
      fetch('/api/pwa/install-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'shown' })
      });
      
      this.showInstallBanner(deferredPrompt);
    });
  }

  showInstallBanner(deferredPrompt) {
    if (this.isStandalone()) return;
    
    const banner = document.createElement('div');
    banner.className = 'install-banner';
    banner.innerHTML = `
      <div class="d-flex align-items-center justify-content-between">
        <div>
          <strong>Install Rhiz</strong>
          <div class="small">Get quick access and offline support</div>
        </div>
        <div>
          <button class="btn btn-sm btn-primary me-2" id="install-btn">Install</button>
          <button class="btn btn-sm btn-outline-secondary" id="dismiss-btn">Later</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(banner);
    setTimeout(() => banner.classList.add('show'), 100);
    
    document.getElementById('install-btn').addEventListener('click', async () => {
      deferredPrompt.prompt();
      const choiceResult = await deferredPrompt.userChoice;
      
      fetch('/api/pwa/install-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: choiceResult.outcome })
      });
      
      this.hideInstallBanner(banner);
    });
    
    document.getElementById('dismiss-btn').addEventListener('click', () => {
      fetch('/api/pwa/install-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'dismissed' })
      });
      
      this.hideInstallBanner(banner);
    });
  }

  hideInstallBanner(banner) {
    banner.classList.remove('show');
    setTimeout(() => {
      if (banner.parentNode) {
        banner.parentNode.removeChild(banner);
      }
    }, 300);
  }

  setupOfflineHandling() {
    const offlineBanner = document.createElement('div');
    offlineBanner.className = 'offline-banner';
    offlineBanner.textContent = 'You\'re offline. Some features may be limited.';
    document.body.appendChild(offlineBanner);
    
    this.handleOnlineStatus(navigator.onLine);
  }

  handleOnlineStatus(isOnline) {
    this.isOnline = isOnline;
    const banner = document.querySelector('.offline-banner');
    
    if (isOnline) {
      banner.classList.remove('show');
      this.syncOfflineData();
    } else {
      banner.classList.add('show');
    }
  }

  async syncOfflineData() {
    try {
      const response = await fetch('/api/mobile/background-sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'all' })
      });
      
      const data = await response.json();
      
      if (data.success && data.synced_items > 0) {
        this.showToast(`Synced ${data.synced_items} items`, 'success');
      }
    } catch (error) {
      console.error('Background sync failed:', error);
    }
  }

  setupPushNotifications() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      this.requestNotificationPermission();
    }
  }

  async requestNotificationPermission() {
    const permission = await Notification.requestPermission();
    
    if (permission === 'granted') {
      this.subscribeToPushNotifications();
    }
  }

  async subscribeToPushNotifications() {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(this.vapidPublicKey)
      });
      
      await fetch('/api/pwa/push-subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription.toJSON())
      });
      
    } catch (error) {
      console.error('Push subscription failed:', error);
    }
  }

  setupMobileTouch() {
    // Improve touch responsiveness
    document.addEventListener('touchstart', () => {}, { passive: true });
    
    // Prevent zoom on double tap for better UX
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
      const now = new Date().getTime();
      if (now - lastTouchEnd <= 300) {
        e.preventDefault();
      }
      lastTouchEnd = now;
    }, false);
    
    // Optimize button touches
    document.addEventListener('touchstart', (e) => {
      if (e.target.matches('button, .btn, a')) {
        e.target.style.transform = 'scale(0.95)';
      }
    }, { passive: true });
    
    document.addEventListener('touchend', (e) => {
      if (e.target.matches('button, .btn, a')) {
        setTimeout(() => {
          e.target.style.transform = '';
        }, 100);
      }
    });
  }

  setupBackgroundSync() {
    navigator.serviceWorker.ready.then(registration => {
      return registration.sync.register('background-sync');
    }).catch(error => {
      console.error('Background sync registration failed:', error);
    });
  }

  handleVisibilityChange() {
    if (document.hidden) {
      // App became inactive
      this.saveAppState();
    } else {
      // App became active
      this.restoreAppState();
      this.checkForUpdates();
    }
  }

  saveAppState() {
    const state = {
      timestamp: Date.now(),
      pathname: window.location.pathname,
      scroll: window.scrollY
    };
    
    localStorage.setItem('rhiz_app_state', JSON.stringify(state));
  }

  restoreAppState() {
    const savedState = localStorage.getItem('rhiz_app_state');
    if (savedState) {
      const state = JSON.parse(savedState);
      
      // Restore scroll position if on same page
      if (state.pathname === window.location.pathname) {
        window.scrollTo(0, state.scroll);
      }
    }
  }

  async checkForUpdates() {
    try {
      const response = await fetch('/api/mobile/sync-status');
      const data = await response.json();
      
      if (!data.synced) {
        this.showToast('Checking for updates...', 'info');
        this.syncOfflineData();
      }
    } catch (error) {
      console.error('Update check failed:', error);
    }
  }

  showToast(message, type = 'info') {
    let container = document.querySelector('.mobile-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'mobile-toast-container';
      document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `mobile-toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 3000);
  }

  isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone ||
           document.referrer.includes('android-app://');
  }

  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // Data refresh methods
  async refreshDashboard() {
    const response = await fetch(window.location.href);
    const html = await response.text();
    const parser = new DOMParser();
    const newDoc = parser.parseFromString(html, 'text/html');
    
    // Update main content
    const mainContent = document.querySelector('.main-content');
    const newMainContent = newDoc.querySelector('.main-content');
    
    if (mainContent && newMainContent) {
      mainContent.innerHTML = newMainContent.innerHTML;
    }
  }

  async refreshContacts() {
    // Implement contact list refresh
    window.location.reload();
  }

  async refreshGoals() {
    // Implement goals list refresh
    window.location.reload();
  }
}

// Initialize mobile PWA when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.rhizMobilePWA = new RhizMobilePWA();
  });
} else {
  window.rhizMobilePWA = new RhizMobilePWA();
}

// Export for global access
window.RhizMobilePWA = RhizMobilePWA;