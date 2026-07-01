/**
 * Main JavaScript file for Stock Market Dashboard
 * Contains core functionality and utilities
 */

// ============================================
// Global Configuration
// ============================================
const CONFIG = {
    AUTO_REFRESH_INTERVAL: 30000, // 30 seconds
    API_BASE_URL: '/',
    DEBOUNCE_DELAY: 300,
    MAX_SEARCH_RESULTS: 10
};

// ============================================
// DOM Ready
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Stock Dashboard initialized');
    
    // Initialize sidebar
    initSidebar();
    
    // Initialize dark mode
    initDarkMode();
    
    // Initialize search
    initSearch();
    
    // Initialize tooltips and popovers
    initTooltips();
    
    // Initialize auto-refresh
    initAutoRefresh();
    
    // Initialize price updates
    initPriceUpdates();
});

// ============================================
// Sidebar Functions
// ============================================
function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Store state in localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Restore sidebar state
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }
    }
    
    // Mobile sidebar toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            if (window.innerWidth <= 992) {
                sidebar.classList.toggle('show');
            }
        });
    }
    
    // Close sidebar on outside click (mobile)
    document.addEventListener('click', function(event) {
        const sidebar = document.getElementById('sidebar');
        const navbarToggler = document.querySelector('.navbar-toggler');
        
        if (window.innerWidth <= 992 && 
            sidebar && 
            !sidebar.contains(event.target) && 
            navbarToggler && 
            !navbarToggler.contains(event.target)) {
            sidebar.classList.remove('show');
        }
    });
}

// ============================================
// Dark Mode Functions
// ============================================
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeIcon = document.getElementById('darkModeIcon');
    
    if (darkModeToggle && darkModeIcon) {
        // Check saved preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            enableDarkMode(darkModeIcon);
        }
        
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const html = document.documentElement;
            const isDark = html.getAttribute('data-bs-theme') === 'dark';
            
            if (isDark) {
                disableDarkMode(darkModeIcon);
            } else {
                enableDarkMode(darkModeIcon);
            }
        });
    }
}

function enableDarkMode(icon) {
    document.documentElement.setAttribute('data-bs-theme', 'dark');
    if (icon) {
        icon.className = 'fas fa-sun';
    }
    localStorage.setItem('theme', 'dark');
}

function disableDarkMode(icon) {
    document.documentElement.setAttribute('data-bs-theme', 'light');
    if (icon) {
        icon.className = 'fas fa-moon';
    }
    localStorage.setItem('theme', 'light');
}

// ============================================
// Search Functions
// ============================================
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput && searchResults) {
        let debounceTimer;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();
            
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            
            debounceTimer = setTimeout(function() {
                searchStocks(query);
            }, CONFIG.DEBOUNCE_DELAY);
        });
        
        // Close search results on outside click
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
}

function searchStocks(query) {
    const searchResults = document.getElementById('searchResults');
    
    if (!searchResults) return;
    
    fetch(`/stock/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.results.length > 0) {
                displaySearchResults(data.results);
            } else {
                searchResults.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            searchResults.style.display = 'none';
        });
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    
    if (!searchResults) return;
    
    searchResults.innerHTML = '';
    results.slice(0, CONFIG.MAX_SEARCH_RESULTS).forEach(function(result) {
        const item = document.createElement('a');
        item.className = 'dropdown-item';
        item.href = `/stock/${result.symbol}`;
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${result.symbol}</strong>
                    <small class="text-muted d-block">${result.company_name || result.symbol}</small>
                </div>
                ${result.current_price ? `
                    <div class="text-end">
                        <div>$${result.current_price.toFixed(2)}</div>
                        <small class="${result.price_change >= 0 ? 'text-success' : 'text-danger'}">
                            ${result.price_change >= 0 ? '+' : ''}${(result.price_change_percent || 0).toFixed(2)}%
                        </small>
                    </div>
                ` : ''}
            </div>
        `;
        searchResults.appendChild(item);
    });
    
    searchResults.style.display = 'block';
}

// Global function for search form submit
function searchStock(event) {
    event.preventDefault();
    const searchInput = document.getElementById('searchInput');
    const query = searchInput ? searchInput.value.trim() : '';
    
    if (query) {
        window.location.href = `/stock/${encodeURIComponent(query.toUpperCase())}`;
    }
    return false;
}

// ============================================
// Tooltip and Popover Functions
// ============================================
function initTooltips() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(el) {
        return new bootstrap.Tooltip(el);
    });
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(el) {
        return new bootstrap.Popover(el);
    });
}

// ============================================
// Auto Refresh Functions
// ============================================
function initAutoRefresh() {
    const autoRefresh = document.querySelector('meta[name="auto-refresh"]');
    if (!autoRefresh) return;
    
    const interval = parseInt(autoRefresh.getAttribute('content')) || CONFIG.AUTO_REFRESH_INTERVAL;
    
    if (interval > 0) {
        setInterval(function() {
            if (!document.hidden) {
                refreshData();
            }
        }, interval);
    }
}

function refreshData() {
    // Refresh dashboard data
    if (document.querySelector('.dashboard-container')) {
        fetchDashboardData();
    }
    
    // Refresh stock prices
    if (document.querySelector('.stock-prices')) {
        updateStockPrices();
    }
}

// ============================================
// Price Update Functions
// ============================================
function initPriceUpdates() {
    const priceElements = document.querySelectorAll('[data-stock-symbol]');
    if (priceElements.length > 0) {
        setInterval(function() {
            updateStockPrices();
        }, 60000); // Update every minute
    }
}

function updateStockPrices() {
    const symbols = [];
    const elements = document.querySelectorAll('[data-stock-symbol]');
    
    elements.forEach(function(el) {
        const symbol = el.getAttribute('data-stock-symbol');
        if (symbol && !symbols.includes(symbol)) {
            symbols.push(symbol);
        }
    });
    
    if (symbols.length === 0) return;
    
    fetch(`/api/stocks/prices?symbols=${symbols.join(',')}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updatePriceDisplay(data.prices);
            }
        })
        .catch(error => console.error('Price update error:', error));
}

function updatePriceDisplay(prices) {
    Object.keys(prices).forEach(function(symbol) {
        const priceData = prices[symbol];
        const elements = document.querySelectorAll(`[data-stock-symbol="${symbol}"]`);
        
        elements.forEach(function(el) {
            const type = el.getAttribute('data-price-type') || 'price';
            
            if (type === 'price' && priceData.price) {
                el.textContent = `$${priceData.price.toFixed(2)}`;
            } else if (type === 'change' && priceData.change !== undefined) {
                const change = priceData.change;
                const changePercent = priceData.change_percent || 0;
                const isPositive = change >= 0;
                
                el.textContent = `${isPositive ? '+' : ''}${change.toFixed(2)} (${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`;
                el.className = `stock-change ${isPositive ? 'positive' : 'negative'}`;
            }
        });
    });
}

// ============================================
// Utility Functions
// ============================================
function formatCurrency(amount, currency = 'USD') {
    const symbols = {
        USD: '$',
        EUR: '€',
        GBP: '£',
        JPY: '¥',
        INR: '₹'
    };
    
    const symbol = symbols[currency] || '$';
    return `${symbol}${Number(amount).toFixed(2)}`;
}

function formatPercentage(value) {
    return `${Number(value).toFixed(2)}%`;
}

function getTimeAgo(date) {
    const now = new Date();
    const diff = now - new Date(date);
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const months = Math.floor(days / 30);
    const years = Math.floor(days / 365);
    
    if (years > 0) return `${years} year${years > 1 ? 's' : ''} ago`;
    if (months > 0) return `${months} month${months > 1 ? 's' : ''} ago`;
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// Toast Notifications
// ============================================
function showToast(message, type = 'info', title = '') {
    const container = document.querySelector('.toast-container');
    if (!container) return;
    
    const colors = {
        success: 'bg-success',
        danger: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
    };
    
    const icons = {
        success: 'fa-check-circle',
        danger: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white ${colors[type] || colors.info} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas ${icons[type] || icons.info} me-2"></i>
                ${title ? `<strong>${title}</strong><br>` : ''}
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    container.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// ============================================
// Loading Spinner
// ============================================
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="spinner-container">
            <div class="spinner"></div>
        </div>
    `;
}

function hideLoading(containerId, content) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = content || '';
}

// ============================================
// Export Functions
// ============================================
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csv = [];
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        
        cols.forEach(function(col) {
            let text = col.textContent.trim();
            // Handle commas and quotes
            if (text.includes(',') || text.includes('"') || text.includes('\n')) {
                text = `"${text.replace(/"/g, '""')}"`;
            }
            rowData.push(text);
        });
        
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function exportTableToPDF(tableId, filename = 'export.pdf') {
    // Requires html2pdf library or similar
    // This is a placeholder
    console.log('PDF export functionality requires html2pdf library');
}