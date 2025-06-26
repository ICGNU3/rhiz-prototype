/**
 * Background Gamification Engine
 * Operates invisibly to support users through subtle feedback and motivation
 */

class BackgroundGamificationEngine {
    constructor() {
        this.settings = {
            mode: 'motivated', // motivated, clean, quiet
            toastEnabled: true,
            glowEffects: true,
            soundEnabled: false
        };
        
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
        this.injectStyles();
        this.createToastContainer();
    }

    loadSettings() {
        const saved = localStorage.getItem('gamification-settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
    }

    saveSettings() {
        localStorage.setItem('gamification-settings', JSON.stringify(this.settings));
    }

    setupEventListeners() {
        // Listen for custom gamification events
        document.addEventListener('gamification:xp-earned', (e) => {
            this.handleXPEarned(e.detail);
        });

        document.addEventListener('gamification:level-up', (e) => {
            this.handleLevelUp(e.detail);
        });

        document.addEventListener('gamification:quest-complete', (e) => {
            this.handleQuestComplete(e.detail);
        });

        document.addEventListener('gamification:streak-continue', (e) => {
            this.handleStreakContinue(e.detail);
        });
    }

    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .gamification-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                transform: translateX(120%);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                border-left: 4px solid #ffd700;
                backdrop-filter: blur(10px);
            }

            .gamification-toast.show {
                transform: translateX(0);
            }

            .gamification-toast.hide {
                transform: translateX(120%);
                opacity: 0;
            }

            .gamification-toast-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .gamification-toast-icon {
                font-size: 24px;
                flex-shrink: 0;
            }

            .gamification-toast-text {
                flex: 1;
            }

            .gamification-toast-title {
                font-weight: 600;
                margin: 0 0 4px 0;
                font-size: 14px;
            }

            .gamification-toast-message {
                margin: 0;
                font-size: 13px;
                opacity: 0.9;
            }

            .gamification-toast-xp {
                background: rgba(255,255,255,0.2);
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }

            .goal-linked-glow {
                animation: goalLinkedPulse 2s ease-in-out;
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            }

            @keyframes goalLinkedPulse {
                0%, 100% { box-shadow: 0 0 5px rgba(255, 215, 0, 0.3); }
                50% { box-shadow: 0 0 25px rgba(255, 215, 0, 0.6); }
            }

            .level-up-celebration {
                animation: levelUpCelebration 3s ease-out;
            }

            @keyframes levelUpCelebration {
                0% { transform: scale(1); }
                15% { transform: scale(1.05); }
                30% { transform: scale(1); }
                100% { transform: scale(1); }
            }

            .xp-counter {
                position: relative;
                overflow: hidden;
            }

            .xp-counter::after {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,215,0,0.4), transparent);
                animation: xpShine 1.5s ease-out;
            }

            @keyframes xpShine {
                0% { left: -100%; }
                100% { left: 100%; }
            }

            .subtle-motivation-badge {
                display: inline-block;
                background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                margin-left: 8px;
                opacity: 0.8;
            }

            .quest-hint {
                background: rgba(103, 126, 234, 0.1);
                border-left: 3px solid #677eea;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 13px;
                margin: 8px 0;
                opacity: 0;
                animation: questHintFadeIn 0.5s ease-out 0.5s forwards;
            }

            @keyframes questHintFadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .micro-progress-ring {
                width: 20px;
                height: 20px;
                position: relative;
                display: inline-block;
                margin-left: 8px;
            }

            .micro-progress-ring svg {
                width: 20px;
                height: 20px;
                transform: rotate(-90deg);
            }

            .micro-progress-ring circle {
                fill: none;
                stroke-width: 2;
            }

            .micro-progress-ring .bg {
                stroke: rgba(255,255,255,0.1);
            }

            .micro-progress-ring .progress {
                stroke: #ffd700;
                stroke-linecap: round;
                transition: stroke-dashoffset 0.5s ease;
            }
        `;
        document.head.appendChild(style);
    }

    createToastContainer() {
        // Wait for document body to be available
        if (document.body && !document.getElementById('gamification-toast-container')) {
            const container = document.createElement('div');
            container.id = 'gamification-toast-container';
            document.body.appendChild(container);
        } else if (!document.body) {
            // Retry when body is available
            setTimeout(() => this.createToastContainer(), 100);
        }
    }

    triggerFeedback(data) {
        if (this.settings.mode === 'quiet') return;

        const actions = {
            toast: () => this.showToast(data),
            glow: () => this.addGlowEffect(data.element),
            celebration: () => this.showCelebration(data),
            badge: () => this.addMotivationBadge(data),
            progress: () => this.updateProgressRing(data)
        };

        if (actions[data.type]) {
            actions[data.type]();
        }
    }

    showToast(data) {
        if (!this.settings.toastEnabled || this.settings.mode === 'clean') return;

        const toast = document.createElement('div');
        toast.className = 'gamification-toast';
        
        const icon = this.getIconForAction(data.action);
        const title = this.getTitleForAction(data.action);
        
        toast.innerHTML = `
            <div class="gamification-toast-content">
                <div class="gamification-toast-icon">${icon}</div>
                <div class="gamification-toast-text">
                    <div class="gamification-toast-title">${title}</div>
                    <div class="gamification-toast-message">${data.message}</div>
                </div>
                ${data.xpGained ? `<div class="gamification-toast-xp">+${data.xpGained} XP</div>` : ''}
            </div>
        `;

        document.getElementById('gamification-toast-container').appendChild(toast);

        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);

        // Hide toast after delay
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 400);
        }, data.duration || 4000);
    }

    getIconForAction(action) {
        const icons = {
            contact_added: '👤',
            goal_created: '🎯',
            email_sent: '📧',
            follow_up: '🔄',
            relationship_created: '🤝',
            conference_contact: '📅',
            level_up: '🏆',
            quest_complete: '✨',
            streak_continue: '🔥'
        };
        return icons[action] || '🌟';
    }

    getTitleForAction(action) {
        const titles = {
            contact_added: 'Contact Added',
            goal_created: 'Goal Set',
            email_sent: 'Email Sent',
            follow_up: 'Follow-up Complete',
            relationship_created: 'Connection Made',
            conference_contact: 'Conference Contact',
            level_up: 'Level Up!',
            quest_complete: 'Quest Complete',
            streak_continue: 'Streak Maintained'
        };
        return titles[action] || 'Progress Made';
    }

    addGlowEffect(element) {
        if (!this.settings.glowEffects || this.settings.mode !== 'motivated') return;
        
        if (element) {
            element.classList.add('goal-linked-glow');
            setTimeout(() => element.classList.remove('goal-linked-glow'), 2000);
        }
    }

    showCelebration(data) {
        if (this.settings.mode !== 'motivated') return;
        
        const element = data.element || document.body;
        element.classList.add('level-up-celebration');
        setTimeout(() => element.classList.remove('level-up-celebration'), 3000);
    }

    addMotivationBadge(data) {
        if (this.settings.mode === 'quiet') return;
        
        const badge = document.createElement('span');
        badge.className = 'subtle-motivation-badge';
        badge.textContent = data.text;
        
        if (data.target) {
            data.target.appendChild(badge);
            setTimeout(() => badge.remove(), 5000);
        }
    }

    updateProgressRing(data) {
        const ring = data.element?.querySelector('.micro-progress-ring');
        if (!ring) return;
        
        const progress = ring.querySelector('.progress');
        const circumference = 2 * Math.PI * 8; // radius = 8
        const offset = circumference - (data.progress / 100) * circumference;
        
        progress.style.strokeDasharray = circumference;
        progress.style.strokeDashoffset = offset;
    }

    handleXPEarned(data) {
        if (data.goalLinked) {
            this.triggerFeedback({
                type: 'toast',
                action: data.action,
                message: `${data.message} (Goal-linked!)`,
                xpGained: data.xpGained,
                duration: 3000
            });
        } else {
            this.triggerFeedback({
                type: 'toast',
                action: data.action,
                message: data.message,
                xpGained: data.xpGained,
                duration: 2500
            });
        }
    }

    handleLevelUp(data) {
        this.triggerFeedback({
            type: 'toast',
            action: 'level_up',
            message: `You're now a ${data.newTitle}! ${data.unlockMessage || ''}`,
            duration: 5000
        });
        
        this.triggerFeedback({
            type: 'celebration',
            element: document.querySelector('.container')
        });
    }

    handleQuestComplete(data) {
        this.triggerFeedback({
            type: 'toast',
            action: 'quest_complete',
            message: `Quest completed: ${data.questTitle}`,
            xpGained: data.xpGained,
            duration: 4000
        });
    }

    handleStreakContinue(data) {
        if (data.streakCount % 7 === 0) { // Celebrate weekly streaks
            this.triggerFeedback({
                type: 'toast',
                action: 'streak_continue',
                message: `${data.streakCount} day streak! Your network is evolving.`,
                xpGained: data.bonusXP,
                duration: 3500
            });
        }
    }

    // Settings management
    setMode(mode) {
        this.settings.mode = mode;
        this.saveSettings();
    }

    toggleSetting(setting) {
        this.settings[setting] = !this.settings[setting];
        this.saveSettings();
    }

    // Quest system integration
    showQuestHint(questData) {
        if (this.settings.mode === 'quiet') return;
        
        const hint = document.createElement('div');
        hint.className = 'quest-hint';
        hint.innerHTML = `
            <strong>💡 Daily Quest:</strong> ${questData.description}
            <div style="font-size: 11px; margin-top: 4px; opacity: 0.7;">
                Reward: ${questData.xpReward} XP
            </div>
        `;
        
        const target = document.querySelector('.container') || document.body;
        target.insertBefore(hint, target.firstChild);
        
        setTimeout(() => hint.remove(), 8000);
    }

    // Progress tracking
    addProgressRing(element, progress) {
        const ring = document.createElement('div');
        ring.className = 'micro-progress-ring';
        ring.innerHTML = `
            <svg>
                <circle class="bg" cx="10" cy="10" r="8"></circle>
                <circle class="progress" cx="10" cy="10" r="8"></circle>
            </svg>
        `;
        
        element.appendChild(ring);
        this.updateProgressRing({ element: ring, progress });
    }
}

// Global instance
window.backgroundGamification = new BackgroundGamificationEngine();

// Helper function for triggering events from server-side
window.triggerGamificationEvent = function(type, data) {
    const event = new CustomEvent(`gamification:${type}`, { detail: data });
    document.dispatchEvent(event);
};

// Settings modal (subtle, only appears when user explicitly wants to configure)
function createSettingsModal() {
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade" id="gamificationSettingsModal" tabindex="-1">
            <div class="modal-dialog modal-sm">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Motivation Settings</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Experience Mode</label>
                            <select class="form-select" id="gamificationMode">
                                <option value="motivated">Motivated - Full feedback</option>
                                <option value="clean">Clean - Minimal feedback</option>
                                <option value="quiet">Quiet - No feedback</option>
                            </select>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="toastEnabled">
                            <label class="form-check-label" for="toastEnabled">
                                Progress notifications
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="glowEffects">
                            <label class="form-check-label" for="glowEffects">
                                Visual effects
                            </label>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="saveGamificationSettings()">Save</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function saveGamificationSettings() {
    const mode = document.getElementById('gamificationMode').value;
    const toastEnabled = document.getElementById('toastEnabled').checked;
    const glowEffects = document.getElementById('glowEffects').checked;
    
    window.backgroundGamification.settings.mode = mode;
    window.backgroundGamification.settings.toastEnabled = toastEnabled;
    window.backgroundGamification.settings.glowEffects = glowEffects;
    window.backgroundGamification.saveSettings();
    
    bootstrap.Modal.getInstance(document.getElementById('gamificationSettingsModal')).hide();
}

// Initialize settings modal when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    createSettingsModal();
});