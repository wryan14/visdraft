const defaultConfigs = {
    line: {
        data: [{
            type: "scatter",
            mode: "lines+markers",
            x: [], // Will be populated with actual data
            y: [], // Will be populated with actual data
            line: {
                width: 2,
                color: "#2ca02c",
                shape: "linear"
            },
            marker: {
                size: 6,
                symbol: "circle",
                opacity: 0.7
            },
            name: "Series 1"
        }],
        layout: {
            template: "plotly_white",
            title: {
                text: "Line Chart",
                font: { size: 24 }
            },
            xaxis: {
                title: { text: "X Axis", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1",
                zeroline: false
            },
            yaxis: {
                title: { text: "Y Axis", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1",
                zeroline: false
            },
            showlegend: true,
            legend: { x: 1, y: 1 },
            hovermode: "closest",
            plot_bgcolor: "#FFFFFF",
            paper_bgcolor: "#FFFFFF",
            margin: { l: 60, r: 30, b: 60, t: 80 }
        }
    },

    bar: {
        data: [{
            type: "bar",
            x: [], // Will be populated with actual data
            y: [], // Will be populated with actual data
            marker: {
                color: "#1f77b4",
                opacity: 0.8
            },
            name: "Series 1",
            text: [], // For bar labels
            textposition: "auto",
        }],
        layout: {
            template: "plotly_white",
            title: {
                text: "Bar Chart",
                font: { size: 24 }
            },
            xaxis: {
                title: { text: "Categories", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1"
            },
            yaxis: {
                title: { text: "Values", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1"
            },
            showlegend: false,
            bargap: 0.3,
            bargroupgap: 0.1,
            plot_bgcolor: "#FFFFFF",
            paper_bgcolor: "#FFFFFF",
            margin: { l: 60, r: 30, b: 60, t: 80 }
        }
    },

    scatter: {
        data: [{
            type: "scatter",
            mode: "markers",
            x: [], // Will be populated with actual data
            y: [], // Will be populated with actual data
            marker: {
                size: 10,
                color: "#ff7f0e",
                opacity: 0.7,
                line: {
                    color: "white",
                    width: 1
                }
            },
            name: "Points"
        }],
        layout: {
            template: "plotly_white",
            title: {
                text: "Scatter Plot",
                font: { size: 24 }
            },
            xaxis: {
                title: { text: "X Axis", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1",
                zeroline: false
            },
            yaxis: {
                title: { text: "Y Axis", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1",
                zeroline: false
            },
            showlegend: false,
            hovermode: "closest",
            plot_bgcolor: "#FFFFFF",
            paper_bgcolor: "#FFFFFF",
            margin: { l: 60, r: 30, b: 60, t: 80 }
        }
    },

    histogram: {
        data: [{
            type: "histogram",
            x: [], // Will be populated with actual data
            marker: {
                color: "#17becf",
                opacity: 0.7,
                line: {
                    color: "white",
                    width: 0.5
                }
            },
            name: "Distribution",
            autobinx: true,
            histnorm: "", // Can be "", "percent", "probability", "density", "probability density"
        }],
        layout: {
            template: "plotly_white",
            title: {
                text: "Histogram",
                font: { size: 24 }
            },
            xaxis: {
                title: { text: "Values", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1"
            },
            yaxis: {
                title: { text: "Frequency", font: { size: 14 } },
                showgrid: true,
                gridcolor: "#E1E1E1"
            },
            showlegend: false,
            bargap: 0.05,
            plot_bgcolor: "#FFFFFF",
            paper_bgcolor: "#FFFFFF",
            margin: { l: 60, r: 30, b: 60, t: 80 }
        }
    }
};

// Function to get config and format it for the editor
// Advanced configuration templates for each chart type
const advancedConfigs = {
    general: {
        layout: {
            updatemenus: [],
            sliders: [],
            annotations: [],
            shapes: []
        },
        config: {
            scrollZoom: true,
            editable: false,
            staticPlot: false,
            toImageButtonOptions: {
                format: 'png',
                filename: 'custom_chart',
                height: 800,
                width: 1200,
                scale: 2
            },
            modeBarButtonsToAdd: [],
            modeBarButtonsToRemove: []
        }
    },
    line: {
        data: [{
            connectgaps: false,
            fill: 'none',
            line: {
                dash: 'solid',
                shape: 'linear',
                smoothing: 1
            },
            transforms: []
        }]
    },
    bar: {
        data: [{
            orientation: 'v',
            textangle: 0,
            textposition: 'auto',
            transforms: [
                {
                    type: 'sort',
                    enabled: false,
                    target: 'y',
                    order: 'ascending'
                },
                {
                    type: 'aggregate',
                    enabled: false,
                    aggregations: [
                        {target: 'y', func: 'sum', enabled: true}
                    ]
                }
            ]
        }]
    },
    scatter: {
        data: [{
            mode: 'markers',
            transforms: [
                {
                    type: 'groupby',
                    enabled: false,
                    groups: [],
                    styles: []
                }
            ]
        }]
    },
    histogram: {
        data: [{
            histfunc: 'count',
            histnorm: '',
            nbinsx: 0,
            autobinx: true,
            cumulative: {enabled: false},
            transforms: []
        }]
    }
};

function getChartConfig(chartType) {
    // Get the base config
    let config = JSON.parse(JSON.stringify(defaultConfigs[chartType] || defaultConfigs.line));
    
    // Merge with advanced configurations
    const advancedTypeConfig = advancedConfigs[chartType] || {};
    const advancedGeneralConfig = advancedConfigs.general;
    
    // Deep merge the configurations
    config = deepMerge(config, advancedTypeConfig);
    config.config = deepMerge({
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ["lasso2d", "select2d"],
        displaylogo: false,
        toImageButtonOptions: {
            format: 'png',
            filename: chartType + '_chart',
            height: 800,
            width: 1200,
            scale: 2
        }
    }, advancedGeneralConfig.config);
    
    return config;
}

// Helper function for deep merging objects
function deepMerge(target, source) {
    if (!source) return target;
    const output = Object.assign({}, target);
    
    if (isObject(target) && isObject(source)) {
        Object.keys(source).forEach(key => {
            if (isObject(source[key])) {
                if (!(key in target))
                    Object.assign(output, { [key]: source[key] });
                else
                    output[key] = deepMerge(target[key], source[key]);
            } else {
                Object.assign(output, { [key]: source[key] });
            }
        });
    }
    return output;
}

function isObject(item) {
    return (item && typeof item === 'object' && !Array.isArray(item));
}

// Function to strip data from configuration while preserving structure
function stripDataFromConfig(config) {
    const strippedConfig = JSON.parse(JSON.stringify(config));
    if (strippedConfig.data) {
        strippedConfig.data.forEach(trace => {
            // Preserve trace type and style but remove data
            trace.x = [];
            trace.y = [];
            if (trace.text) trace.text = [];
        });
    }
    return strippedConfig;
}

// Function to update config with actual data
function updateConfigWithData(config, data, xField, yField) {
    if (!data || !xField || !yField) return config;

    // Create a deep copy to avoid modifying the original
    const updatedConfig = JSON.parse(JSON.stringify(config));
    const xData = data.map(row => row[xField]);
    const yData = data.map(row => row[yField]);

    if (updatedConfig.data[0].type === 'histogram') {
        updatedConfig.data[0].x = xData;
    } else {
        updatedConfig.data[0].x = xData;
        updatedConfig.data[0].y = yData;
    }

    // Update axis labels with field names
    updatedConfig.layout.xaxis.title.text = xField;
    updatedConfig.layout.yaxis.title.text = yField;

    return updatedConfig;
}