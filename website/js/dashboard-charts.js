// Neuro-Genomic AI Dashboard Charts

document.addEventListener('DOMContentLoaded', function() {
    initRawECG();
    initCleanedECG();
    initHRVTrend();
    initRiskGauge();
    initPCACluster();

    // Logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('access_token');
            window.location.href = '../../index.html';
        });
    }
});

// Helper to generate noisy ECG-like data
function generateECGData(points, noiseLevel, isCleaned = false) {
    const data = [];
    for (let i = 0; i < points; i++) {
        let val = Math.sin(i * 0.2) * 0.5;
        // Add periodic peaks
        if (i % 20 === 0) {
            val += 2.0;
        }
        if (!isCleaned) {
            val += (Math.random() - 0.5) * noiseLevel;
        }
        data.push(val);
    }
    return data;
}

function initRawECG() {
    const ctx = document.getElementById('raw-ecg-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: 100}, (_, i) => i),
            datasets: [{
                data: generateECGData(100, 0.4),
                borderColor: '#2c5282',
                borderWidth: 1,
                pointRadius: 0,
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });
}

function initCleanedECG() {
    const ctx = document.getElementById('cleaned-ecg-chart').getContext('2d');
    const data = generateECGData(100, 0, true);
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: 100}, (_, i) => i),
            datasets: [{
                data: data,
                borderColor: '#2c5282',
                borderWidth: 1.5,
                pointRadius: data.map((v, i) => i % 20 === 0 ? 3 : 0),
                pointBackgroundColor: 'red',
                fill: false,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });
}

function initHRVTrend() {
    const ctx = document.getElementById('hrv-trend-chart').getContext('2d');
    const weeks = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30];
    const hrvIndices = [21, 22, 25, 24, 28, 32, 28, 30, 35, 38, 40, 42, 48, 52, 55, 62];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: [{
                label: 'HRV Index',
                data: hrvIndices,
                borderColor: '#2c5282',
                backgroundColor: 'rgba(44, 82, 130, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: '#2c5282'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    title: { display: true, text: 'Weeks', font: { size: 10 } },
                    grid: { display: false }
                },
                y: {
                    title: { display: true, text: 'HRV Index', font: { size: 10 } },
                    min: 0,
                    max: 80
                }
            }
        }
    });
}

function initRiskGauge() {
    const canvas = document.getElementById('risk-gauge');
    const ctx = canvas.getContext('2d');
    
    // Draw semi-circle gauge
    const x = canvas.width / 2;
    const y = canvas.height - 20;
    const radius = 80;
    
    // Draw background arcs
    function drawArc(start, end, color) {
        ctx.beginPath();
        ctx.arc(x, y, radius, start * Math.PI, end * Math.PI);
        ctx.strokeStyle = color;
        ctx.lineWidth = 20;
        ctx.stroke();
    }
    
    // Green (0-0.4), Yellow (0.4-0.7), Red (0.7-1.0)
    // Map to PI values: 1.0 PI is 180deg (left), 2.0 PI is 360deg (right)
    drawArc(1.0, 1.4, '#22c55e'); // Green
    drawArc(1.4, 1.7, '#facc15'); // Yellow
    drawArc(1.7, 2.0, '#ef4444'); // Red
    
    // Draw needle for value 14 (assuming 0-100 scale)
    const normalizedValue = 14 / 100;
    const angle = 1.0 + normalizedValue; // simplified mapping
    
    ctx.beginPath();
    ctx.moveTo(x, y);
    const nx = x + Math.cos(angle * Math.PI) * (radius - 10);
    const ny = y + Math.sin(angle * Math.PI) * (radius - 10);
    ctx.lineTo(nx, ny);
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 4;
    ctx.stroke();
    
    // Center point
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, 2 * Math.PI);
    ctx.fillStyle = '#334155';
    ctx.fill();
    
    // Labels
    ctx.fillStyle = '#64748b';
    ctx.font = '10px Inter';
    ctx.fillText('low', x - radius - 10, y + 15);
    ctx.fillText('normal', x - 15, y - radius - 10);
    ctx.fillText('high', x + radius - 10, y + 15);
}

function initPCACluster() {
    const ctx = document.getElementById('pca-cluster-chart').getContext('2d');
    
    function generatePoints(count, centerX, centerY, spread) {
        return Array.from({length: count}, () => ({
            x: centerX + (Math.random() - 0.5) * spread,
            y: centerY + (Math.random() - 0.5) * spread
        }));
    }

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Normal',
                    data: generatePoints(100, -10, 0, 15),
                    backgroundColor: '#22c55e'
                },
                {
                    label: 'Moderate risk',
                    data: generatePoints(80, 5, 15, 15),
                    backgroundColor: '#facc15'
                },
                {
                    label: 'High risk',
                    data: generatePoints(50, 15, -10, 15),
                    backgroundColor: '#ef4444'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { boxWidth: 10, font: { size: 10 } }
                }
            },
            scales: {
                x: { title: { display: true, text: 'PCA 1', font: { size: 10 } } },
                y: { title: { display: true, text: 'PCA 2', font: { size: 10 } } }
            }
        }
    });
}
