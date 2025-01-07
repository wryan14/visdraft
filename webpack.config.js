const path = require('path');

module.exports = {
    entry: './static/js/visualization-editor.js',
    output: {
        path: path.resolve(__dirname, 'static/dist'),
        filename: 'bundle.js',
        library: {
            name: 'VisualizationEditor',
            type: 'umd',
            export: 'default',
        },
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js']
    },
    externals: {
        'plotly.js-dist': {
            commonjs: 'plotly.js-dist',
            commonjs2: 'plotly.js-dist',
            amd: 'plotly.js-dist',
            root: 'Plotly'
        },
        'lodash': {
            commonjs: 'lodash',
            commonjs2: 'lodash',
            amd: 'lodash',
            root: '_'
        }
    },
    mode: process.env.NODE_ENV || 'development',
    devtool: 'source-map'
};