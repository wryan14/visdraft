// static/js/visualization-editor.js

import { VisualizationState } from './modules/visualization-state.js';
import { PlotlyManager } from './modules/plotly-manager.js';
import { FileManager } from './modules/file-manager.js';
import { ErrorHandler } from './modules/utils/error-handling.js';

export class VisualizationEditor {
    constructor(options = {}) {
        this.options = {
            containerId: 'viz-preview',
            initialConfig: null,
            onSave: options.onSave || (() => {}),
            onError: options.onError || ErrorHandler.handleError,
            ...options
        };

        this.initialize();
    }

    async initialize() {
        try {
            // Initialize state management
            this.state = new VisualizationState(this.options.initialConfig);

            // Initialize Plotly manager
            this.plotlyManager = new PlotlyManager(this.options.containerId, {
                onError: this.options.onError
            });

            // Initialize file manager
            this.fileManager = new FileManager({
                onFileLoaded: this.handleFileLoad.bind(this),
                onError: this.options.onError
            });

            // Load initial configuration if available
            if (this.options.initialConfig) {
                await this.loadExistingVisualization(this.options.initialConfig);
            }

            // Set up global error boundary
            window.addEventListener('unhandledrejection', (event) => {
                this.options.onError(event.reason, 'Unhandled Promise Rejection');
            });

        } catch (error) {
            this.options.onError(error, 'VisualizationEditor.initialize');
        }
    }

    async loadExistingVisualization(config) {
        try {
            // If we have a source file, load it first
            if (config.source_file) {
                await this.loadSourceFile(config.source_file);
            }

            // Import the configuration
            this.state.importConfig(config);

        } catch (error) {
            this.options.onError(error, 'VisualizationEditor.loadExistingVisualization');
        }
    }

    async loadSourceFile(filename) {
        try {
            const response = await fetch(`/viz/data/${encodeURIComponent(filename)}`);
            if (!response.ok) {
                throw new Error('Failed to load source file');
            }

            const data = await response.json();
            this.state.setState({
                sourceFile: filename,
                rawData: data.data,
                columns: data.columns
            });

        } catch (error) {
            throw new Error(`Error loading source file: ${error.message}`);
        }
    }

    handleFileLoad(fileData) {
        this.state.setState({
            sourceFile: fileData.filename,
            rawData: fileData.data,
            columns: fileData.columns
        });
    }

    // Public API methods
    async save() {
        try {
            const config = this.state.exportConfig();
            await this.options.onSave(config);
            this.state.setState({ hasUnsavedChanges: false });
            return true;
        } catch (error) {
            this.options.onError(error, 'VisualizationEditor.save');
            return false;
        }
    }

    updateConfig(config) {
        this.state.importConfig(config);
    }

    async exportImage(format = 'png', options = {}) {
        return await this.plotlyManager.exportImage(format, options);
    }

    destroy() {
        this.plotlyManager.destroy();
        if (this.fileManager.destroy) {
            this.fileManager.destroy();
        }
    }
}

// Export an instance creator function
export function createVisualizationEditor(options) {
    return new VisualizationEditor(options);
}