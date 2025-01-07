// static/js/modules/plotly-manager.js

import { ErrorHandler } from './utils/error-handling.js';

// Import Plotly explicitly
import * as Plotly from 'plotly.js-dist';

// Use global lodash
const _ = window._;

export class PlotlyManager {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['sendDataToCloud', 'lasso2d', 'select2d'],
            displaylogo: false,
            ...options
        };

        this.defaultLayout = {
            margin: { t: 40, r: 20, b: 40, l: 60 },
            autosize: true,
            showlegend: true,
            hovermode: 'closest',
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            font: {
                family: 'Inter, system-ui, sans-serif'
            }
        };

        this.currentChart = null;
        this.pendingUpdate = null;
        this.initializeContainer();
    }

    initializeContainer() {
        if (!this.container) {
            throw new Error('Plot container not found');
        }

        // Set initial dimensions
        this.container.style.minHeight = '400px';
        
        // Add resize observer
        this.resizeObserver = new ResizeObserver(_.debounce(() => {
            if (this.currentChart) {
                Plotly.relayout(this.container, {
                    width: this.container.offsetWidth,
                    height: this.container.offsetHeight
                });
            }
        }, 250));

        this.resizeObserver.observe(this.container);
    }

    async render(config) {
        if (!this.container) return;

        try {
            // Cancel any pending updates
            if (this.pendingUpdate) {
                clearTimeout(this.pendingUpdate);
            }

            // Show loading state
            this.showLoading();

            // Validate configuration
            if (!config || !config.data || !Array.isArray(config.data)) {
                throw new Error('Invalid chart configuration: missing or invalid data');
            }

            // Process configuration
            const processedConfig = this.processConfiguration(config);

            // Delay to ensure loading state is visible
            await new Promise(resolve => setTimeout(resolve, 100));

            // Create new plot
            await Plotly.newPlot(
                this.container,
                processedConfig.data,
                processedConfig.layout,
                this.options
            );

            // Store current configuration
            this.currentChart = processedConfig;

            // Bind events
            this.bindEvents();

            // Hide loading state
            this.hideLoading();

        } catch (error) {
            this.hideLoading();
            ErrorHandler.handleError(error, 'PlotlyManager.render');
            this.showError(error.message);
            throw error; // Re-throw to allow error handling up the chain
        }
    }

    processConfiguration(config) {
        const processedConfig = _.cloneDeep(config);

        // Merge with default layout
        processedConfig.layout = {
            ...this.defaultLayout,
            ...processedConfig.layout
        };

        return processedConfig;
    }

    showLoading() {
        if (!this.container) return;

        // Remove any existing loading overlay
        this.hideLoading();

        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'plot-loading-overlay';
        loadingOverlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;
        loadingOverlay.innerHTML = `
            <div class="flex items-center justify-center h-full">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <span class="ml-2">Loading chart...</span>
            </div>
        `;
        this.container.style.position = 'relative';
        this.container.appendChild(loadingOverlay);
    }

    hideLoading() {
        if (!this.container) return;
        
        const loadingOverlay = this.container.querySelector('.plot-loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }

    showError(message) {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="flex items-center justify-center h-full text-red-600">
                <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>${message}</span>
            </div>
        `;
    }

    destroy() {
        if (this.container) {
            // Remove resize observer
            if (this.resizeObserver) {
                this.resizeObserver.unobserve(this.container);
            }

            // Clean up Plotly
            Plotly.purge(this.container);
            this.currentChart = null;
        }
    }
}