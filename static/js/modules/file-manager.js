// static/js/modules/file-manager.js

import { ErrorHandler } from './utils/error-handling.js';
import { DataProcessor } from './utils/data-processing.js';

export class FileManager {
    constructor(options = {}) {
        this.options = {
            onFileLoaded: options.onFileLoaded || (() => {}),
            onError: options.onError || ErrorHandler.handleError,
            maxFileSize: options.maxFileSize || 50 * 1024 * 1024, // 50MB default
            allowedTypes: options.allowedTypes || ['.csv', '.xlsx', '.xls']
        };

        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        
        if (this.uploadArea) {
            this.initializeDropZone();
        }
        if (this.fileInput) {
            this.initializeFileInput();
        }
    }

    initializeDropZone() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.add('drag-active');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.remove('drag-active');
            });
        });

        this.uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length) {
                this.handleFiles(files[0]);
            }
        });
    }

    initializeFileInput() {
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                this.handleFiles(e.target.files[0]);
            }
        });
    }

    async handleFiles(file) {
        try {
            // Validate file
            this.validateFile(file);

            // Show uploading state
            this.updateUploadAreaUI('uploading', file.name);

            // Process file based on type
            let data;
            if (file.name.endsWith('.csv')) {
                data = await DataProcessor.parseCSV(file);
            } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
                data = await DataProcessor.parseExcel(file);
            }

            // Upload to server
            const uploadedFile = await this.uploadFile(file);

            // Show success state
            this.updateUploadAreaUI('success', file.name);

            // Call success callback with processed data
            this.options.onFileLoaded({
                filename: uploadedFile.filename,
                data: data,
                columns: Object.keys(data[0] || {}),
                columnTypes: DataProcessor.getColumnTypes(data)
            });

        } catch (error) {
            this.updateUploadAreaUI('error', file.name);
            this.options.onError(error, 'FileManager.handleFiles');
        }
    }

    validateFile(file) {
        // Check file size
        if (file.size > this.options.maxFileSize) {
            throw new Error(`File size (${(file.size / (1024*1024)).toFixed(2)}MB) exceeds the maximum limit of ${(this.options.maxFileSize / (1024*1024))}MB`);
        }

        // Check file type
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.options.allowedTypes.includes(fileExtension)) {
            throw new Error(`File type ${fileExtension} is not supported. Supported types: ${this.options.allowedTypes.join(', ')}`);
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/viz/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Upload failed');
        }

        return await response.json();
    }

    updateUploadAreaUI(status, filename) {
        if (!this.uploadArea) return;

        switch (status) {
            case 'uploading':
                this.uploadArea.innerHTML = `
                    <div class="flex items-center space-x-2">
                        <div class="animate-spin rounded-full h-4 w-4 border-2 border-indigo-500"></div>
                        <span class="text-sm text-gray-600">Uploading ${filename}...</span>
                    </div>
                `;
                break;

            case 'success':
                this.uploadArea.innerHTML = `
                    <div class="flex items-center justify-between p-4">
                        <div class="flex items-center space-x-2">
                            <i data-feather="check-circle" class="text-green-500"></i>
                            <span class="text-sm font-medium text-gray-900">${filename}</span>
                        </div>
                        <button class="text-gray-500 hover:text-gray-700" onclick="this.resetUpload()">
                            <i data-feather="x"></i>
                        </button>
                    </div>
                `;
                break;

            case 'error':
                this.uploadArea.innerHTML = `
                    <div class="flex items-center justify-between p-4 text-red-500">
                        <div class="flex items-center space-x-2">
                            <i data-feather="alert-circle"></i>
                            <span class="text-sm">Error uploading ${filename}</span>
                        </div>
                        <button class="hover:text-red-700" onclick="this.resetUpload()">
                            <i data-feather="x"></i>
                        </button>
                    </div>
                `;
                break;

            default:
                this.resetUpload();
        }

        // Initialize Feather icons
        if (window.feather) {
            window.feather.replace();
        }
    }

    resetUpload() {
        if (!this.uploadArea) return;

        this.uploadArea.innerHTML = `
            <i data-feather="upload-cloud" class="w-12 h-12 mx-auto text-gray-400"></i>
            <p class="mt-2 text-sm text-gray-600">
                Drag and drop your file here or
                <button type="button" class="text-indigo-600 hover:text-indigo-500 focus:outline-none focus:underline">
                    browse
                </button>
            </p>
            <p class="mt-1 text-xs text-gray-500">
                CSV, Excel files up to ${(this.options.maxFileSize / (1024*1024))}MB
            </p>
            <input id="file-input" type="file" class="hidden" accept="${this.options.allowedTypes.join(',')}">
        `;

        // Reinitialize Feather icons
        if (window.feather) {
            window.feather.replace();
        }

        // Rebind file input
        const newFileInput = this.uploadArea.querySelector('input[type="file"]');
        if (newFileInput) {
            newFileInput.addEventListener('change', (e) => {
                if (e.target.files.length) {
                    this.handleFiles(e.target.files[0]);
                }
            });
        }
    }

    destroy() {
        // Clean up any event listeners or resources
        if (this.uploadArea) {
            this.uploadArea.innerHTML = '';
        }
        if (this.fileInput) {
            this.fileInput.value = '';
        }
    }
}