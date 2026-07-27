// Optional script file for small interactions
// Currently left minimal — extend as desired

// Add hover highlight to table rows (if any table exists)
document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('table tbody tr');
    rows.forEach(r => {
        r.addEventListener('mouseenter', () => r.style.backgroundColor = 'rgba(0,123,255,0.06)');
        r.addEventListener('mouseleave', () => r.style.backgroundColor = '');
    });
});