// Dashboard JavaScript
let priceChart = null;
let rsiChart = null;
let currentCoin = 'bitcoin';
let refreshInterval = null;

// Utility function to escape HTML and prevent XSS attacks
function escapeHtml(text) {
    if (typeof text !== 'string') {
        text = String(text);
    }
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

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
        `<span class="log-time">[${escapeHtml(timeString)}]</span> ` +
        `<span class="${logClass}">${escapeHtml(message)}</span>`
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
        
        // Update predictions section (using escapeHtml to prevent XSS)
        const predictionsContent = $('#predictions-content');
        predictionsContent.html(`
            <div class="prediction-card ${signalClass}">
                <h3>Latest Prediction</h3>
                <p><strong>Signal:</strong> ${escapeHtml(signal)}</p>
                <p><strong>Confidence:</strong> ${escapeHtml((confidence * 100).toFixed(1))}%</p>
                <p><strong>Cryptocurrency:</strong> ${escapeHtml(currentCoin.toUpperCase())}</p>
                <p><strong>Generated:</strong> ${escapeHtml(new Date().toLocaleString())}</p>
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
            // Use escapeHtml to prevent XSS
            row.html(`
                <td>${escapeHtml(now.toLocaleString())}</td>
                <td>${escapeHtml(currentCoin.toUpperCase())}</td>
                <td>${escapeHtml(action.toUpperCase())}</td>
                <td>$${escapeHtml(formatNumber(Math.random() * 10000 + 10000))}</td>
                <td>${escapeHtml((Math.random() * 0.1).toFixed(6))}</td>
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

// ===== Search Functionality =====
let searchResults = [];

$('#search-btn').on('click', function() {
    searchCrypto();
});

$('#search-input').on('keypress', function(e) {
    if (e.which === 13) { // Enter key
        searchCrypto();
    }
});

$('#select-search-result').on('click', function() {
    selectSearchResult();
});

function searchCrypto() {
    const query = $('#search-input').val().trim();
    
    if (!query || query.length < 2) {
        alert('Please enter at least 2 characters to search');
        return;
    }
    
    addLog(`Searching for: ${query}`);
    
    $.ajax({
        url: '/api/search/',
        method: 'GET',
        data: { query: query },
        success: function(response) {
            searchResults = response.results || [];
            displaySearchResults(searchResults);
            addLog(`Found ${searchResults.length} results`);
        },
        error: function(xhr, status, error) {
            addLog(`Search failed: ${error}`, 'error');
            alert('Search failed. Please try again.');
        }
    });
}

function displaySearchResults(results) {
    const select = $('#search-results-select');
    select.empty();
    
    if (results.length === 0) {
        $('#search-results').hide();
        alert('No results found');
        return;
    }
    
    results.forEach(function(coin) {
        const rank = coin.market_cap_rank ? ` (Rank: ${coin.market_cap_rank})` : '';
        select.append(
            $('<option>')
                .val(coin.id)
                .text(`${coin.name} (${coin.symbol})${rank}`)
        );
    });
    
    $('#search-results').show();
}

function selectSearchResult() {
    const selectedId = $('#search-results-select').val();
    
    if (!selectedId) {
        alert('Please select a cryptocurrency from the results');
        return;
    }
    
    // Add to coin selector if not already there
    const coinSelect = $('#coin-select');
    if (coinSelect.find(`option[value="${selectedId}"]`).length === 0) {
        const selectedResult = searchResults.find(r => r.id === selectedId);
        if (selectedResult) {
            coinSelect.append(
                $('<option>')
                    .val(selectedId)
                    .text(`${selectedResult.name} (${selectedResult.symbol})`)
            );
        }
    }
    
    // Select the coin
    coinSelect.val(selectedId);
    currentCoin = selectedId;
    
    // Hide search results
    $('#search-results').hide();
    $('#search-input').val('');
    
    addLog(`Selected: ${selectedId}`);
    
    // Load data for the selected coin
    loadCryptoPrice();
    loadCryptoHistory();
}

// ===== Watchlist Functionality =====
let watchlistRefreshInterval = null;

$('#add-watchlist-btn').on('click', function() {
    addToWatchlist();
});

$('#view-watchlist-btn').on('click', function() {
    viewWatchlist();
});

function addToWatchlist() {
    const coinId = currentCoin;
    
    if (!coinId) {
        alert('Please select a cryptocurrency first');
        return;
    }
    
    addLog(`Adding ${coinId} to watchlist...`);
    
    // Get coin info first
    $.ajax({
        url: `https://api.coingecko.com/api/v3/coins/${coinId}`,
        method: 'GET',
        data: {
            localization: 'false',
            tickers: 'false',
            market_data: 'false',
            community_data: 'false',
            developer_data: 'false'
        },
        success: function(coinData) {
            // Now add to watchlist
            $.ajax({
                url: '/api/watchlist/add/',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    coin_id: coinId,
                    coin_name: coinData.name || coinId,
                    coin_symbol: coinData.symbol || ''
                }),
                success: function(response) {
                    addLog(`Added ${coinData.name} to watchlist`);
                    alert(`${coinData.name} added to watchlist successfully!`);
                    updateWatchlistCount();
                },
                error: function(xhr, status, error) {
                    const errorMsg = xhr.responseJSON?.error || error;
                    addLog(`Failed to add to watchlist: ${errorMsg}`, 'error');
                    
                    if (xhr.status === 409) {
                        alert('This cryptocurrency is already in your watchlist');
                    } else {
                        alert(`Failed to add to watchlist: ${errorMsg}`);
                    }
                }
            });
        },
        error: function(xhr, status, error) {
            addLog(`Failed to get coin info: ${error}`, 'error');
            alert('Failed to get cryptocurrency information');
        }
    });
}

function viewWatchlist() {
    addLog('Loading watchlist...');
    
    $.ajax({
        url: '/api/watchlist/',
        method: 'GET',
        success: function(response) {
            const watchlist = response.watchlist || [];
            
            if (watchlist.length === 0) {
                alert('Your watchlist is empty. Add cryptocurrencies to start monitoring!');
                return;
            }
            
            displayWatchlist(watchlist);
            
            // Show watchlist section
            $('#watchlist-section').show();
            
            // Start auto-refresh for watchlist
            if (watchlistRefreshInterval) {
                clearInterval(watchlistRefreshInterval);
            }
            watchlistRefreshInterval = setInterval(function() {
                refreshWatchlist();
            }, 30000); // Refresh every 30 seconds
            
            addLog(`Loaded ${watchlist.length} watchlist items`);
        },
        error: function(xhr, status, error) {
            addLog(`Failed to load watchlist: ${error}`, 'error');
            alert('Failed to load watchlist');
        }
    });
}

function displayWatchlist(watchlist) {
    const tbody = $('#watchlist-table-body');
    tbody.empty();
    
    if (watchlist.length === 0) {
        tbody.append('<tr><td colspan="7" class="empty-state">No cryptocurrencies in watchlist</td></tr>');
        return;
    }
    
    watchlist.forEach(function(item) {
        const row = $('<tr>');
        
        // Name
        row.append($('<td>').text(item.name));
        
        // Symbol
        row.append($('<td>').text(item.symbol));
        
        // Price
        const price = item.current_price_usd ? `$${formatNumber(item.current_price_usd)}` : 'N/A';
        row.append($('<td>').text(price));
        
        // 24h Change
        const change = item.price_change_24h_percent;
        const changeCell = $('<td>');
        if (change !== null && change !== undefined) {
            const changeText = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
            changeCell.text(changeText);
            changeCell.css('color', change >= 0 ? '#10b981' : '#ef4444');
        } else {
            changeCell.text('N/A');
        }
        row.append(changeCell);
        
        // Market Cap
        const marketCap = item.market_cap_usd ? `$${formatNumber(item.market_cap_usd)}` : 'N/A';
        row.append($('<td>').text(marketCap));
        
        // Last Updated
        const lastUpdated = new Date(item.last_updated).toLocaleTimeString();
        row.append($('<td>').text(lastUpdated));
        
        // Actions
        const actionsCell = $('<td>');
        const loadBtn = $('<button>')
            .addClass('btn btn-sm btn-primary')
            .text('Load')
            .css({'margin-right': '5px', 'padding': '4px 8px', 'font-size': '12px'})
            .on('click', function() {
                loadFromWatchlist(item.id);
            });
        
        const removeBtn = $('<button>')
            .addClass('btn btn-sm btn-danger')
            .text('Remove')
            .css({'padding': '4px 8px', 'font-size': '12px'})
            .on('click', function() {
                removeFromWatchlist(item.id);
            });
        
        actionsCell.append(loadBtn).append(removeBtn);
        row.append(actionsCell);
        
        tbody.append(row);
    });
}

function refreshWatchlist() {
    $.ajax({
        url: '/api/watchlist/',
        method: 'GET',
        success: function(response) {
            const watchlist = response.watchlist || [];
            displayWatchlist(watchlist);
            addLog('Watchlist refreshed');
        },
        error: function(xhr, status, error) {
            console.error('Failed to refresh watchlist:', error);
        }
    });
}

function loadFromWatchlist(coinId) {
    // Add to coin selector if not already there
    const coinSelect = $('#coin-select');
    if (coinSelect.find(`option[value="${coinId}"]`).length === 0) {
        // Get coin info to add proper label
        $.ajax({
            url: `https://api.coingecko.com/api/v3/coins/${coinId}`,
            method: 'GET',
            data: {
                localization: 'false',
                tickers: 'false',
                market_data: 'false',
                community_data: 'false',
                developer_data: 'false'
            },
            success: function(coinData) {
                coinSelect.append(
                    $('<option>')
                        .val(coinId)
                        .text(`${coinData.name} (${coinData.symbol.toUpperCase()})`)
                );
                selectCoin(coinId);
            },
            error: function() {
                // Add with just the ID if we can't get the name
                coinSelect.append(
                    $('<option>')
                        .val(coinId)
                        .text(coinId)
                );
                selectCoin(coinId);
            }
        });
    } else {
        selectCoin(coinId);
    }
}

function selectCoin(coinId) {
    $('#coin-select').val(coinId);
    currentCoin = coinId;
    addLog(`Loaded: ${coinId}`);
    loadCryptoPrice();
    loadCryptoHistory();
}

function removeFromWatchlist(coinId) {
    if (!confirm('Remove this cryptocurrency from your watchlist?')) {
        return;
    }
    
    $.ajax({
        url: `/api/watchlist/remove/${coinId}/`,
        method: 'DELETE',
        success: function(response) {
            addLog(`Removed from watchlist: ${coinId}`);
            refreshWatchlist();
            updateWatchlistCount();
        },
        error: function(xhr, status, error) {
            addLog(`Failed to remove from watchlist: ${error}`, 'error');
            alert('Failed to remove from watchlist');
        }
    });
}

function updateWatchlistCount() {
    $.ajax({
        url: '/api/watchlist/',
        method: 'GET',
        success: function(response) {
            const count = response.count || 0;
            $('#watchlist-count').text(count);
        },
        error: function(xhr, status, error) {
            console.error('Failed to update watchlist count:', error);
        }
    });
}

// Initialize watchlist count on load
updateWatchlistCount();

// Clean up on page unload
$(window).on('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    if (watchlistRefreshInterval) {
        clearInterval(watchlistRefreshInterval);
    }
});
