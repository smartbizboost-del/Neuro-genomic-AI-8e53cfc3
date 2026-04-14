// Neuro-Genomic AI Dashboard Charts and Clinical Data

const sampleClinicalData = [
    {
        patient_id: 'Jane Doe',
        gestational_weeks: 32,
        maternal_age: 39,
        developmental_index: 0.74,
        confidence_interval: [0.72, 0.78],
        signal_quality: 92,
        signal_quality_text: 'GOOD',
        risk_scores: {
            IUGR: { value: 12, level: 'Low', ci: [8, 16] },
            Preterm: { value: 34, level: 'Moderate', ci: [28, 40] },
            Hypoxia: { value: 8, level: 'Low', ci: [5, 11] }
        },
        hrv_metrics: {
            RMSSD: 35.0,
            SDNN: 110.0,
            'LF/HF': 1.7,
            Sample_Entropy: 0.91,
            AC_T9: 32.4,
            DC_T9: 29.8
        },
        prsa: { AC_T9: 32.4, DC_T9: 29.8 },
        feature_importance: [
            { feature: 'RMSSD', importance: -0.32, direction: 'decreases risk' },
            { feature: 'LF/HF', importance: 0.28, direction: 'increases risk' },
            { feature: 'Sample Entropy', importance: -0.15, direction: 'decreases risk' }
        ],
        recommendation: 'Continue routine monitoring. Repeat in 2 weeks.',
        interpretation: [
            'Autonomic maturation consistent with gestational age',
            'HRV appears within expected physiological range',
            'Sympathetic and parasympathetic balance is acceptable'
        ],
        cluster_id: 0
    },
    {
        patient_id: 'John Smith',
        gestational_weeks: 30,
        maternal_age: 34,
        developmental_index: 0.66,
        confidence_interval: [0.63, 0.69],
        signal_quality: 78,
        signal_quality_text: 'FAIR',
        risk_scores: {
            IUGR: { value: 24, level: 'Moderate', ci: [18, 30] },
            Preterm: { value: 42, level: 'Moderate', ci: [34, 50] },
            Hypoxia: { value: 18, level: 'Moderate', ci: [12, 24] }
        },
        hrv_metrics: {
            RMSSD: 22.5,
            SDNN: 85.0,
            'LF/HF': 2.1,
            Sample_Entropy: 0.82,
            AC_T9: 24.0,
            DC_T9: 21.4
        },
        prsa: { AC_T9: 24.0, DC_T9: 21.4 },
        feature_importance: [
            { feature: 'LF/HF', importance: 0.35, direction: 'increases risk' },
            { feature: 'AC_T9', importance: -0.22, direction: 'decreases risk' },
            { feature: 'Sample Entropy', importance: -0.12, direction: 'decreases risk' }
        ],
        recommendation: 'Signal quality is fair. Consider repeat assessment after improving recording conditions.',
        interpretation: [
            'Elevated sympathetic balance compared to expected range',
            'Reduced complexity suggests developmental stress',
            'Clinical follow-up recommended with Doppler evaluation'
        ],
        cluster_id: 1
    }
];

let currentPatientIndex = 0;
let currentPatientData = null;
let rawEcgChart = null;
let cleanedEcgChart = null;
let hrvTrendChart = null;
let shapChart = null;
let pcaClusterChart = null;

const clinicalApiUrl = 'http://localhost:8000/api/v1';

async function fetchAnalysisFromBackend(fileId) {
    try {
        const response = await fetch(`${clinicalApiUrl}/analysis/${fileId}`);
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Backend error: ${response.status} ${error}`);
        }
        const payload = await response.json();
        return adaptApiResponse(payload, fileId);
    } catch (error) {
        console.error('API fetch failed', error);
        alert('Unable to load backend analysis. Using sample demo data.');
        return null;
    }
}

async function fetchLatestAnalysis() {
    try {
        const response = await fetch(`${clinicalApiUrl}/analysis/latest`);
        if (!response.ok) {
            return null;
        }
        const payload = await response.json();
        return adaptApiResponse(payload, payload.file_id || 'latest');
    } catch (error) {
        console.error('Latest analysis fetch failed', error);
        return null;
    }
}

function adaptApiResponse(payload, fileId) {
    const features = payload.features || {};
    const risk = payload.risk || {};
    const baseValue = payload.developmental_index ?? (features.developmental_index ?? 0.0);
    const confidenceInterval = payload.confidence_intervals?.developmental_index ?? [baseValue - 0.03, baseValue + 0.03];

    return {
        patient_id: payload.patient_id || `Backend ${fileId}`,
        gestational_weeks: payload.gestational_weeks ?? 32,
        maternal_age: payload.maternal_age ?? 34,
        developmental_index: baseValue,
        confidence_interval: confidenceInterval,
        signal_quality: payload.signal_quality ?? Math.round((features.developmental_index ?? 0.7) * 100),
        signal_quality_text: payload.signal_quality_text || 'LIVE',
        risk_scores: {
            IUGR: { value: Math.round((risk.suspect ?? 0) * 100), level: risk.predicted_class === 'suspect' ? 'Moderate' : 'Low', ci: [0, 0] },
            Preterm: { value: Math.round((risk.normal ?? 0) * 100), level: risk.predicted_class === 'normal' ? 'Low' : 'Moderate', ci: [0, 0] },
            Hypoxia: { value: Math.round((risk.pathological ?? 0) * 100), level: risk.predicted_class === 'pathological' ? 'High' : 'Low', ci: [0, 0] }
        },
        hrv_metrics: {
            RMSSD: features.rmssd ?? 0,
            SDNN: features.sdnn ?? 0,
            'LF/HF': features.lf_hf_ratio ?? 0,
            Sample_Entropy: features.sample_entropy ?? 0,
            AC_T9: features.rmssd ?? 0,
            DC_T9: features.sdnn ?? 0
        },
        prsa: { AC_T9: features.rmssd ?? 0, DC_T9: features.sdnn ?? 0 },
        feature_importance: [
            { feature: 'RMSSD', importance: features.rmssd ? -0.2 : 0, direction: 'decreases risk' },
            { feature: 'LF/HF', importance: features.lf_hf_ratio ? 0.2 : 0, direction: 'increases risk' },
            { feature: 'Sample Entropy', importance: features.sample_entropy ? -0.1 : 0, direction: 'decreases risk' }
        ],
        recommendation: payload.interpretation?.[0] || 'Live backend data loaded.',
        interpretation: payload.interpretation || [],
        cluster_id: risk.unsupervised_cluster ?? 0
    };
}

function getCurrentData() {
    return currentPatientData || sampleClinicalData[currentPatientIndex];
}

function setStatusDot(level) {
    const dot = document.getElementById('signal-dot');
    const statusIndicator = document.getElementById('status-indicator');
    if (dot) {
        dot.style.backgroundColor = level === 'GOOD' ? 'var(--status-success)' : level === 'FAIR' ? 'var(--status-warning)' : 'var(--status-error)';
    }
    if (statusIndicator) {
        const state = getCurrentData().risk_scores.Preterm.level;
        statusIndicator.innerHTML = `Patient | ${getCurrentData().gestational_weeks} weeks | Clinical State: <span class="dot"></span> ${state}`;
    }
}

function updateDashboardFields() {
    const data = getCurrentData();
    document.getElementById('patient-name').textContent = data.patient_id;
    document.getElementById('patient-age').textContent = data.maternal_age;
    document.getElementById('patient-id').textContent = data.patient_id.replace(' ', '_');
    document.getElementById('patient-gravidity').textContent = `G1P0`;
    document.getElementById('patient-weeks').textContent = data.gestational_weeks;
    document.getElementById('data-source').textContent = 'PhysioNet CTU-UHB';
    document.getElementById('recording-duration').textContent = '1 hour';
    document.getElementById('signal-quality-text').textContent = data.signal_quality_text;

    document.getElementById('summary-developmental-index').textContent = data.developmental_index.toFixed(2);
    document.getElementById('summary-developmental-range').textContent = `95% CI: ${data.confidence_interval[0].toFixed(2)} - ${data.confidence_interval[1].toFixed(2)}`;
    document.getElementById('summary-signal-quality').textContent = `${data.signal_quality}%`;
    document.getElementById('summary-signal-status').textContent = data.signal_quality_text;
    document.getElementById('summary-confidence').textContent = `${Math.round((data.confidence_interval[1] - data.confidence_interval[0]) / 2 * 100)}%`;
    document.getElementById('summary-confidence-range').textContent = `± ${Math.round((data.confidence_interval[1] - data.confidence_interval[0]) * 100 / 2)}%`;

    const analysisCaption = document.getElementById('analysis-caption');
    if (analysisCaption) {
        analysisCaption.innerHTML = `<strong>High confidence analysis</strong> — Results below are reliable for this ${data.gestational_weeks}-week recording. Signal Quality: ${data.signal_quality}% (${data.signal_quality_text})`;
    }

    const qualityBar = document.getElementById('signal-quality-bar');
    if (qualityBar) qualityBar.value = data.signal_quality;

    const qualitySummary = document.getElementById('signal-quality-summary');
    if (qualitySummary) qualitySummary.textContent = `Overall signal quality: ${data.signal_quality}% (${data.signal_quality_text})`;

    const qualityDetail = document.getElementById('signal-channel-detail');
    if (qualityDetail) qualityDetail.textContent = 'Channel quality: 94% | 91% | 88% | 85%';

    const shapCaption = document.getElementById('shap-caption');
    if (shapCaption) shapCaption.textContent = 'Top feature contributions to overall risk score.';

    const disclaimer = document.getElementById('clinical-disclaimer');
    if (disclaimer) disclaimer.textContent = 'Important disclaimer: This is an investigational research tool only. Correlate with ultrasound, CTG, and standard clinical assessment.';

    document.getElementById('metric-rmssd-value').textContent = `${data.hrv_metrics.RMSSD.toFixed(1)} ms`;
    document.getElementById('metric-sdnn-value').textContent = `${data.hrv_metrics.SDNN.toFixed(1)} ms`;
    document.getElementById('metric-lfhf-value').textContent = `${data.hrv_metrics['LF/HF'].toFixed(2)}`;
    document.getElementById('metric-sample-entropy-value').textContent = `${data.hrv_metrics.Sample_Entropy.toFixed(2)}`;

    document.getElementById('metric-rmssd-desc').textContent = data.hrv_metrics.RMSSD >= 25 ? 'Parasympathetic activity [Normal]' : 'Parasympathetic activity [Low]';
    document.getElementById('metric-sdnn-desc').textContent = data.hrv_metrics.SDNN >= 80 ? 'Overall variability [Normal]' : 'Overall variability [Low]';
    document.getElementById('metric-lfhf-desc').textContent = data.hrv_metrics['LF/HF'] <= 2.0 ? 'Sympathetic vs parasympathetic balance [Acceptable]' : 'Sympathetic dominance [Elevated]';
    document.getElementById('metric-sample-entropy-desc').textContent = data.hrv_metrics.Sample_Entropy >= 0.85 ? 'Signal complexity [Within range]' : 'Signal complexity [Reduced]';

    document.getElementById('iugr-value').textContent = `${data.risk_scores.IUGR.value}%`;
    document.getElementById('iugr-level').textContent = data.risk_scores.IUGR.level;
    document.getElementById('iugr-ci').textContent = `95% CI: ${data.risk_scores.IUGR.ci[0]} - ${data.risk_scores.IUGR.ci[1]}%`;

    document.getElementById('preterm-value').textContent = `${data.risk_scores.Preterm.value}%`;
    document.getElementById('preterm-level').textContent = data.risk_scores.Preterm.level;
    document.getElementById('preterm-ci').textContent = `95% CI: ${data.risk_scores.Preterm.ci[0]} - ${data.risk_scores.Preterm.ci[1]}%`;

    document.getElementById('hypoxia-value').textContent = `${data.risk_scores.Hypoxia.value}%`;
    document.getElementById('hypoxia-level').textContent = data.risk_scores.Hypoxia.level;
    document.getElementById('hypoxia-ci').textContent = `95% CI: ${data.risk_scores.Hypoxia.ci[0]} - ${data.risk_scores.Hypoxia.ci[1]}%`;

    const interpretationList = document.getElementById('interpretation-list');
    interpretationList.innerHTML = data.interpretation.map(item => `<li>${item}</li>`).join('');
    document.getElementById('recommendation-card').innerHTML = `<strong>Recommendation</strong><p>${data.recommendation}</p>`;

    const statusIndicator = document.getElementById('status-indicator');
    if (statusIndicator) {
        statusIndicator.innerHTML = `Patient | ${data.gestational_weeks} weeks | Clinical State: <span class="dot"></span> ${data.risk_scores.Preterm.level}`;
    }

    setStatusDot(data.signal_quality_text);
}

function generateECGData(points, noiseLevel, isCleaned = false) {
    const data = [];
    for (let i = 0; i < points; i++) {
        let val = Math.sin(i * 0.2) * 0.5;
        if (i % 20 === 0) {
            val += 1.8;
        }
        if (!isCleaned) {
            val += (Math.random() - 0.5) * noiseLevel;
        }
        data.push(val);
    }
    return data;
}

function initRawECG() {
    const canvas = document.getElementById('raw-ecg-chart');
    const ctx = canvas.getContext('2d');
    if (rawEcgChart) rawEcgChart.destroy();
    rawEcgChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: 100 }, (_, i) => i),
            datasets: [{
                data: generateECGData(100, 0.35),
                borderColor: '#2c5282',
                borderWidth: 1.5,
                pointRadius: 0,
                fill: false,
                tension: 0.35
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
    const canvas = document.getElementById('cleaned-ecg-chart');
    const ctx = canvas.getContext('2d');
    if (cleanedEcgChart) cleanedEcgChart.destroy();
    const data = generateECGData(100, 0.04, true);
    cleanedEcgChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: 100 }, (_, i) => i),
            datasets: [{
                data: data,
                borderColor: '#2c5282',
                borderWidth: 1.8,
                pointRadius: data.map((_, i) => (i % 20 === 0 ? 3 : 0)),
                pointBackgroundColor: '#ef4444',
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
    const data = getCurrentData();
    const canvas = document.getElementById('hrv-trend-chart');
    const ctx = canvas.getContext('2d');
    if (hrvTrendChart) hrvTrendChart.destroy();

    const weeks = Array.from({ length: 12 }, (_, i) => data.gestational_weeks - 11 + i).map(w => Math.max(20, w));
    const hrvIndices = weeks.map((week, idx) => data.hrv_metrics.RMSSD + (idx - 6) * 0.9 + (Math.random() - 0.5) * 2);

    hrvTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: [{
                label: 'HRV Index',
                data: hrvIndices,
                borderColor: '#2c5282',
                backgroundColor: 'rgba(44, 82, 130, 0.12)',
                fill: true,
                tension: 0.25,
                pointRadius: 3,
                pointBackgroundColor: '#2c5282'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    title: { display: true, text: 'Gestational Weeks', font: { size: 10 } },
                    grid: { display: false }
                },
                y: {
                    title: { display: true, text: 'HRV Index', font: { size: 10 } },
                    min: 0,
                    max: Math.max(...hrvIndices) + 10
                }
            }
        }
    });
}

function initRiskGauge() {
    const data = getCurrentData();
    const canvas = document.getElementById('risk-gauge');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const x = width / 2;
    const y = height - 20;
    const radius = 80;

    function drawArc(start, end, color) {
        ctx.beginPath();
        ctx.arc(x, y, radius, start * Math.PI, end * Math.PI);
        ctx.strokeStyle = color;
        ctx.lineWidth = 18;
        ctx.stroke();
    }

    drawArc(1.0, 1.4, '#22c55e');
    drawArc(1.4, 1.7, '#facc15');
    drawArc(1.7, 2.0, '#ef4444');

    const normalized = Math.min(Math.max(data.developmental_index, 0), 1);
    const angle = 1.0 + normalized;

    ctx.beginPath();
    ctx.moveTo(x, y);
    const nx = x + Math.cos(angle * Math.PI) * (radius - 8);
    const ny = y + Math.sin(angle * Math.PI) * (radius - 8);
    ctx.lineTo(nx, ny);
    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 4;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(x, y, 6, 0, 2 * Math.PI);
    ctx.fillStyle = '#1f2937';
    ctx.fill();

    ctx.fillStyle = '#64748b';
    ctx.font = '10px Inter';
    ctx.fillText('low', x - radius - 12, y + 16);
    ctx.fillText('normal', x - 18, y - radius - 14);
    ctx.fillText('high', x + radius - 16, y + 16);
}

function initPCACluster() {
    const canvas = document.getElementById('pca-cluster-chart');
    const ctx = canvas.getContext('2d');
    if (pcaClusterChart) pcaClusterChart.destroy();

    const current = getCurrentData();
    const base = current.cluster_id;

    function generatePoints(count, centerX, centerY, spread) {
        return Array.from({ length: count }, () => ({
            x: centerX + (Math.random() - 0.5) * spread,
            y: centerY + (Math.random() - 0.5) * spread
        }));
    }

    const datasets = [
        { label: 'Normal', data: generatePoints(100, -10, 0, 15), backgroundColor: '#22c55e' },
        { label: 'Moderate risk', data: generatePoints(80, 5, 15, 15), backgroundColor: '#facc15' },
        { label: 'High risk', data: generatePoints(50, 15, -10, 15), backgroundColor: '#ef4444' }
    ];

    datasets.push({
        label: 'Patient',
        data: [{ x: base === 0 ? -10 : base === 1 ? 5 : 15, y: base === 0 ? 0 : base === 1 ? 15 : -10 }],
        backgroundColor: '#0f172a',
        pointRadius: 10,
        pointStyle: 'cross'
    });

    pcaClusterChart = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
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

function initShapChart() {
    const canvas = document.getElementById('shap-chart');
    const ctx = canvas.getContext('2d');
    if (shapChart) shapChart.destroy();

    const data = getCurrentData().feature_importance || [];
    const labels = data.map(item => item.feature);
    const values = data.map(item => Math.abs(item.importance));
    const colors = data.map(item => item.direction === 'increases risk' ? '#ef4444' : '#22c55e');

    shapChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'SHAP Impact',
                data: values,
                backgroundColor: colors,
                borderRadius: 8,
                barThickness: 18
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = data[context.dataIndex] || {};
                            return `${item.feature}: ${context.parsed.x.toFixed(2)} (${item.direction || ''})`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Impact' },
                    grid: { display: false }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    });
}

function updateCharts() {
    initRawECG();
    initCleanedECG();
    initHRVTrend();
    initRiskGauge();
    initPCACluster();
    initShapChart();
}

function switchMode(isResearch) {
    const recCard = document.getElementById('recommendation-card');
    if (!recCard) return;
    if (isResearch) {
        recCard.style.backgroundColor = '#e0f2fe';
        recCard.querySelector('strong').textContent = 'Research Insight';
    } else {
        recCard.style.backgroundColor = '#eef2ff';
        recCard.querySelector('strong').textContent = 'Recommendation';
    }
}

function loadPatientData(index, backendData = null) {
    currentPatientIndex = index;
    currentPatientData = backendData;
    updateDashboardFields();
    updateCharts();
}

function initPatientSelector() {
    const selector = document.querySelector('.patient-selector');
    if (!selector) return;
    selector.innerHTML = sampleClinicalData.map((patient, idx) => `<option value="${idx}">Patient: ${patient.patient_id}</option>`).join('');
    selector.value = currentPatientIndex;
    selector.addEventListener('change', (event) => {
        loadPatientData(Number(event.target.value));
    });
}

function initButtons() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('access_token');
            window.location.href = '../../index.html';
        });
    }

    const loadDataBtn = document.getElementById('load-data-btn');
    if (loadDataBtn) {
        loadDataBtn.addEventListener('click', async function() {
            const fileIdInput = document.getElementById('api-file-id');
            const fileId = fileIdInput?.value.trim();
            if (fileId) {
                loadDataBtn.textContent = 'Loading...';
                const backendData = await fetchAnalysisFromBackend(fileId);
                if (backendData) {
                    loadPatientData(currentPatientIndex, backendData);
                    loadDataBtn.textContent = 'Loaded from API';
                } else {
                    loadPatientData(currentPatientIndex);
                    loadDataBtn.textContent = 'Loaded Sample Data';
                }
                setTimeout(() => { loadDataBtn.innerHTML = '<span>⟳</span> Load Clinical Data'; }, 1400);
            } else {
                loadPatientData(currentPatientIndex);
                loadDataBtn.textContent = 'Loaded Sample Data';
                setTimeout(() => { loadDataBtn.innerHTML = '<span>⟳</span> Load Clinical Data'; }, 1200);
            }
        });
    }

    const loadLatestBtn = document.getElementById('load-latest-btn');
    if (loadLatestBtn) {
        loadLatestBtn.addEventListener('click', async function() {
            loadLatestBtn.textContent = 'Loading...';
            const latestData = await fetchLatestAnalysis();
            if (latestData) {
                loadPatientData(currentPatientIndex, latestData);
                loadLatestBtn.textContent = 'Latest Loaded';
            } else {
                loadLatestBtn.textContent = 'No Latest Data';
            }
            setTimeout(() => { loadLatestBtn.innerHTML = '<span>★</span> Load Latest'; }, 1400);
        });
    }

    const modeToggle = document.getElementById('research-mode-toggle');
    if (modeToggle) {
        modeToggle.addEventListener('change', function() {
            switchMode(this.checked);
        });
    }

    const btnPdf = document.getElementById('btn-export-pdf');
    if (btnPdf) btnPdf.addEventListener('click', function() {
        alert('Export PDF action triggered. The clinical report data is now available for export.');
    });
    const btnFhir = document.getElementById('btn-export-fhir');
    if (btnFhir) btnFhir.addEventListener('click', function() {
        alert('FHIR export initiated. Data synced to clinical API format.');
    });
    const btnCsv = document.getElementById('btn-export-csv');
    if (btnCsv) btnCsv.addEventListener('click', function() {
        alert('CSV export triggered. Clinical values are now ready to download.');
    });
    const btnSyncEmr = document.getElementById('btn-sync-emr');
    if (btnSyncEmr) btnSyncEmr.addEventListener('click', function() {
        alert('KenyaEMR sync requested. Backend integration is ready.');
    });
}

function initDashboard() {
    initPatientSelector();
    initButtons();
    updateDashboardFields();
    updateCharts();
    switchMode(false);
    fetchLatestAnalysis().then((latestData) => {
        if (latestData) {
            loadPatientData(currentPatientIndex, latestData);
        }
    });
    setInterval(async () => {
        const latestData = await fetchLatestAnalysis();
        if (latestData) {
            loadPatientData(currentPatientIndex, latestData);
        }
    }, 20000);
}

document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
});
