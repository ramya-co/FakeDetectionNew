// Instagram Fake Account Detection - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFormValidation();
    initializeAnimations();
    initializeTooltips();
    initializeProgressBars();
    
    console.log('Instagram Fake Account Detection System loaded successfully');
});

// Form validation and enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

function validateField(field) {
    const isValid = field.checkValidity();
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        hideFieldError(field);
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field);
    }
    
    return isValid;
}

function showFieldError(field) {
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    
    const errorMessage = getFieldErrorMessage(field);
    errorDiv.textContent = errorMessage;
    errorDiv.style.display = 'block';
}

function hideFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function getFieldErrorMessage(field) {
    if (field.validity.valueMissing) {
        return 'This field is required.';
    }
    if (field.validity.typeMismatch) {
        if (field.type === 'email') {
            return 'Please enter a valid email address.';
        }
        if (field.type === 'url') {
            return 'Please enter a valid URL.';
        }
    }
    if (field.validity.patternMismatch) {
        return 'Please match the requested format.';
    }
    if (field.validity.rangeUnderflow) {
        return `Value must be at least ${field.min}.`;
    }
    if (field.validity.rangeOverflow) {
        return `Value must be no more than ${field.max}.`;
    }
    if (field.validity.stepMismatch) {
        return 'Please enter a valid value.';
    }
    if (field.validity.tooShort) {
        return `Please enter at least ${field.minLength} characters.`;
    }
    if (field.validity.tooLong) {
        return `Please enter no more than ${field.maxLength} characters.`;
    }
    
    return 'Please enter a valid value.';
}

// Animation initialization
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });
    
    // Add slide-in animations
    const leftElements = document.querySelectorAll('.slide-left');
    const rightElements = document.querySelectorAll('.slide-right');
    
    leftElements.forEach(function(element, index) {
        element.style.animationDelay = (index * 0.2) + 's';
        element.classList.add('slide-in-left');
    });
    
    rightElements.forEach(function(element, index) {
        element.style.animationDelay = (index * 0.2) + 's';
        element.classList.add('slide-in-right');
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Animate progress bars
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const width = progressBar.style.width;
                progressBar.style.width = '0%';
                
                setTimeout(function() {
                    progressBar.style.width = width;
                }, 100);
                
                observer.unobserve(progressBar);
            }
        });
    });
    
    progressBars.forEach(function(bar) {
        observer.observe(bar);
    });
}

// Utility functions
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.querySelector('.alert-container') || createAlertContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-dismiss
    if (duration > 0) {
        setTimeout(function() {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
    
    return alertDiv;
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1060';
    document.body.appendChild(container);
    return container;
}

function showLoading(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        ${text}
    `;
    element.disabled = true;
    
    return function hideLoading() {
        element.innerHTML = originalContent;
        element.disabled = false;
        element.removeAttribute('data-original-content');
    };
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatPercentage(num, decimals = 1) {
    return num.toFixed(decimals) + '%';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API helper functions
function makeApiCall(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('API call failed:', error);
            throw error;
        });
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Instagram URL validation
function validateInstagramUrl(url) {
    const patterns = [
        /^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9._]{1,30}\/?$/,
        /^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9._]{1,30}\/\?.*$/
    ];
    
    return patterns.some(pattern => pattern.test(url));
}

function extractUsernameFromUrl(url) {
    const match = url.match(/instagram\.com\/([a-zA-Z0-9._]{1,30})/);
    return match ? match[1] : null;
}

// Chart helper functions
function createShapChart(canvasId, shapData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    
    const features = shapData.top_features || [];
    const labels = features.map(f => f.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
    const values = features.map(f => f.importance);
    const colors = values.map(v => v > 0 ? 'rgba(220, 53, 69, 0.8)' : 'rgba(25, 135, 84, 0.8)');
    
    return new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Feature Importance',
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Feature Importance (SHAP Values)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Impact on Prediction'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Features'
                    },
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                bar: {
                    borderRadius: 4
                }
            }
        }
    });
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text)
            .then(() => {
                showAlert('Copied to clipboard!', 'success', 2000);
            })
            .catch(() => {
                fallbackCopyToClipboard(text);
            });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        showAlert('Failed to copy to clipboard', 'error', 3000);
    }
    
    document.body.removeChild(textArea);
}

// Export functionality
function exportResults(data, format = 'json') {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `instagram_analysis_${timestamp}`;
    
    let content, mimeType;
    
    switch (format.toLowerCase()) {
        case 'json':
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
            break;
        case 'csv':
            content = convertToCSV(data);
            mimeType = 'text/csv';
            break;
        default:
            throw new Error('Unsupported export format');
    }
    
    downloadFile(content, `${filename}.${format}`, mimeType);
}

function convertToCSV(data) {
    const headers = Object.keys(data);
    const values = Object.values(data);
    
    return headers.join(',') + '\n' + values.join(',');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

// Mobile detection and optimization
function isMobile() {
    return window.innerWidth <= 768;
}

function optimizeForMobile() {
    if (isMobile()) {
        // Reduce animations on mobile
        document.documentElement.style.setProperty('--animation-duration', '0.3s');
        
        // Simplify hover effects
        const cards = document.querySelectorAll('.analysis-card');
        cards.forEach(card => {
            card.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            card.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            });
        });
    }
}

// Initialize mobile optimizations
window.addEventListener('resize', debounce(optimizeForMobile, 250));
optimizeForMobile();

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    // Could send error reports to a logging service here
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    // Could send error reports to a logging service here
});

// Page visibility handling
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden - pause non-essential activities
        console.log('Page hidden');
    } else {
        // Page is visible - resume activities
        console.log('Page visible');
    }
});

// Service worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export global functions for template usage
window.InstagramDetector = {
    showAlert,
    showLoading,
    formatNumber,
    formatPercentage,
    validateInstagramUrl,
    extractUsernameFromUrl,
    createShapChart,
    copyToClipboard,
    exportResults,
    makeApiCall
};
