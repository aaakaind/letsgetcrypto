// Dashboard JavaScript
let priceChart = null;
let rsiChart = null;
let currentCoin = 'bitcoin';
let refreshInterval = null;
let modelsTrained = false;
let trainingInProgress = false;
const MAX_REQUESTS_PER_MINUTE = 30; // CoinGecko rate limit

// Initialize dashboard on page load
$(document).ready(function() {
    initializeDashboard();
    setupEventHandlers();
    startAutoRefresh();
    displayWelcomeMessage();
});

function initializeDashboard() {
    addLog('🚀 Dashboard initialized - Demo Mode Active', 'info');
    addLog('ℹ️ ML training and trading are simulated for demonstration', 'info');
    updateStatus('connected', 'Connected');
    
    // Initialize charts
    initializeCharts();
    
    // Show loading state
    showLoadingState();
    
    // Load initial data with delay to show loading
    setTimeout(function() {
        loadMarketOverview();
        loadCryptoPrice();
    }, 500);
}

function displayWelcomeMessage() {
    // Create welcome alert after a short delay
    setTimeout(function() {
        const welcomeHtml = `
            <div class="alert alert-info" id="welcome-alert">
                <i class="fas fa-info-circle"></i>
                <div>
                    <strong>Welcome to the LetsGetCrypto Demo!</strong>
                    <p style="margin-top: 0.5rem; font-size: 0.9rem;">
                        Market data is real-time from CoinGecko. ML training and trading features are simulated.
                        <a href="https://github.com/aaakaind/letsgetcrypto" target="_blank" style="color: #1e40af; text-decoration: underline;">
                            Learn more about the full version
                        </a>
                    </p>
                </div>
            </div>
        `;
        $('.dashboard-main').prepend(welcomeHtml);
        
        // Auto-hide after 10 seconds
        setTimeout(function() {
            $('#welcome-alert').fadeOut('slow', function() {
                $(this).remove();
            });
        }, 10000);
    }, 1000);
}

function showLoadingState() {
    $('#current-price').html('<div class="loading-spinner"></div>');
    $('#market-cap').html('<div class="loading-spinner"></div>');
    $('#volume-24h').html('<div class="loading-spinner"></div>');
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
    // Check rate limiting
    if (!checkRateLimit()) {
        addLog('⚠️ Rate limit reached. Please wait before refreshing.', 'error');
        return;
    }
    
    // Direct CoinGecko API call for GitHub Pages
    $.ajax({
        url: 'https://api.coingecko.com/api/v3/coins/markets',
        method: 'GET',
        dataType: 'json',
        data: {
            vs_currency: 'usd',
            order: 'market_cap_desc',
            per_page: 10,
            page: 1,
            sparkline: false
        },
        success: function(data) {
            const marketData = data.map(coin => ({
                name: coin.name,
                symbol: coin.symbol.toUpperCase(),
                price_usd: coin.current_price,
                market_cap_usd: coin.market_cap,
                volume_24h_usd: coin.total_volume,
                price_change_24h_percent: coin.price_change_percentage_24h,
                market_cap_rank: coin.market_cap_rank
            }));
            updateMarketTable(marketData);
            addLog(`✅ Loaded ${data.length} cryptocurrencies`);
            updateStatus('connected', 'Connected');
        },
        error: function(xhr, status, error) {
            handleApiError(xhr, error, 'market data');
        }
    });
}

// Track request timestamps for proper rate limiting
let requestTimestamps = [];

function checkRateLimit() {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;
    
    // Remove requests older than 1 minute
    requestTimestamps = requestTimestamps.filter(timestamp => timestamp > oneMinuteAgo);
    
    if (requestTimestamps.length >= MAX_REQUESTS_PER_MINUTE) {
        return false;
    }
    
    requestTimestamps.push(now);
    return true;
}

function handleApiError(xhr, error, dataType) {
    if (xhr.status === 429) {
        addLog(`⚠️ Rate limit exceeded. Please wait before refreshing ${dataType}.`, 'error');
        updateStatus('disconnected', 'Rate Limited');
        
        // Show rate limit warning
        const warningHtml = `
            <div class="alert alert-warning" id="rate-limit-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                    <strong>API Rate Limit Reached</strong>
                    <p style="margin-top: 0.5rem; font-size: 0.9rem;">
                        CoinGecko's free API has rate limits. Please wait a moment before refreshing.
                        Auto-refresh has been paused temporarily.
                    </p>
                </div>
            </div>
        `;
        
        if ($('#rate-limit-warning').length === 0) {
            $('.dashboard-main').prepend(warningHtml);
            
            // Pause auto-refresh temporarily
            if (refreshInterval) {
                clearInterval(refreshInterval);
                setTimeout(startAutoRefresh, 120000); // Resume after 2 minutes
            }
            
            // Auto-hide warning after 30 seconds
            setTimeout(function() {
                $('#rate-limit-warning').fadeOut('slow', function() {
                    $(this).remove();
                });
            }, 30000);
        }
    } else {
        addLog(`❌ Error loading ${dataType}: ${error}`, 'error');
        updateStatus('disconnected', 'Connection Error');
    }
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
    // Check rate limiting
    if (!checkRateLimit()) {
        addLog('⚠️ Rate limit reached. Please wait before refreshing.', 'error');
        return;
    }
    
    // Direct CoinGecko API call for GitHub Pages
    $.ajax({
        url: `https://api.coingecko.com/api/v3/coins/${currentCoin}`,
        method: 'GET',
        dataType: 'json',
        data: {
            localization: false,
            tickers: false,
            market_data: true,
            community_data: false,
            developer_data: false
        },
        success: function(data) {
            const priceData = {
                price_usd: data.market_data.current_price.usd,
                market_cap_usd: data.market_data.market_cap.usd,
                volume_24h_usd: data.market_data.total_volume.usd,
                price_change_24h_percent: data.market_data.price_change_percentage_24h
            };
            updatePriceStats(priceData);
            addLog(`💰 Updated ${currentCoin.toUpperCase()} price: $${formatNumber(priceData.price_usd)}`);
            
            // Also load history for charts
            loadCryptoHistory();
        },
        error: function(xhr, status, error) {
            handleApiError(xhr, error, `${currentCoin} price`);
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
    
    // Check rate limiting
    if (!checkRateLimit()) {
        return; // Silently skip if rate limited
    }
    
    // Direct CoinGecko API call for GitHub Pages
    $.ajax({
        url: `https://api.coingecko.com/api/v3/coins/${currentCoin}/market_chart`,
        method: 'GET',
        data: {
            vs_currency: 'usd',
            days: days,
            interval: 'daily'
        },
        dataType: 'json',
        success: function(data) {
            // Convert CoinGecko format to our format
            const prices = data.prices.map(item => ({
                timestamp: item[0], // Keep in milliseconds
                price: item[1]
            }));
            updateCharts(prices);
            addLog(`📊 Loaded ${prices.length} historical data points`);
        },
        error: function(xhr, status, error) {
            handleApiError(xhr, error, 'historical data');
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
        const date = new Date(point.timestamp); // Already in milliseconds
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
    if (trainingInProgress) {
        addLog('⚠️ Training already in progress', 'info');
        return;
    }
    
    trainingInProgress = true;
    const trainBtn = $('#train-btn');
    trainBtn.addClass('loading').prop('disabled', true);
    
    addLog('🧠 Training ML models... (Simulated)', 'info');
    addLog('📊 Processing historical data for ' + currentCoin, 'info');
    
    // Show training progress
    const progressHtml = `
        <div class="training-progress" id="training-progress">
            <h4>Training Progress</h4>
            <div class="progress-bar-container">
                <div class="progress-bar" id="training-bar" style="width: 0%"></div>
            </div>
            <div class="status" id="training-status">Initializing models...</div>
        </div>
    `;
    
    const predictionsContent = $('#predictions-content');
    predictionsContent.html(progressHtml);
    
    // Simulate realistic training stages
    const stages = [
        { progress: 20, message: 'Loading historical data...', delay: 500 },
        { progress: 40, message: 'Training Logistic Regression...', delay: 800 },
        { progress: 60, message: 'Training XGBoost model...', delay: 1200 },
        { progress: 80, message: 'Training LSTM neural network...', delay: 1500 },
        { progress: 95, message: 'Validating models...', delay: 800 },
        { progress: 100, message: 'Training complete!', delay: 500 }
    ];
    
    let currentStage = 0;
    
    function runNextStage() {
        if (currentStage >= stages.length) {
            // Training complete
            const accuracy = (Math.random() * 0.15 + 0.75).toFixed(3); // 75-90%
            const precision = (Math.random() * 0.1 + 0.7).toFixed(3); // 70-80%
            const recall = (Math.random() * 0.12 + 0.73).toFixed(3); // 73-85%
            
            addLog(`✅ Model training complete!`, 'info');
            addLog(`📈 Accuracy: ${(accuracy * 100).toFixed(1)}%, Precision: ${(precision * 100).toFixed(1)}%, Recall: ${(recall * 100).toFixed(1)}%`, 'info');
            
            predictionsContent.html(`
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i>
                    <div>
                        <strong>Models trained successfully!</strong>
                        <p style="margin-top: 0.5rem; font-size: 0.9rem;">
                            Accuracy: ${(accuracy * 100).toFixed(1)}% | 
                            Precision: ${(precision * 100).toFixed(1)}% | 
                            Recall: ${(recall * 100).toFixed(1)}%
                        </p>
                        <p style="margin-top: 0.25rem; font-size: 0.85rem; opacity: 0.8;">
                            Note: These are simulated metrics for demonstration purposes.
                        </p>
                    </div>
                </div>
            `);
            
            modelsTrained = true;
            trainingInProgress = false;
            trainBtn.removeClass('loading').prop('disabled', false);
            $('#predict-btn').prop('disabled', false);
            return;
        }
        
        const stage = stages[currentStage];
        $('#training-bar').css('width', stage.progress + '%');
        $('#training-status').text(stage.message);
        addLog(stage.message, 'info');
        
        currentStage++;
        setTimeout(runNextStage, stage.delay);
    }
    
    runNextStage();
}

function getPredictions() {
    if (!modelsTrained) {
        addLog('⚠️ Please train models first', 'info');
        const predictionsContent = $('#predictions-content');
        predictionsContent.html(`
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <div>
                    <strong>Models Not Trained</strong>
                    <p style="margin-top: 0.5rem; font-size: 0.9rem;">
                        Please click "Train Models" before generating predictions.
                    </p>
                </div>
            </div>
        `);
        return;
    }
    
    const predictBtn = $('#predict-btn');
    predictBtn.addClass('loading').prop('disabled', true);
    
    addLog('🔮 Generating predictions...', 'info');
    
    // Simulate prediction generation with realistic delay
    setTimeout(function() {
        // Generate prediction based on recent data (more realistic logic)
        const signals = ['BUY', 'SELL', 'HOLD'];
        const weights = [0.35, 0.25, 0.40]; // Slightly favor HOLD in demo
        const rand = Math.random();
        let signal;
        
        if (rand < weights[0]) {
            signal = 'BUY';
        } else if (rand < weights[0] + weights[1]) {
            signal = 'SELL';
        } else {
            signal = 'HOLD';
        }
        
        const confidence = (Math.random() * 0.25 + 0.65).toFixed(3); // 65-90%
        const predictedChange = (Math.random() * 10 - 5).toFixed(2); // -5% to +5%
        const timeHorizon = Math.random() > 0.5 ? '24 hours' : '7 days';
        
        // Update ML signal card
        $('#ml-signal').text(signal);
        const confidenceElement = $('#ml-confidence');
        confidenceElement.text(`Confidence: ${(confidence * 100).toFixed(1)}%`);
        
        let signalClass = 'signal-hold';
        let signalIcon = 'fas fa-minus-circle';
        let recommendation = '';
        
        if (signal === 'BUY') {
            signalClass = 'signal-buy';
            signalIcon = 'fas fa-arrow-circle-up';
            recommendation = 'Model suggests potential upward price movement.';
        } else if (signal === 'SELL') {
            signalClass = 'signal-sell';
            signalIcon = 'fas fa-arrow-circle-down';
            recommendation = 'Model suggests potential downward price movement.';
        } else {
            recommendation = 'Model suggests waiting for clearer signals.';
        }
        
        // Update predictions section
        const predictionsContent = $('#predictions-content');
        predictionsContent.html(`
            <div class="prediction-card ${signalClass}">
                <h3><i class="${signalIcon}"></i> Latest Prediction</h3>
                <p><strong>Signal:</strong> <span style="font-size: 1.2em;">${signal}</span></p>
                <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
                <p><strong>Cryptocurrency:</strong> ${currentCoin.toUpperCase()}</p>
                <p><strong>Predicted Change:</strong> ${predictedChange > 0 ? '+' : ''}${predictedChange}% over ${timeHorizon}</p>
                <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
                <p style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e5e7eb;">
                    <em>${recommendation}</em>
                </p>
            </div>
            <div class="alert alert-warning" style="margin-top: 1rem;">
                <i class="fas fa-exclamation-triangle"></i>
                <div style="font-size: 0.85rem;">
                    <strong>Disclaimer:</strong> This is a simulated prediction for demonstration purposes only. 
                    Not financial advice. Always do your own research.
                </div>
            </div>
        `);
        
        addLog(`📊 Prediction: ${signal} (Confidence: ${(confidence * 100).toFixed(1)}%)`, 'info');
        addLog(`📈 Predicted ${predictedChange > 0 ? 'increase' : 'decrease'} of ${Math.abs(predictedChange)}% over ${timeHorizon}`, 'info');
        
        predictBtn.removeClass('loading').prop('disabled', false);
    }, 1800);
}

function executeTrade(action) {
    const amount = parseFloat($('#trade-amount').val());
    const testnetMode = $('#testnet-mode').is(':checked');
    
    // Validation
    if (!amount || amount < 10) {
        addLog('⚠️ Minimum trade amount is $10', 'error');
        return;
    }
    
    if (!testnetMode) {
        // Show warning modal for live trading
        showTradeWarningModal(action, amount);
        return;
    }
    
    // Get current price from stats
    const currentPriceText = $('#current-price').text();
    const price = parseFloat(currentPriceText.replace(/[$,]/g, ''));
    
    // Validate price
    if (!price || isNaN(price) || price <= 0) {
        addLog('⚠️ Unable to get current price. Please refresh data first.', 'error');
        return;
    }
    
    const actionBtn = action === 'buy' ? $('#buy-btn') : $('#sell-btn');
    actionBtn.addClass('loading').prop('disabled', true);
    
    addLog(`💰 Executing ${action.toUpperCase()} order for $${amount} (TESTNET MODE)...`, 'info');
    
    // Simulate realistic trade execution delay
    setTimeout(function() {
        const status = Math.random() > 0.05 ? 'success' : 'failed'; // 95% success rate in demo
        
        if (status === 'success') {
            const cryptoAmount = (amount / price).toFixed(6);
            const fee = (amount * 0.001).toFixed(2); // 0.1% fee
            const total = action === 'buy' 
                ? (amount + parseFloat(fee)).toFixed(2) 
                : (amount - parseFloat(fee)).toFixed(2);
            
            addLog(`✅ ${action.toUpperCase()} order executed successfully!`, 'info');
            addLog(`📝 ${action === 'buy' ? 'Bought' : 'Sold'} ${cryptoAmount} ${currentCoin.toUpperCase()} at $${formatNumber(price)}`, 'info');
            addLog(`💵 Fee: $${fee} | ${action === 'buy' ? 'Total cost' : 'Net received'}: $${total}`, 'info');
            
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
                <td><span class="change-${action === 'buy' ? 'positive' : 'negative'}">${action.toUpperCase()}</span></td>
                <td>$${formatNumber(price)}</td>
                <td>${cryptoAmount}</td>
                <td><span class="change-positive">✓ Completed</span></td>
            `);
            tbody.prepend(row);
            
            // Keep only last 10 trades
            if (tbody.children().length > 10) {
                tbody.children().last().remove();
            }
        } else {
            addLog(`❌ ${action.toUpperCase()} order failed! (Simulated failure)`, 'error');
            addLog('⚠️ Please try again or check market conditions', 'error');
        }
        
        actionBtn.removeClass('loading').prop('disabled', false);
    }, 1200);
}

function showTradeWarningModal(action, amount) {
    // Create modal overlay
    const modalHtml = `
        <div class="overlay active" id="trade-warning-modal">
            <div class="modal">
                <h3><i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i> Live Trading Disabled</h3>
                <p style="margin: 1rem 0; color: #666;">
                    This is a demonstration version. Real trading is not available in the GitHub Pages deployment.
                </p>
                <p style="margin: 1rem 0; color: #666;">
                    To enable real trading, please deploy the full application with your own API keys.
                </p>
                <div class="alert alert-info" style="margin: 1rem 0;">
                    <i class="fas fa-info-circle"></i>
                    <div style="font-size: 0.9rem;">
                        <strong>Tip:</strong> You can still test the demo with "Testnet Mode" enabled.
                    </div>
                </div>
                <div class="modal-buttons">
                    <button class="btn btn-primary" onclick="closeTradeWarningModal()">
                        Got it
                    </button>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modalHtml);
}

function closeTradeWarningModal() {
    $('#trade-warning-modal').fadeOut('fast', function() {
        $(this).remove();
    });
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
