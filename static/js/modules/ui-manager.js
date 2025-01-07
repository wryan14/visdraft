// static/js/modules/ui-manager.js

import { ErrorHandler } from './utils/error-handling.js';

export class UIManager {
    constructor(state, plotlyManager) {
        this.state = state;
        this.plotlyManager = plotlyManager;
        this.elements = this.initializeElements();
        
        this.bindStateUpdates();
        this.bindEvents();
        this.initializeUI();
    }

    initializeElements() {
        return {
            // Metadata elements
            metadata: {
                name: document.getElementById('viz-name'),
                description: document.getElementById('viz-description')
            },

            // File handling elements
            fileUpload: {
                area: document.getElementById('upload-area'),
                input: document.getElementById('file-input')
            },

            // Data mapping elements
            dataMapping: {
                container: document.getElementById('data-mapping'),
                chartType: document.getElementById('viz-type'),
                xAxis: document.getElementById('x-column'),
                yAxis: document.getElementById('y-column'),
                groupBy: document.getElementById('group-by'),
                aggregation: document.getElementById('y-aggregation')
            },

            // Advanced settings
            advanced: {
                container: document.getElementById('advanced-settings'),
                sortColumn: document.getElementById('sort-column'),
                sortDirection: document.getElementById('sort-direction'),
                topN: document.getElementById('top-n')
            },

            // Preview elements
            preview: {
                container: document.getElementById('viz-preview'),
                updateButton: document.getElementById('update-preview-button')
            },

            // Code editor elements
            codeEditor: {
                container: document.getElementById('code-container'),
                textarea: document.getElementById('plotly-json'),
                applyButton: document.getElementById('apply-code-button'),
                toggleButton: document.getElementById('toggle-code-button')
            },

            // Action buttons
            buttons: {
                save: document.getElementById('save-visualization-button')
            },

            // Status elements
            status: {
                save: document.getElementById('save-status')
            }
        };
    }

    bindStateUpdates() {
        // Subscribe to state changes
        this.state.subscribe((newState) => {
            this.updateUIFromState(newState);
        });
    }

    bindEvents() {
        // Metadata events
        if (this.elements.metadata.name) {
            this.elements.metadata.name.addEventListener('change', (e) => {
                this.state.setState({ name: e.target.value });
            });
        }

        if (this.elements.metadata.description) {
            this.elements.metadata.description.addEventListener('change', (e) => {
                this.state.setState({ description: e.target.value });
            });
        }

        // File upload events
        if (this.elements.fileUpload.area) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                this.elements.fileUpload.area.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                this.elements.fileUpload.area.addEventListener(eventName, () => {
                    this.elements.fileUpload.area.classList.add('drag-active');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                this.elements.fileUpload.area.addEventListener(eventName, () => {
                    this.elements.fileUpload.area.classList.remove('drag-active');
                });
            });

            this.elements.fileUpload.area.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length) {
                    this.handleFileUpload(files[0]);
                }
            });
        }

        if (this.elements.fileUpload.input) {
            this.elements.fileUpload.input.addEventListener('change', (e) => {
                if (e.target.files.length) {
                    this.handleFileUpload(e.target.files[0]);
                }
            });
        }

        // Data mapping events
        const mappingElements = this.elements.dataMapping;
        if (mappingElements.chartType) {
            mappingElements.chartType.addEventListener('change', (e) => {
                this.state.setState({ chartType: e.target.value });
            });
        }

        ['xAxis', 'yAxis', 'groupBy'].forEach(key => {
            if (mappingElements[key]) {
                mappingElements[key].addEventListener('change', (e) => {
                    this.state.setState({ [key]: e.target.value });
                });
            }
        });

        if (mappingElements.aggregation) {
            mappingElements.aggregation.addEventListener('change', (e) => {
                this.state.setState({ aggregation: e.target.value });
            });
        }

        // Advanced settings events
        const advancedElements = this.elements.advanced;
        if (advancedElements.sortColumn) {
            advancedElements.sortColumn.addEventListener('change', (e) => {
                this.state.setState({ sortBy: e.target.value });
            });
        }

        if (advancedElements.sortDirection) {
            advancedElements.sortDirection.addEventListener('change', (e) => {
                this.state.setState({ sortDirection: e.target.value });
            });
        }

        if (advancedElements.topN) {
            advancedElements.topN.addEventListener('change', (e) => {
                this.state.setState({ topN: e.target.value ? parseInt(e.target.value) : null });
            });
        }

        // Code editor events
        const codeElements = this.elements.codeEditor;
        if (codeElements.toggleButton) {
            codeElements.toggleButton.addEventListener('click', () => {
                codeElements.container.classList.toggle('hidden');
            });
        }

        if (codeElements.applyButton) {
            codeElements.applyButton.addEventListener('click', () => {
                this.handleCodeUpdate();
            });
        }

        // Save button
        if (this.elements.buttons.save) {
            this.elements.buttons.save.addEventListener('click', () => {
                this.handleSave();
            });
        }
    }

    async handleFileUpload(file) {
        try {
            this.updateUploadAreaUI('uploading', file.name);
            await this.state.setDataSource(file);
            this.updateUploadAreaUI('success', file.name);
            this.elements.dataMapping.container.classList.remove('hidden');
        } catch (error) {
            this.updateUploadAreaUI('error', file.name);
            ErrorHandler.handleError(error, 'UIManager.handleFileUpload');
        }
    }

    updateUploadAreaUI(status, filename) {
        const area = this.elements.fileUpload.area;
        if (!area) return;

        switch (status) {
            case 'uploading':
                area.innerHTML = `
                    <div class="flex items-center space-x-2">
                        <div class="animate-spin rounded-full h-4 w-4 border-2 border-indigo-500"></div>
                        <span>Uploading ${filename}...</span>
                    </div>
                `;
                break;

            case 'success':
                area.innerHTML = `
                    <div class="flex items-center justify-between p-4">
                        <div class="flex items-center space-x-2">
                            <i data-feather="check-circle" class="text-green-500"></i>
                            <span>${filename}</span>
                        </div>
                        <button class="text-gray-500 hover:text-gray-700" onclick="this.resetFileUpload()">
                            <i data-feather="x"></i>
                        </button>
                    </div>
                `;
                break;

            case 'error':
                area.innerHTML = `
                    <div class="flex items-center justify-between p-4 text-red-500">
                        <div class="flex items-center space-x-2">
                            <i data-feather="alert-circle"></i>
                            <span>Error uploading ${filename}</span>
                        </div>
                        <button class="hover:text-red-700" onclick="this.resetFileUpload()">
                            <i data-feather="x"></i>
                        </button>
                    </div>
                `;
                break;

            default:
                this.resetFileUpload();
        }

        // Initialize Feather icons
        if (window.feather) {
            window.feather.replace();
        }
    }

    resetFileUpload() {
        const area = this.elements.fileUpload.area;
        if (!area) return;

        area.innerHTML = `
            <i data-feather="upload" class="w-8 h-8 mx-auto text-gray-400 mb-2"></i>
            <p class="text-sm text-gray-600">
                Drop your data file here or
                <label class="text-indigo-600 hover:text-indigo-500 cursor-pointer">
                    <span>browse</span>
                    <input type="file" class="hidden" id="file-input" accept=".csv,.xlsx,.xls">
                </label>
            </p>
            <p class="text-xs text-gray-500 mt-2">Supports CSV, Excel files</p>
        `;

        if (window.feather) {
            window.feather.replace();
        }

        // Rebind file input event
        const newFileInput = area.querySelector('#file-input');
        if (newFileInput) {
            newFileInput.addEventListener('change', (e) => {
                if (e.target.files.length) {
                    this.handleFileUpload(e.target.files[0]);
                }
            });
        }
    }

    handleCodeUpdate() {
        try {
            const config = JSON.parse(this.elements.codeEditor.textarea.value);
            this.state.setState({ plotlyConfig: config });
        } catch (error) {
            ErrorHandler.handleError(error, 'UIManager.handleCodeUpdate');
        }
    }

    async handleSave() {
        try {
            this.updateSaveStatus('saving');
            const config = this.state.exportConfig();
            await this.saveVisualization(config);
            this.updateSaveStatus('saved');
            
            // Redirect after successful save
            setTimeout(() => {
                window.location.href = '/viz';
            }, 1000);
        } catch (error) {
            this.updateSaveStatus('error');
            ErrorHandler.handleError(error, 'UIManager.handleSave');
        }
    }

    updateSaveStatus(status) {
        const statusEl = this.elements.status.save;
        if (!statusEl) return;

        switch (status) {
            case 'saving':
                statusEl.textContent = 'Saving...';
                break;
            case 'saved':
                statusEl.textContent = 'Saved!';
                break;
            case 'error':
                statusEl.textContent = 'Error saving';
                break;
            default:
                statusEl.textContent = '';
        }
    }

    async saveVisualization(config) {
        const response = await fetch('/viz/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to save visualization');
        }

        return response.json();
    }

    updateUIFromState(state) {
        // Update metadata fields
        if (this.elements.metadata.name) {
            this.elements.metadata.name.value = state.name || '';
        }
        if (this.elements.metadata.description) {
            this.elements.metadata.description.value = state.description || '';
        }

        // Update data mapping fields
        const mappingElements = this.elements.dataMapping;
        if (mappingElements.chartType) {
            mappingElements.chartType.value = state.chartType || 'line';
        }

        // Update column selectors if we have new data
        if (state.columns && state.columns.length > 0) {
            this.updateColumnSelectors(state.columns);
        }

        // Update visualization if we have new config
        if (state.plotlyConfig) {
            this.plotlyManager.render(state.plotlyConfig);
            
            // Update code editor
            if (this.elements.codeEditor.textarea) {
                this.elements.codeEditor.textarea.value = JSON.stringify(state.plotlyConfig, null, 2);
            }
        }

        // Update save button state
        if (this.elements.buttons.save) {
            this.elements.buttons.save.disabled = !state.hasUnsavedChanges;
        }
    }

    updateColumnSelectors(columns) {
        const selectors = ['xAxis', 'yAxis', 'groupBy'];
        selectors.forEach(selector => {
            const element = this.elements.dataMapping[selector];
            if (!element) return;

            // Store current value
            const currentValue = element.value;

            // Clear existing options
            element.innerHTML = '';

            // Add empty option for optional fields
            if (selector !== 'xAxis') {
                const emptyOption = document.createElement('option');
                emptyOption.value = '';
                emptyOption.textContent = '-- Select column --';
                element.appendChild(emptyOption);
            }

            // Add column options
            columns.forEach(column => {
                const option = document.createElement('option');
                option.value = column;
                option.textContent = column;
                element.appendChild(option);
            });

            // Restore previous value if it exists in new columns
            if (columns.includes(currentValue)) {
                element.value = currentValue;
            }
        });
    }

    initializeUI() {
        // Handle initial state if provided
        const initialState = this.state.getState();
        if (initialState.id) {
            this.updateUIFromState(initialState);
        }
    }
}