class VisualizationManager {
    constructor() {
        this.initializeEventListeners();
        this.loadVisualizations();
    }

    initializeEventListeners() {
        // Listen for new visualization saves
        document.addEventListener('visualizationSaved', (e) => {
            this.loadVisualizations();
        });

        // Handle the visualization form submission
        const saveForm = document.getElementById('saveVisualizationForm');
        if (saveForm) {
            saveForm.addEventListener('submit', (e) => this.handleVisualizationSave(e));
        }
    }

    async loadVisualizations() {
        try {
            const response = await fetch('/viz/list');
            const data = await response.json();
            this.renderVisualizations(data.visualizations);
        } catch (error) {
            console.error('Error loading visualizations:', error);
            this.showError('Failed to load visualizations');
        }
    }

    renderVisualizations(visualizations) {
        const container = document.getElementById('visualizationsContainer');
        if (!container) return;

        if (!visualizations || visualizations.length === 0) {
            container.innerHTML = this.getEmptyStateHTML();
            return;
        }

        container.innerHTML = visualizations.map(viz => this.getVisualizationCardHTML(viz)).join('');
        
        // Initialize Feather icons
        if (window.feather) {
            feather.replace();
        }

        // Add event listeners to the new cards
        visualizations.forEach(viz => {
            const card = document.getElementById(`viz-${viz.id}`);
            if (card) {
                const deleteBtn = card.querySelector('.delete-viz-btn');
                if (deleteBtn) {
                    deleteBtn.addEventListener('click', (e) => this.handleDelete(e, viz.id));
                }
            }
        });
    }

    getEmptyStateHTML() {
        return `
            <div class="text-center py-12">
                <i data-feather="bar-chart-2" class="w-12 h-12 mx-auto text-gray-400 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-900">No visualizations yet</h3>
                <p class="mt-2 text-sm text-gray-500">Get started by creating your first visualization</p>
                <a href="/viz/create" 
                   class="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
                    Create Visualization
                </a>
            </div>
        `;
    }

    getVisualizationCardHTML(viz) {
        return `
            <div id="viz-${viz.id}" class="bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                <div class="p-4">
                    <div class="flex justify-between items-start">
                        <h3 class="text-lg font-semibold text-gray-900">${viz.name}</h3>
                        <div class="flex space-x-2">
                            <button onclick="window.location.href='/viz/${viz.id}/edit'"
                                    class="text-gray-400 hover:text-indigo-600">
                                <i data-feather="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button class="delete-viz-btn text-gray-400 hover:text-red-600">
                                <i data-feather="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                    
                    <p class="mt-2 text-sm text-gray-600">
                        ${viz.description || 'No description provided'}
                    </p>
                    
                    <div class="mt-4 flex items-center text-sm text-gray-500">
                        <i data-feather="clock" class="w-4 h-4 mr-1"></i>
                        <span>Last updated: ${new Date(viz.updated_at).toLocaleString()}</span>
                    </div>

                    <div class="mt-4 flex items-center text-sm text-gray-500">
                        <i data-feather="${viz.chart_type.toLowerCase()}" class="w-4 h-4 mr-1"></i>
                        <span>${viz.chart_type}</span>
                    </div>

                    <div class="mt-4">
                        <a href="/viz/${viz.id}/edit" 
                           class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200">
                            Open Visualization
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    async handleDelete(e, vizId) {
        e.preventDefault();
        if (!confirm('Are you sure you want to delete this visualization?')) {
            return;
        }

        try {
            const response = await fetch(`/viz/${vizId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Failed to delete visualization');
            }

            // Reload the visualizations
            this.loadVisualizations();
        } catch (error) {
            console.error('Error deleting visualization:', error);
            this.showError('Failed to delete visualization');
        }
    }

    async handleVisualizationSave(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        try {
            const response = await fetch('/viz/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: formData.get('title'),
                    description: formData.get('description'),
                    config: window.currentVisualizationConfig,
                    chart_type: window.currentChartType || 'custom'
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.closeSaveModal();
                window.location.href = '/';
            } else {
                throw new Error(data.error || 'Failed to save visualization');
            }
        } catch (error) {
            console.error('Error saving visualization:', error);
            this.showError(error.message);
        }
    }

    showError(message) {
        // You can implement your preferred error notification method here
        alert(message);
    }

    closeSaveModal() {
        const modal = document.getElementById('saveVisualizationModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
}

// Initialize the visualization manager when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.vizManager = new VisualizationManager();
});