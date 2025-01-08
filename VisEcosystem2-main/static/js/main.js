// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is present
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Update recent list if element exists
    const recentList = document.getElementById('recent-list');
    if (recentList) {
        updateRecentList();
    }
});

// Function to safely handle null/undefined values
function safeString(value, fallback = '') {
    return value != null ? String(value) : fallback;
}

// Function to escape HTML and prevent XSS
function escapeHtml(unsafe) {
    if (unsafe == null) return '';
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Function to create a single visualization list item
function createVisualizationListItem(viz) {
    return `
        <a href="/viz/${safeString(viz.id)}" class="list-group-item list-group-item-action">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    ${escapeHtml(safeString(viz.name, 'Unnamed Visualization'))}
                    <small class="text-muted d-block">
                        ${escapeHtml(safeString(viz.chart_type, 'Unknown Type'))}
                    </small>
                </div>
                ${viz.category ? 
                    `<span class="badge bg-secondary">${escapeHtml(safeString(viz.category))}</span>` 
                    : ''}
            </div>
        </a>
    `;
}

// Function to show loading state
function showLoadingState(element) {
    if (!element) return;
    element.innerHTML = `
        <div class="list-group-item">
            <div class="d-flex justify-content-center align-items-center py-3">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span>Loading...</span>
            </div>
        </div>
    `;
}

// Function to show error state
function showErrorState(element, error) {
    if (!element) return;
    element.innerHTML = `
        <div class="list-group-item text-danger">
            <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Error loading items: ${escapeHtml(error.message)}
            </div>
        </div>
    `;
}

function updateRecentList() {
    const recentList = document.getElementById('recent-list');
    if (!recentList) return;

    // Show loading state
    recentList.innerHTML = `
        <div class="list-group-item text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>`;

    fetch('/api/recent')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            if (data.visualizations && Array.isArray(data.visualizations) && data.visualizations.length > 0) {
                recentList.innerHTML = data.visualizations
                    .map(viz => `
                        <a href="/viz/${viz.id}" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${escapeHtml(viz.name || 'Untitled')}</h6>
                                    <small class="text-muted">${escapeHtml(viz.chart_type || 'Unknown Type')}</small>
                                </div>
                                ${viz.category ? 
                                    `<span class="badge bg-secondary">${escapeHtml(viz.category)}</span>` 
                                    : ''}
                            </div>
                        </a>
                    `)
                    .join('');
            } else {
                recentList.innerHTML = `
                    <div class="list-group-item text-center text-muted py-3">
                        <i class="bi bi-info-circle me-2"></i>
                        No visualizations yet
                    </div>`;
            }
        })
        .catch(error => {
            console.error('Error updating recent list:', error);
            recentList.innerHTML = `
                <div class="list-group-item text-danger">
                    <div class="d-flex align-items-center">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <small>Error loading recent items</small>
                    </div>
                </div>`;
        });
}

// Utility function to safely escape HTML
function escapeHtml(unsafe) {
    if (unsafe == null) return '';
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Function to format dates
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}
function selectChartType(element, chartType) {
    // Remove selection from all cards
    document.querySelectorAll('.chart-type-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked card
    element.classList.add('selected');
    
    // Store selected chart type
    selectedChartType = chartType;
    
    // Enable next button
    const nextButton = document.getElementById('next-step');
    if (nextButton) {
        nextButton.disabled = false;
    }

    // Update editor with default config if it exists
    if (editor && defaultConfigs[chartType]) {
        editor.setValue(JSON.stringify(defaultConfigs[chartType], null, 2));
    }
}
// Add global error handling for fetch requests
window.addEventListener('unhandledrejection', function(event) {
    if (event.reason instanceof Error) {
        console.error('Unhandled Promise Rejection:', event.reason);
    }
});