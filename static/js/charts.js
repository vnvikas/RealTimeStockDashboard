/**
 * Charts JavaScript for Stock Market Dashboard
 * Handles all chart creation and updates using Chart.js and Plotly
 */

// ============================================
// Chart.js Charts
// ============================================
class ChartManager {
    constructor() {
        this.charts = {};
        this.defaultColors = [
            '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
            '#9b59b6', '#1abc9c', '#e67e22', '#2c3e50',
            '#2980b9', '#27ae60', '#c0392b', '#d35400'
        ];
    }
    
    createLineChart(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId);
        if (!ctx) return null;
        
        const defaultOptions = {
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
        };
        
        const config = {
            type: 'line',
            data: data,
            options: { ...defaultOptions, ...options }
        };
        
        this.charts[elementId] = new Chart(ctx, config);
        return this.charts[elementId];
    }
    
    createBarChart(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId);
        if (!ctx) return null;
        
        const defaultOptions = {
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
                    },
                    beginAtZero: true
                }
            }
        };
        
        const config = {
            type: 'bar',
            data: data,
            options: { ...defaultOptions, ...options }
        };
        
        this.charts[elementId] = new Chart(ctx, config);
        return this.charts[elementId];
    }
    
    createDoughnutChart(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId);
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        };
        
        const config = {
            type: 'doughnut',
            data: data,
            options: { ...defaultOptions, ...options }
        };
        
        this.charts[elementId] = new Chart(ctx, config);
        return this.charts[elementId];
    }
    
    createPieChart(elementId, data, options = {}) {
        const ctx = document.getElementById(elementId);
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        };
        
        const config = {
            type: 'pie',
            data: data,
            options: { ...defaultOptions, ...options }
        };
        
        this.charts[elementId] = new Chart(ctx, config);
        return this.charts[elementId];
    }
    
    updateChart(elementId, data) {
        if (this.charts[elementId]) {
            this.charts[elementId].data = data;
            this.charts[elementId].update();
        }
    }
    
    destroyChart(elementId) {
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
            delete this.charts[elementId];
        }
    }
    
    getChart(elementId) {
        return this.charts[elementId] || null;
    }
}

// ============================================
// Plotly Charts
// ============================================
class PlotlyChartManager {
    constructor() {
        this.charts = {};
        this.layoutDefaults = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['toImage', 'sendDataToCloud'],
            showlegend: true,
            legend: {
                orientation: 'h',
                y: 1.1
            },
            xaxis: {
                gridcolor: 'rgba(0,0,0,0.05)'
            },
            yaxis: {
                gridcolor: 'rgba(0,0,0,0.05)'
            }
        };
    }
    
    createLineChart(elementId, data, layout = {}) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        const defaultLayout = {
            ...this.layoutDefaults,
            title: 'Line Chart',
            xaxis: { ...this.layoutDefaults.xaxis, title: 'Date' },
            yaxis: { ...this.layoutDefaults.yaxis, title: 'Value' }
        };
        
        const config = {
            ...defaultLayout,
            ...layout
        };
        
        Plotly.newPlot(elementId, data, config, { responsive: true });
        this.charts[elementId] = { data, layout: config };
        return this.charts[elementId];
    }
    
    createCandlestickChart(elementId, data, layout = {}) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        const defaultLayout = {
            ...this.layoutDefaults,
            title: 'Candlestick Chart',
            xaxis: { ...this.layoutDefaults.xaxis, title: 'Date' },
            yaxis: { ...this.layoutDefaults.yaxis, title: 'Price ($)' }
        };
        
        const config = {
            ...defaultLayout,
            ...layout
        };
        
        Plotly.newPlot(elementId, data, config, { responsive: true });
        this.charts[elementId] = { data, layout: config };
        return this.charts[elementId];
    }
    
    createBarChart(elementId, data, layout = {}) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        const defaultLayout = {
            ...this.layoutDefaults,
            title: 'Bar Chart',
            xaxis: { ...this.layoutDefaults.xaxis, title: 'Category' },
            yaxis: { ...this.layoutDefaults.yaxis, title: 'Value' },
            barmode: 'group'
        };
        
        const config = {
            ...defaultLayout,
            ...layout
        };
        
        Plotly.newPlot(elementId, data, config, { responsive: true });
        this.charts[elementId] = { data, layout: config };
        return this.charts[elementId];
    }
    
    createPieChart(elementId, data, layout = {}) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        const defaultLayout = {
            ...this.layoutDefaults,
            title: 'Distribution',
            showlegend: true
        };
        
        const config = {
            ...defaultLayout,
            ...layout
        };
        
        Plotly.newPlot(elementId, data, config, { responsive: true });
        this.charts[elementId] = { data, layout: config };
        return this.charts[elementId];
    }
    
    updateChart(elementId, data, layout = {}) {
        if (this.charts[elementId]) {
            const currentLayout = this.charts[elementId].layout;
            const newLayout = { ...currentLayout, ...layout };
            Plotly.react(elementId, data, newLayout, { responsive: true });
            this.charts[elementId] = { data, layout: newLayout };
        }
    }
    
    destroyChart(elementId) {
        if (this.charts[elementId]) {
            Plotly.purge(elementId);
            delete this.charts[elementId];
        }
    }
    
    getChart(elementId) {
        return this.charts[elementId] || null;
    }
}

// ============================================
// Chart Data Helpers
// ============================================
function preparePriceData(priceHistory, symbol) {
    if (!priceHistory || priceHistory.length === 0) return null;
    
    const dates = priceHistory.map(p => p.date);
    const prices = priceHistory.map(p => p.close);
    
    return {
        labels: dates,
        datasets: [{
            label: symbol || 'Stock Price',
            data: prices,
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            fill: true,
            tension: 0.4
        }]
    };
}

function prepareCandlestickData(priceHistory) {
    if (!priceHistory || priceHistory.length === 0) return null;
    
    return {
        dates: priceHistory.map(p => p.date),
        open: priceHistory.map(p => p.open),
        high: priceHistory.map(p => p.high),
        low: priceHistory.map(p => p.low),
        close: priceHistory.map(p => p.close)
    };
}

function preparePortfolioData(portfolio) {
    if (!portfolio || portfolio.length === 0) return null;
    
    const labels = portfolio.map(p => p.symbol);
    const values = portfolio.map(p => p.current_value);
    const colors = values.map(v => v >= 0 ? '#2ecc71' : '#e74c3c');
    
    return {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors,
            borderColor: colors,
            borderWidth: 1
        }]
    };
}

function prepareSectorData(sectorDistribution) {
    if (!sectorDistribution || Object.keys(sectorDistribution).length === 0) return null;
    
    const labels = Object.keys(sectorDistribution);
    const values = Object.values(sectorDistribution);
    const colors = [
        '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
        '#9b59b6', '#1abc9c', '#e67e22', '#2c3e50'
    ];
    
    return {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: colors.slice(0, labels.length),
            borderColor: '#fff',
            borderWidth: 2
        }]
    };
}

function preparePerformanceData(performance) {
    if (!performance || performance.length === 0) return null;
    
    const labels = performance.map(p => p.symbol);
    const values = performance.map(p => p.profit_loss_percent);
    const colors = values.map(v => v >= 0 ? 'rgba(46, 204, 113, 0.7)' : 'rgba(231, 76, 60, 0.7)');
    
    return {
        labels: labels,
        datasets: [{
            label: 'Performance %',
            data: values,
            backgroundColor: colors,
            borderColor: colors.map(c => c.replace('0.7', '1')),
            borderWidth: 1
        }]
    };
}

// ============================================
// Initialize Chart Managers
// ============================================
const chartManager = new ChartManager();
const plotlyManager = new PlotlyChartManager();

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts based on page
    if (document.querySelector('.dashboard-container')) {
        initializeDashboardCharts();
    }
    
    if (document.querySelector('.stock-details-container')) {
        initializeStockCharts();
    }
    
    if (document.querySelector('.portfolio-container')) {
        initializePortfolioCharts();
    }
});

function initializeDashboardCharts() {
    // Portfolio Growth
    const growthElement = document.getElementById('portfolioGrowthChart');
    if (growthElement) {
        chartManager.createLineChart('portfolioGrowthChart', {
            labels: [],
            datasets: [{
                label: 'Portfolio Value',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.4
            }]
        });
    }
    
    // Sector Distribution
    const sectorElement = document.getElementById('sectorDistributionChart');
    if (sectorElement) {
        chartManager.createDoughnutChart('sectorDistributionChart', {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'],
                borderWidth: 2
            }]
        });
    }
}

function initializeStockCharts() {
    // Stock charts will be initialized when data loads
}

function initializePortfolioCharts() {
    // Portfolio charts will be initialized when data loads
}

// ============================================
// Chart Utility Functions
// ============================================
function downloadChart(elementId, filename = 'chart.png') {
    Plotly.downloadImage(elementId, {
        format: 'png',
        width: 1200,
        height: 800,
        filename: filename
    });
}

function exportChartData(elementId) {
    const chart = chartManager.getChart(elementId);
    if (chart) {
        const data = {
            labels: chart.data.labels,
            datasets: chart.data.datasets.map(ds => ({
                label: ds.label,
                data: ds.data
            }))
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${elementId}_data_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}