// Dashboard JavaScript
let priceChart = null;
let rsiChart = null;
let currentCoin = 'bitcoin';
let refreshInterval = null;

// Initialize dashboard on page load
$(document).ready(function() {
    initializeDashboard();
    setupEventHandlers();
    startAutoRefresh();
});

function initializeDashboard() {
    addLog('Dashboard initialized');
    updateStatus('connected', 'Connected');
    
    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadMarketOverview();
    loadCryptoPrice();
}

function setupEventHandlers() {
    // Coin selection change
    $('#coin-select').on('change', function() {
        currentCoin = $(this).val();
        addLog(`Switched to ${currentCoin}`);
        loadCryptoPrice();
    });

    // Refresh button
    $('#refresh-btn').on('click', function() {
        addLog('Refreshing data...');
        loadMarketOverview();
        loadCryptoPrice();
        loadCryptoHistory();
    });

    // Train models button
    $('#train-btn').on('click', function() {
        trainModels();
    });

    // Get predictions button
    $('#predict-btn').on('click', function() {
        getPredictions();
    });

    // Buy button
    $('#buy-btn').on('click', function() {
        executeTrade('buy');
    });

    // Sell button
    $('#sell-btn').on('click', function() {
        executeTrade('sell');
    });
}

function startAutoRefresh() {
    // Refresh data every 30 seconds
    refreshInterval = setInterval(function() {
        loadMarketOverview();
        loadCryptoPrice();
    }, 30000);
}

function updateStatus(status, text) {
    const statusDot = $('#status-dot');
    const statusText = $('#status-text');
    
    if (status === 'connected') {
        statusDot.removeClass('disconnected');
        statusText.text(text);
    } else {
        statusDot.addClass('disconnected');
        statusText.text(text);
    }
    
    updateLastUpdate();
}

function updateLastUpdate() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    $('#last-update').text(timeString);
}

function addLog(message, type = 'info') {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const logEntry = $('<div class="log-entry"></div>');
    
    let logClass = '';
    if (type === 'error') {
        logClass = 'log-error';
    }
    
    logEntry.html(
        `<span class="log-time">[${timeString}]</span> ` +
        `<span class="${logClass}">${message}</span>`
    );
    
    const logContainer = $('#system-log');
    logContainer.prepend(logEntry);
    
    // Keep only last 50 log entries
    if (logContainer.children().length > 50) {
        logContainer.children().last().remove();
    }
}

function initializeCharts() {
    // Price Chart
    const priceCtx = document.getElementById('price-chart').getContext('2d');
    priceChart = new Chart(priceCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price (USD)',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
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
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });

    // RSI Chart
    const rsiCtx = document.getElementById('rsi-chart').getContext('2d');
    rsiChart = new Chart(rsiCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'RSI',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
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
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        }
    });
}

function loadMarketOverview() {
    $.ajax({
        url: '/api/market/',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            updateMarketTable(data.market_overview);
            addLog(`Loaded ${data.total_cryptocurrencies} cryptocurrencies`);
        },
        error: function(xhr, status, error) {
            addLog(`Error loading market data: ${error}`, 'error');
            updateStatus('disconnected', 'Connection Error');
        }
    });
}

function updateMarketTable(marketData) {
    const tbody = $('#market-table-body');
    tbody.empty();
    
    if (!marketData || marketData.length === 0) {
        tbody.append('<tr><td colspan="7" class="empty-state">No market data available</td></tr>');
        return;
    }
    
    marketData.forEach(function(coin) {
        const changeClass = coin.price_change_24h_percent >= 0 ? 'change-positive' : 'change-negative';
        const changeIcon = coin.price_change_24h_percent >= 0 ? '▲' : '▼';
        
        const row = $('<tr></tr>');
        row.html(`
            <td>${coin.market_cap_rank || '--'}</td>
            <td><strong>${coin.name}</strong></td>
            <td>${coin.symbol}</td>
            <td>$${formatNumber(coin.price_usd)}</td>
            <td class="${changeClass}">${changeIcon} ${formatPercentage(coin.price_change_24h_percent)}</td>
            <td>$${formatLargeNumber(coin.market_cap_usd)}</td>
            <td>$${formatLargeNumber(coin.volume_24h_usd)}</td>
        `);
        tbody.append(row);
    });
}

function loadCryptoPrice() {
    $.ajax({
        url: `/api/price/${currentCoin}/`,
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            updatePriceStats(data);
            addLog(`Updated ${currentCoin} price: $${formatNumber(data.price_usd)}`);
            
            // Also load history for charts
            loadCryptoHistory();
        },
        error: function(xhr, status, error) {
            addLog(`Error loading ${currentCoin} price: ${error}`, 'error');
        }
    });
}

function updatePriceStats(data) {
    // Update current price
    $('#current-price').text('$' + formatNumber(data.price_usd));
    
    // Update price change
    const change = data.price_change_24h_percent;
    const changeElement = $('#price-change');
    const changeClass = change >= 0 ? 'positive' : 'negative';
    const changeIcon = change >= 0 ? '▲' : '▼';
    changeElement.removeClass('positive negative').addClass(changeClass);
    changeElement.text(`${changeIcon} ${formatPercentage(change)}`);
    
    // Update market cap
    $('#market-cap').text('$' + formatLargeNumber(data.market_cap_usd));
    
    // Update volume
    $('#volume-24h').text('$' + formatLargeNumber(data.volume_24h_usd));
}

function loadCryptoHistory() {
    const days = $('#days-input').val();
    
    $.ajax({
        url: `/api/history/${currentCoin}/`,
        method: 'GET',
        data: { days: days },
        dataType: 'json',
        success: function(data) {
            updateCharts(data.prices);
            addLog(`Loaded ${data.data_points} historical data points`);
        },
        error: function(xhr, status, error) {
            addLog(`Error loading history: ${error}`, 'error');
        }
    });
}

function updateCharts(prices) {
    if (!prices || prices.length === 0) {
        return;
    }
    
    // Prepare data for charts
    const labels = [];
    const priceData = [];
    const rsiData = [];
    
    // Calculate RSI (simplified version)
    const rsiPeriod = 14;
    
    prices.forEach(function(point, index) {
        const date = new Date(point.timestamp * 1000);
        labels.push(date.toLocaleDateString());
        priceData.push(point.price);
        
        // Calculate simple RSI
        if (index >= rsiPeriod) {
            const slice = prices.slice(index - rsiPeriod, index);
            let gains = 0;
            let losses = 0;
            
            for (let i = 1; i < slice.length; i++) {
                const change = slice[i].price - slice[i-1].price;
                if (change > 0) {
                    gains += change;
                } else {
                    losses += Math.abs(change);
                }
            }
            
            const avgGain = gains / rsiPeriod;
            const avgLoss = losses / rsiPeriod;
            const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
            const rsi = 100 - (100 / (1 + rs));
            rsiData.push(rsi);
        } else {
            rsiData.push(50); // Default neutral RSI
        }
    });
    
    // Update price chart
    priceChart.data.labels = labels;
    priceChart.data.datasets[0].data = priceData;
    priceChart.update();
    
    // Update RSI chart
    rsiChart.data.labels = labels;
    rsiChart.data.datasets[0].data = rsiData;
    rsiChart.update();
}

function trainModels() {
    addLog('Training ML models... (This is a simulation)', 'info');
    
    // Simulate training delay
    setTimeout(function() {
        const accuracy = (Math.random() * 0.15 + 0.75).toFixed(3); // 75-90%
        addLog(`Model training complete. Accuracy: ${(accuracy * 100).toFixed(1)}%`, 'info');
        
        // Enable predictions
        $('#predict-btn').prop('disabled', false);
    }, 2000);
}

function getPredictions() {
    addLog('Generating predictions...', 'info');
    
    // Simulate prediction generation
    setTimeout(function() {
        const signals = ['BUY', 'SELL', 'HOLD'];
        const signal = signals[Math.floor(Math.random() * signals.length)];
        const confidence = (Math.random() * 0.3 + 0.6).toFixed(3); // 60-90%
        
        // Update ML signal card
        $('#ml-signal').text(signal);
        const confidenceElement = $('#ml-confidence');
        confidenceElement.text(`Confidence: ${(confidence * 100).toFixed(1)}%`);
        
        let signalClass = 'signal-hold';
        if (signal === 'BUY') signalClass = 'signal-buy';
        if (signal === 'SELL') signalClass = 'signal-sell';
        
        // Update predictions section
        const predictionsContent = $('#predictions-content');
        predictionsContent.html(`
            <div class="prediction-card ${signalClass}">
                <h3>Latest Prediction</h3>
                <p><strong>Signal:</strong> ${signal}</p>
                <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
                <p><strong>Cryptocurrency:</strong> ${currentCoin.toUpperCase()}</p>
                <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
            </div>
        `);
        
        addLog(`Prediction: ${signal} (Confidence: ${(confidence * 100).toFixed(1)}%)`, 'info');
    }, 1500);
}

function executeTrade(action) {
    const amount = $('#trade-amount').val();
    const testnetMode = $('#testnet-mode').is(':checked');
    
    if (!testnetMode) {
        if (!confirm('WARNING: You are about to execute a REAL trade! Continue?')) {
            return;
        }
    }
    
    addLog(`Executing ${action.toUpperCase()} order for $${amount} (${testnetMode ? 'TESTNET' : 'LIVE'})...`, 'info');
    
    // Simulate trade execution
    setTimeout(function() {
        const status = Math.random() > 0.1 ? 'success' : 'failed';
        
        if (status === 'success') {
            addLog(`${action.toUpperCase()} order executed successfully!`, 'info');
            
            // Add to trading history
            const tbody = $('#trading-table-body');
            if (tbody.find('.empty-state').length > 0) {
                tbody.empty();
            }
            
            const now = new Date();
            const row = $('<tr></tr>');
            row.html(`
                <td>${now.toLocaleString()}</td>
                <td>${currentCoin.toUpperCase()}</td>
                <td>${action.toUpperCase()}</td>
                <td>$${formatNumber(Math.random() * 10000 + 10000)}</td>
                <td>${(Math.random() * 0.1).toFixed(6)}</td>
                <td><span class="change-positive">Completed</span></td>
            `);
            tbody.prepend(row);
        } else {
            addLog(`${action.toUpperCase()} order failed!`, 'error');
        }
    }, 1000);
}

// Utility functions
function formatNumber(num) {
    if (num === null || num === undefined) return '--';
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatLargeNumber(num) {
    if (num === null || num === undefined) return '--';
    
    if (num >= 1e9) {
        return (num / 1e9).toFixed(2) + 'B';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(2) + 'M';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(2) + 'K';
    }
    return num.toFixed(2);
}

function formatPercentage(num) {
    if (num === null || num === undefined) return '--';
    return parseFloat(num).toFixed(2) + '%';
}

// Clean up on page unload
$(window).on('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
