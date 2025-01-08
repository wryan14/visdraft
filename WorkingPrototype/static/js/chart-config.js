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
function getChartConfig(chartType) {
    // Get the base config
    let config = JSON.parse(JSON.stringify(defaultConfigs[chartType] || defaultConfigs.line));
    
    // Add some standard configuration options
    config.config = {
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
    };
    
    return config;
}

// Function to update config with actual data
function updateConfigWithData(config, data, xField, yField) {
    if (!data || !xField || !yField) return config;

    const xData = data.map(row => row[xField]);
    const yData = data.map(row => row[yField]);

    if (config.data[0].type === 'histogram') {
        config.data[0].x = xData;
    } else {
        config.data[0].x = xData;
        config.data[0].y = yData;
    }

    // Update axis labels with field names
    config.layout.xaxis.title.text = xField;
    config.layout.yaxis.title.text = yField;

    return config;
}