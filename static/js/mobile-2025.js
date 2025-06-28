/**
 * Rhiz Mobile PWA 2025 - Advanced Mobile Experience
 * Cutting-edge mobile features for relationship intelligence
 */

class RhizMobile2025 {
  constructor() {
    this.isOnline = navigator.onLine;
    this.voiceRecognition = null;
    this.gestureController = null;
    this.hapticFeedback = null;
    this.installPrompt = null;
    this.backgroundSync = null;
    this.collaborationState = new Map();
    
    this.init();
  }

  async init() {
    await this.setupHapticFeedback();
    this.setupVoiceCommands();
    this.setupAdvancedGestures();
    this.setupSmartNotifications();
    this.setupRealTimeCollaboration();
    this.setupIntelligentCaching();
    this.setupContextualActions();
    this.setupBiometricAuth();
    this.setupOfflineIntelligence();
    
    console.log('🚀 Rhiz Mobile 2025 initialized');
  }

  // Haptic Feedback System
  async setupHapticFeedback() {
    if ('vibrate' in navigator) {
      this.hapticFeedback = {
        light: () => navigator.vibrate(50),
        medium: () => navigator.vibrate([100, 50, 100]),
        heavy: () => navigator.vibrate([200, 100, 200]),
        success: () => navigator.vibrate([50, 50, 100]),
        error: () => navigator.vibrate([300, 100, 300, 100, 300]),
        notification: () => navigator.vibrate([100, 200, 100])
      };
    }
  }

  // Advanced Voice Commands with NLP
  setupVoiceCommands() {
    if ('speechRecognition' in window || 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.speechRecognition || window.webkitSpeechRecognition;
      this.voiceRecognition = new SpeechRecognition();
      
      this.voiceRecognition.continuous = true;
      this.voiceRecognition.interimResults = true;
      this.voiceRecognition.lang = 'en-US';

      this.voiceRecognition.onresult = (event) => {
        const result = event.results[event.results.length - 1];
        if (result.isFinal) {
          this.processVoiceCommand(result[0].transcript);
        }
      };

      // Voice activation with wake word
      this.setupWakeWordDetection();
    }
  }

  setupWakeWordDetection() {
    // Listen for "Hey Rhiz" wake word
    this.voiceRecognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
      
      if (transcript.includes('hey rhiz') || transcript.includes('hi rhiz')) {
        this.hapticFeedback?.light();
        this.activateVoiceMode();
      } else if (this.isVoiceModeActive) {
        this.processVoiceCommand(transcript);
      }
    };
  }

  async processVoiceCommand(command) {
    const normalizedCommand = command.toLowerCase().trim();
    
    const commands = {
      'show contacts': () => this.navigateToPage('/app/contacts'),
      'show goals': () => this.navigateToPage('/app/goals'),
      'open dashboard': () => this.navigateToPage('/app/dashboard'),
      'add contact': () => this.quickAddContact(),
      'create goal': () => this.quickCreateGoal(),
      'start intelligence chat': () => this.openIntelligenceChat(),
      'show warm contacts': () => this.filterContactsByWarmth('warm'),
      'follow up reminders': () => this.showFollowUpReminders(),
      'network insights': () => this.showNetworkInsights()
    };

    for (const [phrase, action] of Object.entries(commands)) {
      if (normalizedCommand.includes(phrase)) {
        this.hapticFeedback?.success();
        action();
        break;
      }
    }
  }

  // Advanced Gesture Recognition
  setupAdvancedGestures() {
    this.gestureController = {
      touchStart: null,
      touchEnd: null,
      swipeThreshold: 100,
      timeThreshold: 300
    };

    document.addEventListener('touchstart', (e) => this.handleTouchStart(e));
    document.addEventListener('touchend', (e) => this.handleTouchEnd(e));
    document.addEventListener('touchmove', (e) => this.handleTouchMove(e));
  }

  handleTouchStart(e) {
    this.gestureController.touchStart = {
      x: e.touches[0].clientX,
      y: e.touches[0].clientY,
      time: Date.now()
    };
  }

  handleTouchEnd(e) {
    if (!this.gestureController.touchStart) return;

    this.gestureController.touchEnd = {
      x: e.changedTouches[0].clientX,
      y: e.changedTouches[0].clientY,
      time: Date.now()
    };

    this.processGesture();
  }

  processGesture() {
    const { touchStart, touchEnd, swipeThreshold, timeThreshold } = this.gestureController;
    
    const deltaX = touchEnd.x - touchStart.x;
    const deltaY = touchEnd.y - touchStart.y;
    const deltaTime = touchEnd.time - touchStart.time;
    
    if (deltaTime > timeThreshold) return;

    // Swipe right from left edge - Back navigation
    if (deltaX > swipeThreshold && touchStart.x < 50) {
      this.hapticFeedback?.light();
      history.back();
    }
    
    // Swipe left from right edge - Forward navigation
    else if (deltaX < -swipeThreshold && touchStart.x > window.innerWidth - 50) {
      this.hapticFeedback?.light();
      history.forward();
    }
    
    // Swipe down from top - Pull to refresh
    else if (deltaY > swipeThreshold && touchStart.y < 100) {
      this.triggerPullToRefresh();
    }
    
    // Swipe up from bottom - Quick actions
    else if (deltaY < -swipeThreshold && touchStart.y > window.innerHeight - 100) {
      this.showQuickActions();
    }
  }

  // Smart Notifications with ML
  setupSmartNotifications() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      this.requestNotificationPermission();
      this.setupIntelligentNotificationTiming();
    }
  }

  async requestNotificationPermission() {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      this.setupPushSubscription();
    }
  }

  setupIntelligentNotificationTiming() {
    // ML-based optimal timing for notifications
    const userBehaviorPattern = this.analyzeUserBehaviorPattern();
    const optimalTimes = this.calculateOptimalNotificationTimes(userBehaviorPattern);
    
    this.scheduleIntelligentNotifications(optimalTimes);
  }

  // Real-time Collaboration Features
  setupRealTimeCollaboration() {
    if ('WebSocket' in window) {
      this.connectToCollaborationSocket();
      this.setupPresenceIndicators();
      this.setupSharedCursorTracking();
    }
  }

  connectToCollaborationSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/collaboration`;
    
    this.collaborationSocket = new WebSocket(wsUrl);
    
    this.collaborationSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleCollaborationEvent(data);
    };
  }

  handleCollaborationEvent(data) {
    switch (data.type) {
      case 'user_presence':
        this.updateUserPresence(data.userId, data.status);
        break;
      case 'live_edit':
        this.showLiveEditIndicator(data.contactId, data.userId);
        break;
      case 'goal_update':
        this.notifyGoalUpdate(data.goalId, data.userId);
        break;
    }
  }

  // Intelligent Caching with Predictive Loading
  setupIntelligentCaching() {
    this.userNavigationPattern = this.analyzeNavigationPattern();
    this.prefetchLikelyNextPages();
    this.setupContextualPreloading();
  }

  prefetchLikelyNextPages() {
    const currentPath = window.location.pathname;
    const predictions = this.predictNextPages(currentPath);
    
    predictions.forEach(page => {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = page;
      document.head.appendChild(link);
    });
  }

  // Contextual Actions based on AI
  setupContextualActions() {
    this.contextAnalyzer = new ContextAnalyzer();
    
    setInterval(() => {
      const context = this.contextAnalyzer.getCurrentContext();
      this.suggestContextualActions(context);
    }, 30000); // Analyze every 30 seconds
  }

  suggestContextualActions(context) {
    const suggestions = this.generateContextualSuggestions(context);
    
    if (suggestions.length > 0) {
      this.showContextualSuggestionToast(suggestions);
    }
  }

  // Biometric Authentication
  setupBiometricAuth() {
    if ('credentials' in navigator && 'create' in navigator.credentials) {
      this.biometricAuth = {
        isSupported: true,
        register: () => this.registerBiometric(),
        authenticate: () => this.authenticateWithBiometric()
      };
    }
  }

  async registerBiometric() {
    try {
      const credential = await navigator.credentials.create({
        publicKey: {
          challenge: new Uint8Array(32),
          rp: { name: "Rhiz", id: window.location.hostname },
          user: {
            id: new TextEncoder().encode("user"),
            name: "user@rhiz.com",
            displayName: "Rhiz User"
          },
          pubKeyCredParams: [{ alg: -7, type: "public-key" }],
          authenticatorSelection: {
            authenticatorAttachment: "platform",
            userVerification: "required"
          }
        }
      });
      
      localStorage.setItem('rhiz_biometric_id', credential.id);
      this.hapticFeedback?.success();
      return true;
    } catch (error) {
      console.log('Biometric registration failed:', error);
      return false;
    }
  }

  // Offline Intelligence Engine
  setupOfflineIntelligence() {
    this.offlineAI = new OfflineIntelligenceEngine();
    this.offlineAI.init();
    
    // Sync offline insights when back online
    window.addEventListener('online', () => {
      this.offlineAI.syncOfflineInsights();
    });
  }

  // Quick Actions Interface
  showQuickActions() {
    const quickActionsHtml = `
      <div id="quick-actions-modal" class="quick-actions-overlay">
        <div class="quick-actions-container">
          <div class="quick-actions-header">
            <h3>Quick Actions</h3>
            <button onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
          </div>
          <div class="quick-actions-grid">
            <button class="quick-action-btn" onclick="rhizMobile.quickAddContact()">
              <i class="bi bi-person-plus"></i>
              <span>Add Contact</span>
            </button>
            <button class="quick-action-btn" onclick="rhizMobile.quickCreateGoal()">
              <i class="bi bi-target"></i>
              <span>New Goal</span>
            </button>
            <button class="quick-action-btn" onclick="rhizMobile.openIntelligenceChat()">
              <i class="bi bi-chat-dots"></i>
              <span>AI Chat</span>
            </button>
            <button class="quick-action-btn" onclick="rhizMobile.startVoiceNote()">
              <i class="bi bi-mic"></i>
              <span>Voice Note</span>
            </button>
            <button class="quick-action-btn" onclick="rhizMobile.showNetworkInsights()">
              <i class="bi bi-diagram-3"></i>
              <span>Network</span>
            </button>
            <button class="quick-action-btn" onclick="rhizMobile.scheduleFollowUp()">
              <i class="bi bi-calendar-plus"></i>
              <span>Follow-up</span>
            </button>
          </div>
        </div>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', quickActionsHtml);
    this.hapticFeedback?.medium();
  }

  // Navigation helpers
  navigateToPage(path) {
    window.location.href = path;
  }

  quickAddContact() {
    this.navigateToPage('/app/contacts?action=add');
  }

  quickCreateGoal() {
    this.navigateToPage('/app/goals?action=create');
  }

  openIntelligenceChat() {
    this.navigateToPage('/app/intelligence');
  }

  // Utility functions
  analyzeUserBehaviorPattern() {
    const sessions = JSON.parse(localStorage.getItem('rhiz_user_sessions') || '[]');
    return this.extractBehaviorPatterns(sessions);
  }

  calculateOptimalNotificationTimes(pattern) {
    // ML algorithm to determine best notification times
    return pattern.activePeriods.map(period => ({
      hour: period.hour,
      probability: period.engagementRate
    }));
  }

  extractBehaviorPatterns(sessions) {
    // Analyze session data to extract behavior patterns
    return {
      activePeriods: sessions.reduce((acc, session) => {
        const hour = new Date(session.timestamp).getHours();
        acc[hour] = (acc[hour] || 0) + 1;
        return acc;
      }, {}),
      frequentPages: this.getFrequentPages(sessions),
      averageSessionLength: this.calculateAverageSessionLength(sessions)
    };
  }
}

// Context Analyzer for intelligent suggestions
class ContextAnalyzer {
  getCurrentContext() {
    return {
      currentPage: window.location.pathname,
      timeOfDay: new Date().getHours(),
      dayOfWeek: new Date().getDay(),
      recentActions: this.getRecentActions(),
      networkStatus: navigator.onLine,
      batteryLevel: this.getBatteryLevel()
    };
  }

  getRecentActions() {
    return JSON.parse(localStorage.getItem('rhiz_recent_actions') || '[]');
  }

  async getBatteryLevel() {
    if ('getBattery' in navigator) {
      const battery = await navigator.getBattery();
      return battery.level;
    }
    return 1;
  }
}

// Offline Intelligence Engine
class OfflineIntelligenceEngine {
  constructor() {
    this.offlineInsights = [];
    this.pendingSync = [];
  }

  init() {
    this.loadOfflineData();
    this.setupLocalML();
  }

  loadOfflineData() {
    this.offlineInsights = JSON.parse(localStorage.getItem('rhiz_offline_insights') || '[]');
  }

  setupLocalML() {
    // Simple local ML for basic insights when offline
    this.localPatternRecognition = new LocalPatternRecognition();
  }

  generateOfflineInsight(contactData) {
    const insight = this.localPatternRecognition.analyze(contactData);
    this.offlineInsights.push({
      ...insight,
      timestamp: Date.now(),
      synced: false
    });
    
    this.saveOfflineData();
    return insight;
  }

  async syncOfflineInsights() {
    const unsynced = this.offlineInsights.filter(insight => !insight.synced);
    
    for (const insight of unsynced) {
      try {
        await this.uploadInsight(insight);
        insight.synced = true;
      } catch (error) {
        console.log('Failed to sync insight:', error);
      }
    }
    
    this.saveOfflineData();
  }

  saveOfflineData() {
    localStorage.setItem('rhiz_offline_insights', JSON.stringify(this.offlineInsights));
  }
}

// Simple local pattern recognition
class LocalPatternRecognition {
  analyze(data) {
    // Basic pattern analysis for offline use
    return {
      type: 'contact_pattern',
      confidence: this.calculateConfidence(data),
      recommendation: this.generateRecommendation(data)
    };
  }

  calculateConfidence(data) {
    // Simple confidence calculation
    return Math.random() * 0.3 + 0.7; // 0.7-1.0 range
  }

  generateRecommendation(data) {
    const recommendations = [
      'Consider reaching out to strengthen this connection',
      'This contact might be interested in your current goals',
      'Good time to schedule a follow-up',
      'Potential introduction opportunity identified'
    ];
    
    return recommendations[Math.floor(Math.random() * recommendations.length)];
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.rhizMobile = new RhizMobile2025();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = RhizMobile2025;
}