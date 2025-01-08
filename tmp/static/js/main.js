// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
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

// Function to update recent visualizations list
function updateRecentList() {
    fetch('/api/recent')
        .then(response => response.json())
        .then(data => {
            const recentList = document.getElementById('recent-list');
            if (data.visualizations && data.visualizations.length > 0) {
                recentList.innerHTML = data.visualizations
                    .map(viz => `
                        <a href="/viz/${viz.id}" class="list-group-item list-group-item-action">
                            ${viz.name}
                            <small class="text-muted d-block">${viz.chart_type}</small>
                        </a>
                    `)
                    .join('');
            } else {
                recentList.innerHTML = '<div class="list-group-item">No recent visualizations</div>';
            }
        })
        .catch(error => {
            console.error('Error updating recent list:', error);
            recentList.innerHTML = '<div class="list-group-item text-danger">Error loading recent items</div>';
        });
}