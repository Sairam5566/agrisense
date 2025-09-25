// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global variables
let currentSection = 'prices';
let allPrices = [];
let selectedState = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Load supported states
    loadSupportedStates();

    // Set up form handlers
    setupFormHandlers();

    // Load initial prices
    loadPrices();
});

// Navigation
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionName).classList.add('active');

    // Update navigation buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    currentSection = sectionName;

    // Load section-specific data
    switch(sectionName) {
        case 'prices':
            loadPrices();
            break;
        case 'trends':
            // Trends will be loaded when user clicks analyze
            break;
        case 'alerts':
            loadAlerts();
            break;
    }
}

// API Helper Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}


// Prices Section
async function loadPrices() {
    const container = document.getElementById('prices-container');
    const loading = document.getElementById('prices-loading');

    loading.style.display = 'block';
    container.innerHTML = '';

    try {
        // Fetch prices for selected state or all states
        let endpoint = '/prices/today';
        if (selectedState) {
            endpoint += `?state=${encodeURIComponent(selectedState)}`;
        }
        const prices = await apiCall(endpoint);
        allPrices = prices;
        displayPrices(prices);

    } catch (error) {
        console.error('Failed to load prices:', error);
        container.innerHTML = '<div class="error">Failed to load prices. Please make sure the backend is running on port 9000.</div>';
    } finally {
        loading.style.display = 'none';
    }
}

async function filterByCommodity() {
    const selectedCommodity = document.getElementById('commodity-filter').value;
    const container = document.getElementById('prices-container');
    const loading = document.getElementById('prices-loading');

    loading.style.display = 'block';
    container.innerHTML = '';

    try {
        let prices;

        if (!selectedCommodity) {
            // Fetch all prices for selected state
            let endpoint = '/prices/today';
            if (selectedState) {
                endpoint += `?state=${encodeURIComponent(selectedState)}`;
            }
            prices = await apiCall(endpoint);
        } else {
            // Fetch prices for specific commodity in selected state
            let endpoint = `/prices/today/${selectedCommodity}`;
            if (selectedState) {
                endpoint += `?state=${encodeURIComponent(selectedState)}`;
            }
            prices = await apiCall(endpoint);
        }

        allPrices = prices;
        displayPrices(prices);

    } catch (error) {
        console.error('Failed to filter prices:', error);
        container.innerHTML = '<div class="error">Failed to load prices. Please try again.</div>';
    } finally {
        loading.style.display = 'none';
    }
}

async function filterByState() {
    selectedState = document.getElementById('state-filter').value;
    // Reload prices with selected state
    await loadPrices();
    // Reset commodity filter
    document.getElementById('commodity-filter').value = '';
}

function displayPrices(prices) {
    const container = document.getElementById('prices-container');
    container.innerHTML = '';

    if (prices.length === 0) {
        container.innerHTML = '<div class="no-data">No price data available</div>';
        return;
    }

    prices.forEach(price => {
        const priceCard = createPriceCard(price);
        container.appendChild(priceCard);
    });
}

function createPriceCard(price) {
    const card = document.createElement('div');
    card.className = 'price-card';

    // Calculate trend percentage (simplified - you might want to implement this properly)
    const trendPercent = price.trend_percent || 0;

    const trendClass = trendPercent >= 0 ? 'positive' : 'negative';
    const trendIcon = trendPercent >= 0 ? '↗️' : '↘️';

    card.innerHTML = `
        <div class="price-header">
            <div class="price-title">${price.commodity}</div>
            <div class="price-badge ${trendClass}">${trendIcon} ${Math.abs(trendPercent).toFixed(1)}%</div>
        </div>
        <div class="price-details">
            <div class="price-item">
                <div class="price-value">₹${price.price}</div>
                <div class="price-label">Current Price</div>
            </div>
            <div class="price-item">
                <div class="price-value">₹${price.min_price} - ₹${price.max_price}</div>
                <div class="price-label">Min - Max</div>
            </div>
        </div>
        <div class="price-location">
            <i class="fas fa-map-marker-alt"></i> ${price.market_name}, ${price.city}, ${price.state}
        </div>
        <div class="price-date">
            <i class="fas fa-clock"></i> Updated: ${new Date(price.date).toLocaleDateString()}
        </div>
    `;

    return card;
}

// Trends Section
async function loadTrends() {
    const container = document.getElementById('trends-container');
    const commodity = document.getElementById('trend-commodity').value;
    const market = document.getElementById('trend-market').value;
    const days = document.getElementById('trend-days').value;

    container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Analyzing trends...</div>';

    try {
        // Fetch historical data for the commodity
        const historicalData = await apiCall(`/prices/history/${commodity}/${days}`);

        // Calculate trend analysis
        let trendPercent = 0;
        let trendDirection = 'stable';
        let currentPrice = 'N/A';
        let previousPrice = 'N/A';

        if (historicalData.length >= 2) {
            const latest = historicalData[0].avg_price;
            const previous = historicalData[1].avg_price;
            trendPercent = ((latest - previous) / previous) * 100;
            trendDirection = trendPercent > 0 ? 'up' : trendPercent < 0 ? 'down' : 'stable';
            currentPrice = latest.toFixed(2);
            previousPrice = previous.toFixed(2);
        } else if (historicalData.length === 1) {
            currentPrice = historicalData[0].avg_price.toFixed(2);
        }

        const trendData = {
            commodity: commodity,
            market: market,
            trend_percent: trendPercent,
            trend_direction: trendDirection,
            current_price: currentPrice,
            previous_price: previousPrice,
            historical_data: historicalData
        };

        displayTrendAnalysis(trendData);

    } catch (error) {
        console.error('Failed to load trend analysis:', error);
        container.innerHTML = '<div class="error">Failed to load trend analysis. Please make sure the backend is running.</div>';
    }
}

function displayTrendAnalysis(trend) {
    const container = document.getElementById('trends-container');

    const trendCard = document.createElement('div');
    trendCard.className = 'trend-card';

    const trendIcon = trend.trend_direction === 'up' ? '📈' : trend.trend_direction === 'down' ? '📉' : '➡️';
    const trendColor = trend.trend_percent > 0 ? '#28a745' : trend.trend_percent < 0 ? '#dc3545' : '#6c757d';

    trendCard.innerHTML = `
        <div class="trend-header">
            <div class="trend-title">${trendIcon} ${trend.commodity} - ${trend.market}</div>
            <div style="color: ${trendColor}; font-weight: bold; font-size: 1.2rem;">
                ${trend.trend_percent > 0 ? '+' : ''}${trend.trend_percent.toFixed(1)}%
            </div>
        </div>

        <div class="trend-metric">
            <div class="metric-item">
                <div class="metric-value">${trend.current_price}</div>
                <div class="metric-label">Current Price</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${trend.previous_price}</div>
                <div class="metric-label">Previous Price</div>
            </div>
            <div class="metric-item">
                <div class="metric-value" style="color: ${trendColor}">
                    ${trend.trend_percent > 0 ? '+' : ''}${trend.trend_percent.toFixed(1)}%
                </div>
                <div class="metric-label">Change</div>
            </div>
        </div>

        <div class="trend-insights">
            <h5>💡 Insights</h5>
            <p>
                ${trend.historical_data.length > 0
                    ? `Historical data available for ${trend.historical_data.length} days.`
                    : 'No historical data available for trend analysis.'
                }
            </p>
        </div>

        <div class="trend-chart">
            <h5>📊 Historical Data Points</h5>
            <div class="price-history">
                ${trend.historical_data.slice(0, 10).map(data => `
                    <div class="history-item">
                        <span class="date">${new Date(data.date).toLocaleDateString()}</span>
                        <span class="price">₹${data.avg_price.toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    container.innerHTML = '';
    container.appendChild(trendCard);
}

// Load supported states for the dropdown
async function loadSupportedStates() {
    try {
        const states = await apiCall('/states');
        const stateFilter = document.getElementById('state-filter');
        
        // Clear existing options except the first one
        stateFilter.innerHTML = '<option value="">All States</option>';
        
        // Add states to the dropdown
        states.forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load supported states:', error);
    }
}

// Search Section
async function performSearch() {
    const commodity = document.getElementById('search-commodity').value;
    const state = document.getElementById('search-state').value;
    const date = document.getElementById('search-date').value;

    const resultsContainer = document.getElementById('search-results');

    if (!commodity && !state && !date) {
        alert('Please enter at least one search criteria');
        return;
    }

    resultsContainer.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';

    try {
        // Build search query
        let searchUrl = `${API_BASE_URL}/prices/search?`;

        if (commodity) {
            searchUrl += `commodity=${encodeURIComponent(commodity)}&`;
        }

        if (state) {
            searchUrl += `state=${encodeURIComponent(state)}&`;
        }

        // Remove trailing & or ?
        searchUrl = searchUrl.slice(0, -1);

        const response = await fetch(searchUrl);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const searchResults = await response.json();

        displaySearchResults(searchResults);

    } catch (error) {
        console.error('Search failed:', error);
        resultsContainer.innerHTML = '<div class="error">Search failed. Please make sure the backend is running.</div>';
    }
}

function clearSearch() {
    document.getElementById('search-commodity').value = '';
    document.getElementById('search-state').value = '';
    document.getElementById('search-date').value = '';
    document.getElementById('search-results').innerHTML = '';
}

function displaySearchResults(results) {
    const container = document.getElementById('search-results');

    if (results.length === 0) {
        container.innerHTML = '<div class="no-data">No results found matching your criteria</div>';
        return;
    }

    const tableHTML = `
        <div class="results-table">
            <table>
                <thead>
                    <tr>
                        <th>Commodity</th>
                        <th>Market</th>
                        <th>Location</th>
                        <th>Price (₹/kg)</th>
                        <th>Min-Max</th>
                        <th>State</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${results.map(result => {
                        const trendClass = 'neutral'; // Simplified
                        const trendIcon = '→';
                        return `
                            <tr>
                                <td><strong>${result.commodity}</strong></td>
                                <td>${result.market_name}</td>
                                <td>${result.city}</td>
                                <td><strong style="color: #28a745;">₹${result.price}</strong></td>
                                <td>₹${result.min_price || 'N/A'} - ₹${result.max_price || 'N/A'}</td>
                                <td><span class="state-badge">${result.state}</span></td>
                                <td>${new Date(result.date).toLocaleDateString()}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = tableHTML;
}

// Alerts Section
async function loadAlerts() {
    const container = document.getElementById('alerts-container');

    container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading alerts...</div>';

    try {
        // Fetch alerts from the API
        const alerts = await apiCall('/alerts');

        if (alerts.length === 0) {
            container.innerHTML = '<div class="no-data">No price alerts set up yet</div>';
            return;
        }

        const alertsHTML = alerts.map(alert => `
            <div class="alert-card">
                <div class="alert-info">
                    <div class="alert-header">
                        <strong>${alert.commodity}</strong>
                        <span class="alert-farmer">Farmer: ${alert.farmer_id}</span>
                    </div>
                    <div class="alert-details">
                        Target: ₹${alert.target_price} |
                        Alert when price goes ${alert.alert_type} |
                        Created: ${new Date(alert.created_at).toLocaleDateString()}
                    </div>
                    <div class="alert-status">
                        <span class="status-badge ${alert.status}">${alert.status}</span>
                    </div>
                </div>
                <div class="alert-actions">
                    <button class="btn-secondary" onclick="deleteAlert(${alert.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = alertsHTML;

    } catch (error) {
        console.error('Failed to load alerts:', error);
        container.innerHTML = '<div class="error">Failed to load alerts. Please make sure the backend is running.</div>';
    }
}

async function createAlert() {
    const farmerId = document.getElementById('alert-farmer-id').value || null;
    const commodity = document.getElementById('alert-commodity').value;
    const targetPrice = parseFloat(document.getElementById('alert-price').value);
    const alertType = document.getElementById('alert-type').value;

    if (!commodity || isNaN(targetPrice)) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const response = await apiCall('/alerts', {
            method: 'POST',
            body: JSON.stringify({
                farmer_id: farmerId,
                commodity: commodity,
                target_price: targetPrice,
                alert_type: alertType
            })
        });

        closeAlertModal();
        loadAlerts();
        alert('Price alert created successfully!');
    } catch (error) {
        console.error('Failed to create alert:', error);
        alert('Failed to create alert. Please make sure the backend is running.');
    }
}

async function deleteAlert(alertId) {
    if (confirm('Are you sure you want to delete this alert?')) {
        try {
            await apiCall(`/alerts/${alertId}`, {
                method: 'DELETE'
            });

            loadAlerts();
            alert('Alert deleted successfully!');
        } catch (error) {
            console.error('Failed to delete alert:', error);
            alert('Failed to delete alert. Please make sure the backend is running.');
        }
    }
}

function showAlertModal() {
    document.getElementById('alert-modal').style.display = 'block';
}

function closeAlertModal() {
    document.getElementById('alert-modal').style.display = 'none';
    document.getElementById('alert-form').reset();
}

function deleteAlert(alertId) {
    if (confirm('Are you sure you want to delete this alert?')) {
        // Sample delete - replace with actual API call
        loadAlerts();
        alert('Alert deleted successfully!');
    }
}

// Form Handlers
function setupFormHandlers() {
    // Alert form submission
    document.getElementById('alert-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        createAlert();
    });

    // Close modal when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('alert-modal');
        if (event.target === modal) {
            closeAlertModal();
        }
    };
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN');
}

// Error handling
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    // You could show a user-friendly error message here
});
