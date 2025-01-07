// static/js/modules/utils/error-handling.js

export class ErrorHandler {
    static showToast(message, type = 'error') {
        const template = document.getElementById('error-toast-template');
        if (!template) return;

        const toast = template.content.cloneNode(true);
        const messageEl = toast.querySelector('.error-message');
        if (messageEl) {
            messageEl.textContent = message;
        }

        document.body.appendChild(toast);

        // Initialize Feather icons in the toast
        if (window.feather) {
            window.feather.replace();
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            const toastEl = document.querySelector('.fixed.top-4.right-4');
            if (toastEl) {
                toastEl.remove();
            }
        }, 5000);
    }

    static handleError(error, context = '') {
        console.error(`Error in ${context}:`, error);
        this.showToast(error.message || 'An unexpected error occurred');
    }

    static wrapAsync(fn, context = '') {
        return async (...args) => {
            try {
                return await fn(...args);
            } catch (error) {
                this.handleError(error, context);
                throw error;
            }
        };
    }
}

export function withErrorHandling(target, context = '') {
    return new Proxy(target, {
        get(target, prop) {
            if (typeof target[prop] === 'function') {
                return ErrorHandler.wrapAsync(target[prop].bind(target), `${context}.${prop}`);
            }
            return target[prop];
        }
    });
}