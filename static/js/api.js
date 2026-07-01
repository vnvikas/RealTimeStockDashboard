/**
 * API JavaScript for Stock Market Dashboard
 * Handles API calls and data fetching
 */

// ============================================
// API Configuration
// ============================================
const API = {
    BASE_URL: '',
    endpoints: {
        stock: '/stock/api',
        market: '/market/api',
        portfolio: '/portfolio/api',
        watchlist: '/watchlist/api',
        dashboard: '/dashboard/api'
    }
};

// ============================================
// Stock API Functions
// ============================================
function getStockQuote(symbol) {
    return fetch(`${API.BASE_URL}/stock/api/quote/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch stock quote');
            }
        });
}

function getStockHistory(symbol, days = 30) {
    return fetch(`${API.BASE_URL}/stock/api/history/${symbol}?days=${days}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch stock history');
            }
        });
}

function getStockDetails(symbol) {
    return fetch(`${API.BASE_URL}/stock/api/details/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch stock details');
            }
        });
}

function searchStocks(query) {
    return fetch(`${API.BASE_URL}/stock/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.results;
            } else {
                throw new Error(data.error || 'Search failed');
            }
        });
}

// ============================================
// Market API Functions
// ============================================
function getMarketData() {
    return fetch(`${API.BASE_URL}/market/api/market-data`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch market data');
            }
        });
}

function getIndices() {
    return fetch(`${API.BASE_URL}/market/api/indices`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch indices');
            }
        });
}

function getTopMovers() {
    return fetch(`${API.BASE_URL}/market/api/top-movers`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch top movers');
            }
        });
}

// ============================================
// Portfolio API Functions
// ============================================
function getPortfolio() {
    return fetch(`${API.BASE_URL}/portfolio/api/portfolio-data`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch portfolio');
            }
        });
}

function addToPortfolio(symbol, quantity, buyPrice, buyDate, notes) {
    const formData = new FormData();
    formData.append('symbol', symbol);
    formData.append('quantity', quantity);
    formData.append('buy_price', buyPrice);
    formData.append('buy_date', buyDate);
    formData.append('notes', notes || '');
    
    return fetch(`${API.BASE_URL}/portfolio/add`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to add to portfolio');
        }
        return data;
    });
}

function updatePortfolio(portfolioId, quantity, buyPrice, notes) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('buy_price', buyPrice);
    formData.append('notes', notes || '');
    
    return fetch(`${API.BASE_URL}/portfolio/update/${portfolioId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to update portfolio');
        }
        return data;
    });
}

function removeFromPortfolio(portfolioId) {
    return fetch(`${API.BASE_URL}/portfolio/delete/${portfolioId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to remove from portfolio');
        }
        return data;
    });
}

// ============================================
// Watchlist API Functions
// ============================================
function getWatchlist() {
    return fetch(`${API.BASE_URL}/watchlist/api/watchlist-data`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch watchlist');
            }
        });
}

function addToWatchlist(symbol, notes, priceAlert) {
    return fetch(`${API.BASE_URL}/watchlist/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            symbol: symbol,
            notes: notes || '',
            price_alert: priceAlert || null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to add to watchlist');
        }
        return data;
    });
}

function removeFromWatchlist(watchlistId) {
    return fetch(`${API.BASE_URL}/watchlist/remove/${watchlistId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to remove from watchlist');
        }
        return data;
    });
}

function toggleFavorite(watchlistId) {
    return fetch(`${API.BASE_URL}/watchlist/favorite/${watchlistId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to toggle favorite');
        }
        return data;
    });
}

// ============================================
// Dashboard API Functions
// ============================================
function getDashboardData() {
    return fetch(`${API.BASE_URL}/dashboard/api/dashboard-data`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data;
            } else {
                throw new Error(data.error || 'Failed to fetch dashboard data');
            }
        });
}

// ============================================
// News API Functions
// ============================================
function getNews(symbol = null, category = 'all', limit = 10) {
    let url = `${API.BASE_URL}/news?limit=${limit}`;
    if (symbol) url += `&symbol=${symbol}`;
    if (category !== 'all') url += `&category=${category}`;
    
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch news');
            }
        });
}

// ============================================
// Notification API Functions
// ============================================
function getNotifications() {
    return fetch(`${API.BASE_URL}/notifications`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.error || 'Failed to fetch notifications');
            }
        });
}

function markNotificationRead(notificationId) {
    return fetch(`${API.BASE_URL}/notifications/${notificationId}/read`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to mark notification as read');
        }
        return data;
    });
}

// ============================================
// User API Functions
// ============================================
function updateProfile(data) {
    return fetch(`${API.BASE_URL}/profile/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to update profile');
        }
        return data;
    });
}

function changePassword(currentPassword, newPassword, confirmPassword) {
    return fetch(`${API.BASE_URL}/profile/change-password`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
            confirm_password: confirmPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Failed to change password');
        }
        return data;
    });
}

// ============================================
// Helper Functions for API Calls
// ============================================
function handleAPIError(error) {
    console.error('API Error:', error);
    showToast(error.message || 'An error occurred', 'danger');
    throw error;
}

function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.error || 'Request failed');
            }
            return data;
        })
        .catch(error => {
            console.error('API request error:', error);
            throw error;
        });
}