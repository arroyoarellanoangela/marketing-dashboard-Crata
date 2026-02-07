/* ==========================================================================
   CRATA AI - Growth Intelligence Dashboard
   Main JavaScript
   ========================================================================== */

// ===== UTILITY FUNCTIONS =====

/**
 * Format number with locale
 */
function formatNumber(num, locale = 'es-ES') {
    if (num === undefined || num === null || isNaN(num)) return '--';
    return new Intl.NumberFormat(locale).format(num);
}

/**
 * Format percentage
 */
function formatPercent(num, decimals = 1) {
    if (num === undefined || num === null || isNaN(num)) return '--';
    return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
}

/**
 * Format duration (seconds to minutes:seconds)
 */
function formatDuration(seconds) {
    if (!seconds || isNaN(seconds)) return '--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format date
 */
function formatDate(dateString, format = 'short') {
    if (!dateString) return '--';
    const date = new Date(dateString);
    const options = format === 'short' 
        ? { day: '2-digit', month: 'short' }
        : { day: '2-digit', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('es-ES', options);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== API FUNCTIONS =====

/**
 * Fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

/**
 * POST request helper
 */
async function postAPI(endpoint, data) {
    return fetchAPI(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// ===== CHART HELPERS =====

/**
 * Common chart layout configuration
 */
function getChartLayout(title = '', options = {}) {
    return {
        title: {
            text: title,
            font: {
                family: 'Space Grotesk',
                size: 14,
                color: 'rgba(255,255,255,0.9)'
            }
        },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: {
            family: 'Outfit',
            color: 'rgba(255,255,255,0.8)'
        },
        margin: { l: 50, r: 30, t: title ? 40 : 20, b: 40 },
        xaxis: {
            gridcolor: 'rgba(108, 168, 164, 0.1)',
            linecolor: 'rgba(108, 168, 164, 0.2)',
            tickcolor: 'rgba(108, 168, 164, 0.2)',
            tickfont: { size: 11 },
            ...options.xaxis
        },
        yaxis: {
            gridcolor: 'rgba(108, 168, 164, 0.1)',
            linecolor: 'rgba(108, 168, 164, 0.2)',
            tickcolor: 'rgba(108, 168, 164, 0.2)',
            tickfont: { size: 11 },
            ...options.yaxis
        },
        legend: {
            orientation: 'h',
            y: -0.15,
            font: { size: 11 },
            ...options.legend
        },
        showlegend: options.showlegend !== false,
        ...options
    };
}

/**
 * Chart color palette
 */
const chartColors = {
    primary: '#6CA8A4',
    primaryDark: '#1D4744',
    accent: '#FFD700',
    success: '#4CAF50',
    danger: '#f44336',
    purple: '#9C27B0',
    blue: '#2196F3',
    orange: '#FF9800',
    gradient: ['#6CA8A4', '#1D4744', '#FFD700', '#f44336', '#9C27B0', '#2196F3', '#FF9800']
};

/**
 * Create line chart trace
 */
function createLineTrace(data, xKey, yKey, name, color = chartColors.primary) {
    return {
        x: data.map(d => d[xKey]),
        y: data.map(d => d[yKey]),
        type: 'scatter',
        mode: 'lines+markers',
        name: name,
        line: { color: color, width: 2 },
        marker: { size: 4 }
    };
}

/**
 * Create bar chart trace
 */
function createBarTrace(data, xKey, yKey, name, color = chartColors.primary, orientation = 'v') {
    const trace = {
        type: 'bar',
        name: name,
        marker: { color: typeof color === 'string' ? color : color }
    };
    
    if (orientation === 'h') {
        trace.x = data.map(d => d[yKey]);
        trace.y = data.map(d => d[xKey]);
        trace.orientation = 'h';
    } else {
        trace.x = data.map(d => d[xKey]);
        trace.y = data.map(d => d[yKey]);
    }
    
    return trace;
}

/**
 * Create pie chart trace
 */
function createPieTrace(labels, values, colors = chartColors.gradient) {
    return {
        labels: labels,
        values: values,
        type: 'pie',
        hole: 0.4,
        marker: { colors: colors },
        textinfo: 'label+percent',
        textposition: 'outside'
    };
}

// ===== UI HELPERS =====

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.add('active');
        } else {
            overlay.classList.remove('active');
        }
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if doesn't exist
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    // Create toast
    const toast = document.createElement('div');
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#FF9800',
        info: '#6CA8A4'
    };
    
    toast.style.cssText = `
        padding: 1rem 1.5rem;
        background: ${colors[type] || colors.info};
        color: white;
        border-radius: 8px;
        font-family: 'Outfit', sans-serif;
        font-size: 0.9rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease;
        cursor: pointer;
    `;
    toast.textContent = message;
    toast.onclick = () => toast.remove();
    
    container.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Update KPI element with animation
 */
function updateKPI(elementId, value, format = 'number') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let formattedValue;
    switch (format) {
        case 'number':
            formattedValue = formatNumber(value);
            break;
        case 'percent':
            formattedValue = formatPercent(value);
            break;
        case 'duration':
            formattedValue = formatDuration(value);
            break;
        default:
            formattedValue = value;
    }
    
    // Animate value change
    element.style.opacity = '0';
    element.style.transform = 'translateY(-10px)';
    
    setTimeout(() => {
        element.textContent = formattedValue;
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 200);
}

/**
 * Update delta indicator
 */
function updateDelta(elementId, value) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const isPositive = value >= 0;
    element.className = `kpi-delta ${isPositive ? 'positive' : 'negative'}`;
    element.innerHTML = `<span>${isPositive ? '↑' : '↓'}</span> ${Math.abs(value).toFixed(1)}%`;
}

// ===== EVENT LISTENERS =====

/**
 * Setup sidebar toggle for mobile
 */
function setupMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

/**
 * Setup smooth scroll
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input');
            if (searchInput) searchInput.focus();
        }
        
        // Escape: Close modals/sidebars
        if (e.key === 'Escape') {
            const sidebar = document.querySelector('.sidebar.open');
            if (sidebar) sidebar.classList.remove('open');
        }
    });
}

// ===== INITIALIZATION =====

document.addEventListener('DOMContentLoaded', () => {
    setupMobileMenu();
    setupSmoothScroll();
    setupKeyboardShortcuts();
    
    // Add CSS for toast animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        @keyframes slideOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
    `;
    document.head.appendChild(style);
});

// ===== EXPORT FOR MODULES =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatNumber,
        formatPercent,
        formatDuration,
        formatDate,
        debounce,
        throttle,
        fetchAPI,
        postAPI,
        getChartLayout,
        chartColors,
        createLineTrace,
        createBarTrace,
        createPieTrace,
        showLoading,
        showToast,
        updateKPI,
        updateDelta
    };
}

