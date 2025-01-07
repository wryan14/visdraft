// static/js/modules/utils/data-processing.js

// Use global objects instead of imports
const _ = window._;
const Papa = window.Papa;

export class DataProcessor {
    static async parseCSV(file) {
        return new Promise((resolve, reject) => {
            Papa.parse(file, {
                header: true,
                dynamicTyping: true,
                skipEmptyLines: true,
                complete: (results) => {
                    if (results.errors.length > 0) {
                        reject(new Error('Error parsing CSV: ' + results.errors[0].message));
                        return;
                    }
                    resolve(results.data);
                },
                error: (error) => reject(error)
            });
        });
    }

    static formatForPlotly(data, config) {
        const { chartType, xAxis, yAxis, groupBy } = config;
        
        // Handle empty or invalid data
        if (!data || !Array.isArray(data) || data.length === 0) {
            return {
                data: [],
                layout: this.getDefaultLayout(config)
            };
        }

        let traces = [];

        if (groupBy) {
            // Create a trace for each group
            const groups = _.groupBy(data, groupBy);
            traces = Object.entries(groups).map(([groupName, groupData]) => ({
                name: groupName,
                x: groupData.map(d => d[xAxis]),
                y: groupData.map(d => d[yAxis]),
                type: this.getPlotlyChartType(chartType),
                mode: this.getPlotlyMode(chartType),
                ...this.getTraceStyle(chartType)
            }));
        } else {
            // Create a single trace
            traces = [{
                x: data.map(d => d[xAxis]),
                y: data.map(d => d[yAxis]),
                type: this.getPlotlyChartType(chartType),
                mode: this.getPlotlyMode(chartType),
                ...this.getTraceStyle(chartType)
            }];
        }

        return {
            data: traces,
            layout: this.getDefaultLayout(config)
        };
    }

    static getPlotlyChartType(chartType) {
        const typeMap = {
            'line': 'scatter',
            'bar': 'bar',
            'scatter': 'scatter',
            'area': 'scatter',
            'histogram': 'histogram',
            'box': 'box',
            'violin': 'violin'
        };

        return typeMap[chartType] || 'scatter';
    }

    static getPlotlyMode(chartType) {
        switch (chartType) {
            case 'scatter':
                return 'markers';
            case 'line':
                return 'lines+markers';
            case 'area':
                return 'lines';
            default:
                return null;
        }
    }

    static getTraceStyle(chartType) {
        const styles = {
            area: {
                fill: 'tozeroy',
                fillcolor: 'rgba(99, 102, 241, 0.2)',
                line: { color: 'rgb(99, 102, 241)' }
            },
            line: {
                line: { width: 2, color: 'rgb(99, 102, 241)' },
                marker: { size: 6 }
            },
            scatter: {
                marker: { 
                    size: 8,
                    color: 'rgb(99, 102, 241)',
                    opacity: 0.7
                }
            },
            bar: {
                marker: {
                    color: 'rgb(99, 102, 241)',
                    opacity: 0.8
                }
            }
        };

        return styles[chartType] || {};
    }

    static getDefaultLayout(config) {
        return {
            title: config.title,
            showlegend: true,
            xaxis: {
                title: config.xAxis,
                type: this.getAxisType(config.xAxisType)
            },
            yaxis: {
                title: config.yAxis,
                type: this.getAxisType(config.yAxisType)
            },
            margin: { t: 30, r: 20, b: 40, l: 60 },
            autosize: true,
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            font: {
                family: 'Inter, system-ui, sans-serif'
            }
        };
    }

    static getAxisType(dataType) {
        switch (dataType) {
            case 'date':
                return 'date';
            case 'number':
                return 'linear';
            default:
                return 'category';
        }
    }

    static processData(data, config) {
        let processedData = [...data];

        // Apply aggregation if specified
        if (config.aggregation && config.aggregation !== 'none') {
            processedData = this.aggregate(processedData, config);
        }

        // Apply sorting if specified
        if (config.sortBy) {
            processedData = _.orderBy(
                processedData, 
                [config.sortBy], 
                [config.sortDirection || 'asc']
            );
        }

        // Apply Top N filter if specified
        if (config.topN) {
            processedData = processedData.slice(0, parseInt(config.topN));
        }

        return processedData;
    }

    static getColumnTypes(data) {
        if (!data || data.length === 0) return {};

        const types = {};
        const sampleRow = data[0];

        Object.keys(sampleRow).forEach(key => {
            const values = data.map(row => row[key]).filter(val => val != null);
            if (values.length === 0) {
                types[key] = 'unknown';
                return;
            }

            const firstValue = values[0];
            if (typeof firstValue === 'number') {
                types[key] = 'number';
            } else if (firstValue instanceof Date) {
                types[key] = 'date';
            } else {
                // Check if all values are valid dates
                const isDate = values.every(val => !isNaN(Date.parse(val)));
                types[key] = isDate ? 'date' : 'string';
            }
        });

        return types;
    }

    static aggregate(data, config) {
        const { yAxis, aggregation, groupBy } = config;
        
        if (!yAxis || !aggregation) return data;

        return _.chain(data)
            .groupBy(groupBy || config.xAxis)
            .map((group, key) => {
                const aggregated = {
                    [config.xAxis]: key
                };

                // Apply the specified aggregation
                switch (aggregation) {
                    case 'sum':
                        aggregated[yAxis] = _.sumBy(group, yAxis);
                        break;
                    case 'avg':
                        aggregated[yAxis] = _.meanBy(group, yAxis);
                        break;
                    case 'min':
                        aggregated[yAxis] = _.minBy(group, yAxis);
                        break;
                    case 'max':
                        aggregated[yAxis] = _.maxBy(group, yAxis);
                        break;
                    case 'count':
                        aggregated[yAxis] = group.length;
                        break;
                    default:
                        aggregated[yAxis] = group[0][yAxis];
                }

                return aggregated;
            })
            .value();
    }
}