/**
 * Dashboard JavaScript for Stock Market Dashboard
 * Handles dashboard charts and data updates
 */

// ============================================
// Dashboard Charts
// ============================================
let dashboardCharts = {};

document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.dashboard-container')) {
        initializeDashboardCharts();
        loadDashboardData();
        setupAutoRefresh();
    }
});

function initializeDashboardCharts() {
    // Portfolio Growth Chart
    const portfolioChartElement = document.getElementById('portfolioGrowthChart');
    if (portfolioChartElement) {
        dashboardCharts.portfolioGrowth = createPortfolioGrowthChart(portfolioChartElement);
    }
    
    // Sector Distribution Chart
    const sectorChartElement = document.getElementById('sectorDistributionChart');
    if (sectorChartElement) {
        dashboardCharts.sectorDistribution = createSectorDistributionChart(sectorChartElement);
    }
    
    // Performance Chart
    const performanceChartElement = document.getElementById('performanceChart');
    if (performanceChartElement) {
        dashboardCharts.performance = createPerformanceChart(performanceChartElement);
    }
}

function createPortfolioGrowthChart(element) {
    const ctx = element.getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Portfolio Value',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function createSectorDistributionChart(element) {
    const ctx = element.getContext('2d');
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
                    '#9b59b6', '#1abc9c', '#e67e22', '#2c3e50'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function createPerformanceChart(element) {
    const ctx = element.getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Profit/Loss',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// ============================================
// Load Dashboard Data
// ============================================
function loadDashboardData() {
    fetch('/dashboard/api/dashboard-data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateDashboardCharts(data);
                updateDashboardStats(data);
                updateMarketData(data);
            } else {
                console.error('Error loading dashboard data:', data.error);
            }
        })
        .catch(error => {
            console.error('Dashboard data error:', error);
        });
}

function updateDashboardCharts(data) {
    // Update Portfolio Growth Chart
    if (dashboardCharts.portfolioGrowth && data.portfolio) {
        const chart = dashboardCharts.portfolioGrowth;
        chart.data.labels = data.portfolio.dates || [];
        chart.data.datasets[0].data = data.portfolio.values || [];
        chart.update();
    }
    
    // Update Sector Distribution Chart
    if (dashboardCharts.sectorDistribution && data.sectors) {
        const chart = dashboardCharts.sectorDistribution;
        chart.data.labels = Object.keys(data.sectors);
        chart.data.datasets[0].data = Object.values(data.sectors);
        chart.update();
    }
    
    // Update Performance Chart
    if (dashboardCharts.performance && data.performance) {
        const chart = dashboardCharts.performance;
        chart.data.labels = data.performance.symbols || [];
        chart.data.datasets[0].data = data.performance.profit_loss || [];
        chart.data.datasets[0].backgroundColor = data.performance.profit_loss.map(v => 
            v >= 0 ? 'rgba(46, 204, 113, 0.7)' : 'rgba(231, 76, 60, 0.7)'
        );
        chart.update();
    }
}

function updateDashboardStats(data) {
    if (data.stats) {
        // Update portfolio value
        const portfolioValue = document.getElementById('portfolioValue');
        if (portfolioValue) {
            portfolioValue.textContent = formatCurrency(data.stats.total_value);
        }
        
        // Update profit/loss
        const profitLoss = document.getElementById('profitLoss');
        if (profitLoss) {
            const pl = data.stats.profit_loss || 0;
            profitLoss.textContent = formatCurrency(pl);
            profitLoss.className = `stat-change ${pl >= 0 ? 'positive' : 'negative'}`;
        }
        
        // Update watchlist count
        const watchlistCount = document.getElementById('watchlistCount');
        if (watchlistCount) {
            watchlistCount.textContent = data.stats.watchlist_count || 0;
        }
        
        // Update stock count
        const stockCount = document.getElementById('stockCount');
        if (stockCount) {
            stockCount.textContent = data.stats.stock_count || 0;
        }
    }
}

function updateMarketData(data) {
    if (data.market) {
        // Update market status
        const marketStatus = document.getElementById('marketStatus');
        if (marketStatus) {
            marketStatus.className = `market-status ${data.market.status}`;
            marketStatus.textContent = data.market.status.toUpperCase();
        }
        
        // Update market time
        const marketTime = document.getElementById('marketTime');
        if (marketTime) {
            marketTime.textContent = data.market.time || '';
        }
        
        // Update indices
        const indicesContainer = document.getElementById('indicesContainer');
        if (indicesContainer && data.market.indices) {
            indicesContainer.innerHTML = '';
            data.market.indices.forEach(function(index) {
                const div = document.createElement('div');
                div.className = 'd-flex justify-content-between align-items-center p-2 border-bottom';
                div.innerHTML = `
                    <div>
                        <strong>${index.name}</strong>
                    </div>
                    <div class="text-end">
                        <div>${formatCurrency(index.value)}</div>
                        <small class="${index.change >= 0 ? 'text-success' : 'text-danger'}">
                            ${index.change >= 0 ? '+' : ''}${index.change.toFixed(2)}%
                        </small>
                    </div>
                `;
                indicesContainer.appendChild(div);
            });
        }
    }
}

// ============================================
// Auto Refresh
// ============================================
function setupAutoRefresh() {
    const refreshCheckbox = document.getElementById('autoRefreshToggle');
    if (refreshCheckbox) {
        const interval = setInterval(function() {
            if (refreshCheckbox.checked) {
                loadDashboardData();
            }
        }, 30000); // 30 seconds
        
        // Store interval for cleanup
        window.dashboardRefreshInterval = interval;
    }
}

// ============================================
// Export Dashboard Data
// ============================================
function exportDashboardData() {
    // Get current data from charts
    const data = {
        portfolio: dashboardCharts.portfolioGrowth ? dashboardCharts.portfolioGrowth.data : null,
        sectors: dashboardCharts.sectorDistribution ? dashboardCharts.sectorDistribution.data : null,
        performance: dashboardCharts.performance ? dashboardCharts.performance.data : null,
        timestamp: new Date().toISOString()
    };
    
    // Create download
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `dashboard_export_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ============================================
// Stock Details Chart (Plotly)
// ============================================
function createStockChart(data, elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const trace = {
        type: 'scatter',
        mode: 'lines',
        name: data.symbol || 'Stock',
        x: data.dates || [],
        y: data.prices || [],
        line: {
            color: '#3498db',
            width: 2
        }
    };
    
    const layout = {
        title: `${data.symbol} - Price History`,
        xaxis: {
            title: 'Date',
            gridcolor: 'rgba(0,0,0,0.05)'
        },
        yaxis: {
            title: 'Price ($)',
            gridcolor: 'rgba(0,0,0,0.05)'
        },
        hovermode: 'x unified',
        showlegend: true,
        legend: {
            orientation: 'h',
            y: 1.1
        }
    };
    
    Plotly.newPlot(element, [trace], layout, {
        responsive: true,
        displayModeBar: true
    });
}

function createCandlestickChart(data, elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const trace = {
        type: 'candlestick',
        x: data.dates || [],
        open: data.open || [],
        high: data.high || [],
        low: data.low || [],
        close: data.close || [],
        increasing: { line: { color: '#2ecc71' } },
        decreasing: { line: { color: '#e74c3c' } }
    };
    
    const layout = {
        title: `${data.symbol} - Candlestick Chart`,
        xaxis: {
            title: 'Date',
            gridcolor: 'rgba(0,0,0,0.05)'
        },
        yaxis: {
            title: 'Price ($)',
            gridcolor: 'rgba(0,0,0,0.05)'
        },
        hovermode: 'x unified'
    };
    
    Plotly.newPlot(element, [trace], layout, {
        responsive: true,
        displayModeBar: true
    });
}

function createVolumeChart(data, elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const trace = {
        type: 'bar',
        name: 'Volume',
        x: data.dates || [],
        y: data.volume || [],
        marker: {
            color: '#3498db',
            opacity: 0.7
        }
    };
    
    const layout = {
        title: `${data.symbol} - Volume`,
        xaxis: {
            title: 'Date',
            gridcolor: 'rgba(0,0,0,0.05)'
        },
        yaxis: {
            title: 'Volume',
            gridcolor: 'rgba(0,0,0,0.05)'
        }
    };
    
    Plotly.newPlot(element, [trace], layout, {
        responsive: true,
        displayModeBar: true
    });
}

// ============================================
// Stock Details Data Loading
// ============================================
function loadStockDetails(symbol) {
    const container = document.getElementById('stockDetailsContainer');
    if (!container) return;
    
    showLoading('stockDetailsContainer');
    
    fetch(`/stock/api/stock-data/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayStockDetails(data.data);
                createStockCharts(data.data);
            } else {
                showToast('Error loading stock data: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            console.error('Stock details error:', error);
            showToast('Error loading stock data.', 'danger');
        })
        .finally(() => {
            hideLoading('stockDetailsContainer');
        });
}

function displayStockDetails(data) {
    // Update stock info
    document.getElementById('stockSymbol').textContent = data.symbol;
    document.getElementById('stockName').textContent = data.company_name;
    document.getElementById('stockPrice').textContent = formatCurrency(data.current_price);
    
    const change = data.price_change || 0;
    const changePercent = data.price_change_percent || 0;
    const changeElement = document.getElementById('stockChange');
    changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
    changeElement.className = `stock-change ${change >= 0 ? 'positive' : 'negative'}`;
    
    // Update company info
    document.getElementById('companySector').textContent = data.sector || 'N/A';
    document.getElementById('companyIndustry').textContent = data.industry || 'N/A';
    document.getElementById('companyCEO').textContent = data.ceo || 'N/A';
    document.getElementById('companyEmployees').textContent = data.employees ? data.employees.toLocaleString() : 'N/A';
    document.getElementById('companyWebsite').href = data.website || '#';
    document.getElementById('companyWebsite').textContent = data.website || 'N/A';
    document.getElementById('companyDescription').textContent = data.description || 'No description available.';
    
    // Update financials
    document.getElementById('marketCap').textContent = data.market_cap ? formatCurrency(data.market_cap) : 'N/A';
    document.getElementById('peRatio').textContent = data.pe_ratio ? data.pe_ratio.toFixed(2) : 'N/A';
    document.getElementById('dividendYield').textContent = data.dividend_yield ? data.dividend_yield.toFixed(2) + '%' : 'N/A';
    document.getElementById('weekHigh').textContent = data.fifty_two_week_high ? formatCurrency(data.fifty_two_week_high) : 'N/A';
    document.getElementById('weekLow').textContent = data.fifty_two_week_low ? formatCurrency(data.fifty_two_week_low) : 'N/A';
}

function createStockCharts(data) {
    // Create charts using Plotly
    if (data.prices && data.prices.length > 0) {
        const chartData = {
            symbol: data.symbol,
            dates: data.prices.map(p => p.date),
            prices: data.prices.map(p => p.close),
            open: data.prices.map(p => p.open),
            high: data.prices.map(p => p.high),
            low: data.prices.map(p => p.low),
            close: data.prices.map(p => p.close),
            volume: data.prices.map(p => p.volume)
        };
        
        createStockChart(chartData, 'priceChart');
        createCandlestickChart(chartData, 'candlestickChart');
        createVolumeChart(chartData, 'volumeChart');
    }
}