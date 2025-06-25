// Progressive Web App functionality for Founder Network AI
class FounderNetworkApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.offlineDB = null;
        this.notificationPermission = 'default';
        
        this.init();
    }
    
    async init() {
        // Register service worker
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/sw.js');
                console.log('Service Worker registered:', registration);
                
                // Handle updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
            } catch (error) {
                console.log('Service Worker registration failed:', error);
            }
        }
        
        // Initialize offline database
        await this.initOfflineDB();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Request notification permission
        await this.requestNotificationPermission();
        
        // Setup push notifications
        this.setupPushNotifications();
        
        // Initialize mobile optimizations
        this.initMobileOptimizations();
        
        // Check for offline data to sync
        this.checkOfflineSync();
    }
    
    async initOfflineDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('FounderNetworkOffline', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.offlineDB = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                if (!db.objectStoreNames.contains('contacts')) {
                    const contactStore = db.createObjectStore('contacts', { keyPath: 'id' });
                    contactStore.createIndex('name', 'name', { unique: false });
                    contactStore.createIndex('company', 'company', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('interactions')) {
                    const interactionStore = db.createObjectStore('interactions', { keyPath: 'id' });
                    interactionStore.createIndex('contactId', 'contactId', { unique: false });
                    interactionStore.createIndex('date', 'date', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('goals')) {
                    const goalStore = db.createObjectStore('goals', { keyPath: 'id' });
                    goalStore.createIndex('title', 'title', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('notifications')) {
                    const notificationStore = db.createObjectStore('notifications', { keyPath: 'id' });
                    notificationStore.createIndex('dueDate', 'dueDate', { unique: false });
                }
            };
        });
    }
    
    setupEventListeners() {
        // Online/offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showConnectionStatus('online');
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showConnectionStatus('offline');
        });
        
        // Form submissions for offline support
        document.addEventListener('submit', (e) => {
            if (!this.isOnline && e.target.matches('.offline-support')) {
                e.preventDefault();
                this.handleOfflineFormSubmission(e.target);
            }
        });
        
        // PWA install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.showInstallPrompt(e);
        });
        
        // App shortcuts
        this.setupKeyboardShortcuts();
        
        // Touch gestures for mobile
        this.setupTouchGestures();
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for quick search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openQuickSearch();
            }
            
            // Ctrl/Cmd + N for new contact
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.openNewContactModal();
            }
            
            // Ctrl/Cmd + G for new goal
            if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
                e.preventDefault();
                this.openNewGoalModal();
            }
        });
    }
    
    setupTouchGestures() {
        let touchStartX = 0;
        let touchStartY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            
            // Swipe left to open quick actions
            if (deltaX < -100 && Math.abs(deltaY) < 50) {
                this.openQuickActions();
            }
            
            // Swipe right to go back
            if (deltaX > 100 && Math.abs(deltaY) < 50) {
                window.history.back();
            }
            
            // Swipe down to refresh
            if (deltaY > 100 && Math.abs(deltaX) < 50 && window.scrollY === 0) {
                this.pullToRefresh();
            }
        });
    }
    
    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            this.notificationPermission = permission;
            
            if (permission === 'granted') {
                this.scheduleFollowUpNotifications();
            }
        }
    }
    
    async setupPushNotifications() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array(
                        'your-vapid-public-key-here' // Replace with actual VAPID key
                    )
                });
                
                // Send subscription to server
                await this.sendSubscriptionToServer(subscription);
            } catch (error) {
                console.log('Push notification setup failed:', error);
            }
        }
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
    
    async sendSubscriptionToServer(subscription) {
        try {
            await fetch('/api/push-subscription', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subscription)
            });
        } catch (error) {
            console.log('Failed to send subscription to server:', error);
        }
    }
    
    initMobileOptimizations() {
        // Viewport height fix for mobile browsers
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVH();
        window.addEventListener('resize', setVH);
        
        // Prevent zoom on input focus
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                if (input.getAttribute('data-prevent-zoom') !== 'false') {
                    input.style.fontSize = '16px';
                }
            });
        });
        
        // Optimize scroll performance
        document.addEventListener('touchmove', (e) => {
            if (e.target.closest('.scroll-container')) {
                e.stopPropagation();
            }
        }, { passive: true });
        
        // Add loading states for better UX
        this.addLoadingStates();
    }
    
    addLoadingStates() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('button[type="submit"], .btn-submit');
            if (button && !button.disabled) {
                button.classList.add('loading');
                button.disabled = true;
                
                setTimeout(() => {
                    button.classList.remove('loading');
                    button.disabled = false;
                }, 3000);
            }
        });
    }
    
    showConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status') || 
                             this.createConnectionStatusElement();
        
        statusElement.textContent = status === 'online' ? 'Back online' : 'Offline mode';
        statusElement.className = `connection-status ${status}`;
        statusElement.style.display = 'block';
        
        setTimeout(() => {
            statusElement.style.display = 'none';
        }, 3000);
    }
    
    createConnectionStatusElement() {
        const element = document.createElement('div');
        element.id = 'connection-status';
        element.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 9999;
            display: none;
        `;
        document.body.appendChild(element);
        return element;
    }
    
    showInstallPrompt(e) {
        const installBanner = document.createElement('div');
        installBanner.innerHTML = `
            <div class="install-banner">
                <div class="install-content">
                    <strong>Install Founder Network AI</strong>
                    <p>Get quick access to your network from your home screen</p>
                </div>
                <div class="install-actions">
                    <button class="btn btn-primary btn-sm" id="install-app">Install</button>
                    <button class="btn btn-secondary btn-sm" id="dismiss-install">Later</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(installBanner);
        
        document.getElementById('install-app').addEventListener('click', () => {
            e.prompt();
            installBanner.remove();
        });
        
        document.getElementById('dismiss-install').addEventListener('click', () => {
            installBanner.remove();
        });
    }
    
    showUpdateNotification() {
        const updateNotification = document.createElement('div');
        updateNotification.innerHTML = `
            <div class="update-notification">
                <span>New version available</span>
                <button class="btn btn-outline-primary btn-sm" id="update-app">Update</button>
            </div>
        `;
        
        document.body.appendChild(updateNotification);
        
        document.getElementById('update-app').addEventListener('click', () => {
            window.location.reload();
        });
    }
    
    // Offline functionality
    async handleOfflineFormSubmission(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        data.id = Date.now().toString();
        data.offline = true;
        data.timestamp = new Date().toISOString();
        
        const action = form.action || window.location.pathname;
        
        if (action.includes('contact')) {
            await this.saveOfflineContact(data);
            this.showOfflineMessage('Contact saved offline. Will sync when online.');
        } else if (action.includes('interaction')) {
            await this.saveOfflineInteraction(data);
            this.showOfflineMessage('Interaction logged offline. Will sync when online.');
        }
        
        // Register background sync
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            const registration = await navigator.serviceWorker.ready;
            await registration.sync.register('contact-sync');
        }
    }
    
    async saveOfflineContact(contactData) {
        const transaction = this.offlineDB.transaction(['contacts'], 'readwrite');
        const store = transaction.objectStore('contacts');
        await store.add(contactData);
    }
    
    async saveOfflineInteraction(interactionData) {
        const transaction = this.offlineDB.transaction(['interactions'], 'readwrite');
        const store = transaction.objectStore('interactions');
        await store.add(interactionData);
    }
    
    showOfflineMessage(message) {
        const toast = document.createElement('div');
        toast.className = 'offline-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #f39c12;
            color: white;
            padding: 12px 20px;
            border-radius: 5px;
            z-index: 9999;
        `;
        
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }
    
    async syncOfflineData() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            const registration = await navigator.serviceWorker.ready;
            await registration.sync.register('contact-sync');
            await registration.sync.register('interaction-sync');
        }
    }
    
    async checkOfflineSync() {
        if (this.offlineDB) {
            const contactTransaction = this.offlineDB.transaction(['contacts'], 'readonly');
            const contactStore = contactTransaction.objectStore('contacts');
            const contactCount = await contactStore.count();
            
            const interactionTransaction = this.offlineDB.transaction(['interactions'], 'readonly');
            const interactionStore = interactionTransaction.objectStore('interactions');
            const interactionCount = await interactionStore.count();
            
            if (contactCount > 0 || interactionCount > 0) {
                this.showSyncPrompt(contactCount + interactionCount);
            }
        }
    }
    
    showSyncPrompt(itemCount) {
        const syncPrompt = document.createElement('div');
        syncPrompt.innerHTML = `
            <div class="sync-prompt">
                <span>${itemCount} items waiting to sync</span>
                <button class="btn btn-primary btn-sm" id="sync-now">Sync Now</button>
            </div>
        `;
        
        document.body.appendChild(syncPrompt);
        
        document.getElementById('sync-now').addEventListener('click', () => {
            this.syncOfflineData();
            syncPrompt.remove();
        });
    }
    
    // Quick actions
    openQuickSearch() {
        // Implement quick search modal
        console.log('Opening quick search...');
    }
    
    openNewContactModal() {
        // Navigate to new contact page or open modal
        window.location.href = '/contacts/new';
    }
    
    openNewGoalModal() {
        // Navigate to new goal page or open modal
        window.location.href = '/goals/new';
    }
    
    openQuickActions() {
        // Show floating action menu
        console.log('Opening quick actions...');
    }
    
    pullToRefresh() {
        // Implement pull to refresh
        window.location.reload();
    }
    
    // Notification scheduling
    async scheduleFollowUpNotifications() {
        try {
            const response = await fetch('/api/follow-ups-due');
            const followUps = await response.json();
            
            for (const followUp of followUps) {
                this.scheduleNotification(followUp);
            }
        } catch (error) {
            console.log('Failed to schedule notifications:', error);
        }
    }
    
    scheduleNotification(followUp) {
        if (this.notificationPermission === 'granted') {
            const dueDate = new Date(followUp.due_date);
            const now = new Date();
            const timeDiff = dueDate.getTime() - now.getTime();
            
            if (timeDiff > 0 && timeDiff < 24 * 60 * 60 * 1000) { // Within 24 hours
                setTimeout(() => {
                    new Notification('Follow-up Due', {
                        body: `Follow up with ${followUp.contact_name}`,
                        icon: '/static/icons/icon-192x192.png',
                        badge: '/static/icons/icon-72x72.png',
                        data: { url: `/contacts/${followUp.contact_id}` }
                    });
                }, timeDiff);
            }
        }
    }
}

// Voice command integration for Telegram
class VoiceCommands {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.setupRecognition();
        }
    }
    
    setupRecognition() {
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.toLowerCase();
            this.processVoiceCommand(transcript);
        };
        
        this.recognition.onerror = (event) => {
            console.log('Speech recognition error:', event.error);
            this.isListening = false;
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
        };
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            this.isListening = true;
            this.recognition.start();
        }
    }
    
    processVoiceCommand(transcript) {
        console.log('Voice command:', transcript);
        
        // Send to Telegram bot for processing
        if (transcript.includes('show') && transcript.includes('contacts')) {
            window.location.href = '/contacts';
        } else if (transcript.includes('add') && transcript.includes('contact')) {
            window.location.href = '/contacts/new';
        } else if (transcript.includes('analytics') || transcript.includes('stats')) {
            window.location.href = '/analytics';
        } else if (transcript.includes('follow up') || transcript.includes('follow-up')) {
            window.location.href = '/crm/pipeline';
        } else {
            // Send to Telegram for natural language processing
            this.sendToTelegram(transcript);
        }
    }
    
    async sendToTelegram(message) {
        try {
            await fetch('/api/telegram-command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: message })
            });
        } catch (error) {
            console.log('Failed to send voice command to Telegram:', error);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.founderNetworkApp = new FounderNetworkApp();
    window.voiceCommands = new VoiceCommands();
    
    // Add voice command button
    const voiceButton = document.createElement('button');
    voiceButton.innerHTML = '<i class="bi bi-mic"></i>';
    voiceButton.className = 'btn btn-floating voice-btn';
    voiceButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: #3b82f6;
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
    `;
    
    voiceButton.addEventListener('click', () => {
        window.voiceCommands.startListening();
        voiceButton.classList.add('listening');
        setTimeout(() => voiceButton.classList.remove('listening'), 3000);
    });
    
    document.body.appendChild(voiceButton);
});