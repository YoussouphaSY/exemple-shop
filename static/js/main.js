// Shop360 JavaScript Main File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Sidebar toggle for mobile
    const sidebarToggle = document.querySelector('[data-bs-toggle="collapse"]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const sidebar = document.querySelector('#sidebar');
            sidebar.classList.toggle('show');
        });
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Number input formatting
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value && this.step === '0.01') {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Confirm delete modals
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.getAttribute('data-confirm-delete') || 'Êtes-vous sûr de vouloir supprimer cet élément ?';
            if (confirm(message)) {
                if (this.tagName === 'A') {
                    window.location.href = this.href;
                } else if (this.form) {
                    this.form.submit();
                }
            }
        });
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const targetSelector = this.getAttribute('data-search');
            const targets = document.querySelectorAll(targetSelector);
            
            targets.forEach(function(target) {
                const text = target.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    target.style.display = '';
                } else {
                    target.style.display = 'none';
                }
            });
        });
    });

    // Print functionality
    const printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const printSelector = this.getAttribute('data-print');
            if (printSelector) {
                const printContent = document.querySelector(printSelector);
                if (printContent) {
                    const printWindow = window.open('', '_blank');
                    printWindow.document.write(`
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Impression - Shop360</title>
                            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                            <style>
                                body { margin: 20px; }
                                @media print { .no-print { display: none !important; } }
                            </style>
                        </head>
                        <body>
                            ${printContent.outerHTML}
                        </body>
                        </html>
                    `);
                    printWindow.document.close();
                    printWindow.focus();
                    printWindow.print();
                    printWindow.close();
                }
            } else {
                window.print();
            }
        });
    });
});

// Utility functions
const Shop360Utils = {
    // Format currency
    formatCurrency: function(amount, currency = '€') {
        return parseFloat(amount).toFixed(2) + ' ' + currency;
    },

    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR');
    },

    // Show loading spinner
    showLoading: function(element) {
        if (element) {
            element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Chargement...';
            element.disabled = true;
        }
    },

    // Hide loading spinner
    hideLoading: function(element, originalText = 'OK') {
        if (element) {
            element.innerHTML = originalText;
            element.disabled = false;
        }
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1055';
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toastHtml = `
            <div class="toast align-items-center text-bg-${type}" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove toast from DOM after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    },

    // API request helper
    apiRequest: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        };

        const requestOptions = { ...defaultOptions, ...options };
        
        if (requestOptions.headers['Content-Type'] === 'application/json' && requestOptions.body && typeof requestOptions.body !== 'string') {
            requestOptions.body = JSON.stringify(requestOptions.body);
        }

        return fetch(url, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API request failed:', error);
                this.showToast('Une erreur est survenue', 'danger');
                throw error;
            });
    },

    // Get CSRF token
    getCsrfToken: function() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    },

    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }
};

// Make utilities globally available
window.Shop360Utils = Shop360Utils;