/**
 * Advanced Contact Search Module
 * Provides real-time search, filtering, and intelligent suggestions
 */

class ContactSearchEngine {
    constructor() {
        this.searchTimeout = null;
        this.suggestionCache = new Map();
        this.activeFilters = new Map();
        this.searchHistory = [];
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSearchHistory();
        this.setupMobileOptimizations();
    }
    
    bindEvents() {
        // Main search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearchInput.bind(this));
            searchInput.addEventListener('focus', this.handleSearchFocus.bind(this));
            searchInput.addEventListener('keydown', this.handleSearchKeydown.bind(this));
        }
        
        // Filter elements
        document.querySelectorAll('select[name], input[type="checkbox"]').forEach(element => {
            element.addEventListener('change', this.handleFilterChange.bind(this));
        });
        
        // Tags input with intelligent suggestions
        const tagsInput = document.getElementById('tagsFilter');
        if (tagsInput) {
            tagsInput.addEventListener('input', this.handleTagsInput.bind(this));
        }
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', this.handleDocumentClick.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Filter toggle
        const filterToggle = document.querySelector('[onclick="toggleFilters()"]');
        if (filterToggle) {
            filterToggle.onclick = this.toggleFilters.bind(this);
        }
        
        // Clear filters
        const clearButton = document.querySelector('[onclick="clearAllFilters()"]');
        if (clearButton) {
            clearButton.onclick = this.clearAllFilters.bind(this);
        }
    }
    
    async handleSearchInput(e) {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        if (query.length >= 2) {
            this.searchTimeout = setTimeout(() => {
                this.fetchSuggestions(query);
            }, 300);
        } else {
            this.hideSuggestions();
        }
        
        // Show popular searches if input is empty
        if (query.length === 0) {
            this.showPopularSearches();
        }
    }
    
    handleSearchFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= 2) {
            this.fetchSuggestions(query);
        } else {
            this.showPopularSearches();
        }
    }
    
    handleSearchKeydown(e) {
        const suggestions = document.getElementById('searchSuggestions');
        const suggestionItems = suggestions.querySelectorAll('.suggestion-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.navigateSuggestions(suggestionItems, 1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.navigateSuggestions(suggestionItems, -1);
        } else if (e.key === 'Enter') {
            const selected = suggestions.querySelector('.suggestion-item.selected');
            if (selected) {
                e.preventDefault();
                this.selectSuggestion(selected.textContent);
            }
        } else if (e.key === 'Escape') {
            this.hideSuggestions();
        }
    }
    
    navigateSuggestions(items, direction) {
        const current = document.querySelector('.suggestion-item.selected');
        let index = -1;
        
        if (current) {
            index = Array.from(items).indexOf(current);
            current.classList.remove('selected');
        }
        
        index += direction;
        
        if (index < 0) index = items.length - 1;
        if (index >= items.length) index = 0;
        
        if (items[index]) {
            items[index].classList.add('selected');
            items[index].scrollIntoView({ block: 'nearest' });
        }
    }
    
    async fetchSuggestions(query) {
        // Check cache first
        if (this.suggestionCache.has(query)) {
            this.showSuggestions(this.suggestionCache.get(query));
            return;
        }
        
        try {
            const response = await fetch(`/api/contacts/search/suggestions?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                this.suggestionCache.set(query, data.suggestions);
                this.showSuggestions(data.suggestions);
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }
    
    showSuggestions(suggestions) {
        const suggestionsEl = document.getElementById('searchSuggestions');
        let html = '';
        
        // Add different types of suggestions with icons
        const suggestionTypes = [
            { key: 'names', icon: 'bi-person', label: 'Contacts' },
            { key: 'companies', icon: 'bi-building', label: 'Companies' },
            { key: 'titles', icon: 'bi-briefcase', label: 'Titles' },
            { key: 'tags', icon: 'bi-tags', label: 'Tags' }
        ];
        
        suggestionTypes.forEach(type => {
            if (suggestions[type.key] && suggestions[type.key].length > 0) {
                html += `<div class="suggestion-category">
                    <small class="text-muted ps-2">
                        <i class="${type.icon} me-1"></i>${type.label}
                    </small>
                </div>`;
                
                suggestions[type.key].forEach(item => {
                    html += `<div class="suggestion-item" data-value="${item}">
                        <i class="${type.icon} me-2 text-muted"></i>${item}
                    </div>`;
                });
            }
        });
        
        if (html) {
            suggestionsEl.innerHTML = html;
            suggestionsEl.classList.remove('d-none');
            
            // Bind click events to suggestion items
            suggestionsEl.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.selectSuggestion(item.dataset.value);
                });
            });
        } else {
            this.hideSuggestions();
        }
    }
    
    showPopularSearches() {
        if (this.searchHistory.length === 0) return;
        
        const suggestionsEl = document.getElementById('searchSuggestions');
        let html = '<div class="suggestion-category"><small class="text-muted ps-2">Recent Searches</small></div>';
        
        this.searchHistory.slice(0, 5).forEach(search => {
            html += `<div class="suggestion-item" data-value="${search}">
                <i class="bi-clock me-2 text-muted"></i>${search}
            </div>`;
        });
        
        suggestionsEl.innerHTML = html;
        suggestionsEl.classList.remove('d-none');
        
        // Bind click events
        suggestionsEl.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectSuggestion(item.dataset.value);
            });
        });
    }
    
    hideSuggestions() {
        const suggestionsEl = document.getElementById('searchSuggestions');
        suggestionsEl.classList.add('d-none');
    }
    
    selectSuggestion(value) {
        const searchInput = document.getElementById('searchInput');
        searchInput.value = value;
        this.hideSuggestions();
        this.addToSearchHistory(value);
        this.performSearch();
    }
    
    handleFilterChange(e) {
        const name = e.target.name;
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        
        if (value) {
            this.activeFilters.set(name, value);
        } else {
            this.activeFilters.delete(name);
        }
        
        // Auto-submit form after short delay
        setTimeout(() => {
            this.performSearch();
        }, 100);
    }
    
    handleTagsInput(e) {
        const value = e.target.value;
        const lastTag = value.split(',').pop().trim();
        
        // Trigger tag suggestions if last tag is being typed
        if (lastTag.length >= 2) {
            this.fetchTagSuggestions(lastTag);
        }
    }
    
    async fetchTagSuggestions(partial) {
        try {
            const response = await fetch(`/api/contacts/tags/suggestions?q=${encodeURIComponent(partial)}`);
            const data = await response.json();
            
            if (data.success && data.tags.length > 0) {
                this.showTagSuggestions(data.tags, partial);
            }
        } catch (error) {
            console.error('Error fetching tag suggestions:', error);
        }
    }
    
    showTagSuggestions(tags, partial) {
        // Create or update tags suggestion dropdown
        let dropdown = document.getElementById('tagsSuggestions');
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.id = 'tagsSuggestions';
            dropdown.className = 'search-suggestions';
            document.getElementById('tagsFilter').parentNode.appendChild(dropdown);
        }
        
        let html = '';
        tags.forEach(tag => {
            html += `<div class="suggestion-item" onclick="addTagSuggestion('${tag}')">
                <i class="bi-tag me-2"></i>${tag}
            </div>`;
        });
        
        dropdown.innerHTML = html;
        dropdown.classList.remove('d-none');
    }
    
    handleDocumentClick(e) {
        if (!e.target.closest('.position-relative')) {
            this.hideSuggestions();
        }
        
        // Hide tag suggestions
        const tagSuggestions = document.getElementById('tagsSuggestions');
        if (tagSuggestions && !e.target.closest('#tagsFilter')) {
            tagSuggestions.classList.add('d-none');
        }
    }
    
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Ctrl/Cmd + / to toggle filters
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            this.toggleFilters();
        }
    }
    
    toggleFilters() {
        const filters = document.getElementById('searchFilters');
        const isVisible = filters.style.display !== 'none';
        
        filters.style.display = isVisible ? 'none' : 'block';
        
        // Update button state
        const toggleBtn = document.querySelector('[onclick="toggleFilters()"]');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (isVisible) {
                icon.className = 'bi bi-funnel me-1';
                toggleBtn.classList.remove('btn-primary');
                toggleBtn.classList.add('btn-outline-primary');
            } else {
                icon.className = 'bi bi-funnel-fill me-1';
                toggleBtn.classList.remove('btn-outline-primary');
                toggleBtn.classList.add('btn-primary');
            }
        }
    }
    
    clearAllFilters() {
        // Clear all form inputs
        const form = document.getElementById('searchForm');
        if (form) {
            // Clear text inputs
            form.querySelectorAll('input[type="text"]').forEach(input => {
                input.value = '';
            });
            
            // Reset selects
            form.querySelectorAll('select').forEach(select => {
                select.selectedIndex = 0;
            });
            
            // Uncheck checkboxes
            form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = false;
            });
        }
        
        // Clear active filters
        this.activeFilters.clear();
        
        // Redirect to clean URL
        window.location.href = '/contacts/search';
    }
    
    performSearch() {
        const form = document.getElementById('searchForm');
        if (form) {
            // Add current search to history
            const query = document.getElementById('searchInput').value.trim();
            if (query) {
                this.addToSearchHistory(query);
            }
            
            form.submit();
        }
    }
    
    addToSearchHistory(query) {
        if (!query || this.searchHistory.includes(query)) return;
        
        this.searchHistory.unshift(query);
        this.searchHistory = this.searchHistory.slice(0, 10); // Keep only last 10
        
        // Save to localStorage
        localStorage.setItem('contactSearchHistory', JSON.stringify(this.searchHistory));
    }
    
    loadSearchHistory() {
        try {
            const saved = localStorage.getItem('contactSearchHistory');
            if (saved) {
                this.searchHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Error loading search history:', error);
        }
    }
    
    setupMobileOptimizations() {
        if ('ontouchstart' in window) {
            // Add touch feedback to contact results
            document.querySelectorAll('.contact-result').forEach(result => {
                result.addEventListener('touchstart', function() {
                    this.style.transform = 'scale(0.98)';
                });
                
                result.addEventListener('touchend', function() {
                    this.style.transform = '';
                });
            });
            
            // Optimize search input for mobile
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.setAttribute('autocomplete', 'off');
                searchInput.setAttribute('autocorrect', 'off');
                searchInput.setAttribute('spellcheck', 'false');
            }
        }
    }
}

// Global functions for template compatibility
window.selectSuggestion = function(value) {
    if (window.contactSearchEngine) {
        window.contactSearchEngine.selectSuggestion(value);
    }
};

window.toggleFilters = function() {
    if (window.contactSearchEngine) {
        window.contactSearchEngine.toggleFilters();
    }
};

window.clearAllFilters = function() {
    if (window.contactSearchEngine) {
        window.contactSearchEngine.clearAllFilters();
    }
};

window.addTagSuggestion = function(tag) {
    const tagsInput = document.getElementById('tagsFilter');
    if (tagsInput) {
        const currentValue = tagsInput.value;
        const tags = currentValue.split(',').map(t => t.trim()).filter(t => t);
        
        if (!tags.includes(tag)) {
            tags.push(tag);
            tagsInput.value = tags.join(', ');
        }
        
        // Hide suggestions
        const suggestions = document.getElementById('tagsSuggestions');
        if (suggestions) {
            suggestions.classList.add('d-none');
        }
        
        // Trigger search
        if (window.contactSearchEngine) {
            window.contactSearchEngine.performSearch();
        }
    }
};

window.logInteraction = function(contactId) {
    // Open interaction logging modal or redirect
    window.location.href = `/contacts/${contactId}#log-interaction`;
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.contactSearchEngine = new ContactSearchEngine();
});