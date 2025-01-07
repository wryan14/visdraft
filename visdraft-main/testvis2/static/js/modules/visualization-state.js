// static/js/modules/visualization-state.js

import { ErrorHandler } from './utils/error-handling.js';
import { DataProcessor } from './utils/data-processing.js';

export class VisualizationState {
    constructor(initialState = {}) {
        this.listeners = new Set();
        this.state = {
            // Visualization metadata
            id: null,
            name: '',
            description: '',
            
            // Data source information
            sourceFile: null,
            rawData: null,
            processedData: null,
            columns: [],
            columnTypes: {},
            
            // Visualization configuration
            chartType: 'line',
            xAxis: null,
            yAxis: null,
            groupBy: null,
            aggregation: 'none',
            
            // Advanced settings
            sortBy: null,
            sortDirection: 'asc',
            topN: null,
            filters: [],
            
            // Plotly-specific configuration
            plotlyConfig: {
                data: [],
                layout: {
                    margin: { t: 30, r: 20, b: 40, l: 60 },
                    autosize: true,
                    showlegend: true
                }
            },
            
            // UI state
            loading: false,
            hasUnsavedChanges: false,
            error: null,
            
            // Override with any initial state
            ...initialState
        };
    }

    // Event subscription management
    subscribe(listener) {
        this.listeners.add(listener);
        // Return unsubscribe function
        return () => this.listeners.delete(listener);
    }

    // State updates
    setState(updates) {
        const oldState = { ...this.state };
        
        // Apply updates
        this.state = {
            ...this.state,
            ...updates,
            hasUnsavedChanges: true
        };

        // Don't mark as unsaved for certain updates
        const nonSaveUpdates = ['loading', 'error'];
        if (Object.keys(updates).every(key => nonSaveUpdates.includes(key))) {
            this.state.hasUnsavedChanges = oldState.hasUnsavedChanges;
        }

        // Process data if necessary
        if (this.shouldProcessData(oldState, this.state)) {
            this.processData();
        }

        this.notifyListeners();
    }

    // Check if data needs reprocessing
    shouldProcessData(oldState, newState) {
        const relevantKeys = [
            'rawData', 'chartType', 'xAxis', 'yAxis', 'groupBy',
            'aggregation', 'sortBy', 'sortDirection', 'topN', 'filters'
        ];

        return relevantKeys.some(key => oldState[key] !== newState[key]);
    }

    // Process data based on current configuration
    async processData() {
        if (!this.state.rawData) return;

        try {
            this.setState({ loading: true });

            const processedData = DataProcessor.processData(this.state.rawData, {
                chartType: this.state.chartType,
                xAxis: this.state.xAxis,
                yAxis: this.state.yAxis,
                groupBy: this.state.groupBy,
                aggregation: this.state.aggregation,
                sortBy: this.state.sortBy,
                sortDirection: this.state.sortDirection,
                topN: this.state.topN,
                filters: this.state.filters
            });

            const plotlyConfig = DataProcessor.formatForPlotly(processedData, {
                chartType: this.state.chartType,
                xAxis: this.state.xAxis,
                yAxis: this.state.yAxis,
                groupBy: this.state.groupBy,
                xAxisType: this.state.columnTypes[this.state.xAxis],
                yAxisType: this.state.columnTypes[this.state.yAxis],
                title: this.state.name
            });

            this.setState({
                processedData,
                plotlyConfig,
                loading: false,
                error: null
            });

        } catch (error) {
            this.setState({
                loading: false,
                error: error.message
            });
            ErrorHandler.handleError(error, 'VisualizationState.processData');
        }
    }

    // Data source methods
    async setDataSource(file) {
        try {
            this.setState({ loading: true });

            let data;
            if (file.name.endsWith('.csv')) {
                data = await DataProcessor.parseCSV(file);
            } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                data = await DataProcessor.parseExcel(file);
            } else {
                throw new Error('Unsupported file type');
            }

            const columns = Object.keys(data[0]);
            const columnTypes = DataProcessor.getColumnTypes(data);

            this.setState({
                sourceFile: file,
                rawData: data,
                columns,
                columnTypes,
                loading: false,
                error: null
            });

        } catch (error) {
            this.setState({
                loading: false,
                error: error.message
            });
            ErrorHandler.handleError(error, 'VisualizationState.setDataSource');
        }
    }

    // Configuration methods
    setVisualizationConfig(config) {
        this.setState({
            chartType: config.chartType ?? this.state.chartType,
            xAxis: config.xAxis ?? this.state.xAxis,
            yAxis: config.yAxis ?? this.state.yAxis,
            groupBy: config.groupBy ?? this.state.groupBy,
            aggregation: config.aggregation ?? this.state.aggregation
        });
    }

    setAdvancedSettings(settings) {
        this.setState({
            sortBy: settings.sortBy ?? this.state.sortBy,
            sortDirection: settings.sortDirection ?? this.state.sortDirection,
            topN: settings.topN ?? this.state.topN,
            filters: settings.filters ?? this.state.filters
        });
    }

    // Export/Import configuration
    exportConfig() {
        const {
            id, name, description, chartType,
            xAxis, yAxis, groupBy, aggregation,
            sortBy, sortDirection, topN, filters,
            plotlyConfig
        } = this.state;

        return {
            id,
            name,
            description,
            config: {
                type: chartType,
                mapping: {
                    x: xAxis,
                    y: yAxis,
                    groupBy,
                    aggregation
                },
                advanced: {
                    sortBy,
                    sortDirection,
                    topN,
                    filters
                },
                plotly: plotlyConfig
            }
        };
    }

    importConfig(config) {
        if (!config) return;

        this.setState({
            id: config.id,
            name: config.name,
            description: config.description,
            chartType: config.config?.type || 'line',
            xAxis: config.config?.mapping?.x,
            yAxis: config.config?.mapping?.y,
            groupBy: config.config?.mapping?.groupBy,
            aggregation: config.config?.mapping?.aggregation || 'none',
            sortBy: config.config?.advanced?.sortBy,
            sortDirection: config.config?.advanced?.sortDirection || 'asc',
            topN: config.config?.advanced?.topN,
            filters: config.config?.advanced?.filters || [],
            plotlyConfig: config.config?.plotly || this.state.plotlyConfig,
            hasUnsavedChanges: false
        });
    }

    // Reset state
    resetState() {
        const preservedKeys = ['id', 'name', 'description'];
        const preserved = {};
        preservedKeys.forEach(key => {
            preserved[key] = this.state[key];
        });

        this.state = {
            ...this.constructor().state,
            ...preserved
        };
        
        this.notifyListeners();
    }

    // Helper methods
    notifyListeners() {
        this.listeners.forEach(listener => {
            try {
                listener(this.state);
            } catch (error) {
                ErrorHandler.handleError(error, 'VisualizationState.notifyListeners');
            }
        });
    }

    getState() {
        return { ...this.state };
    }
}