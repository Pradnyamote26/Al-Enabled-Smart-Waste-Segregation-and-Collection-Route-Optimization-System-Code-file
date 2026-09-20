let categoryChart = null;
let binStatusChart = null;

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        if (data.success) {
            renderKPICards(data.summary);
            renderCategoryChart(data.chart_category);
            renderBinStatusChart(data.chart_bin_status);
            renderRecentDetectionsTable(data.recent_detections);
            renderUrgentBinsList(data.urgent_bins);
            renderLatestRouteSummary(data.latest_route);
        }
    } catch (err) {
        console.error('Error fetching dashboard statistics:', err);
    }
}

function renderKPICards(summary) {
    document.getElementById('dashScans').textContent = summary.total_detections;
    document.getElementById('dashRecycling').textContent = `${summary.recycling_rate_percent}%`;
    document.getElementById('dashBins').textContent = summary.total_bins;
    document.getElementById('dashUrgent').textContent = summary.overflown_bins;
}

function renderCategoryChart(chartData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) categoryChart.destroy();

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.counts,
                backgroundColor: chartData.colors,
                borderColor: '#1e293b',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } }
                }
            }
        }
    });
}

function renderBinStatusChart(chartData) {
    const ctx = document.getElementById('binStatusChart').getContext('2d');

    if (binStatusChart) binStatusChart.destroy();

    binStatusChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Number of Bins',
                data: chartData.counts,
                backgroundColor: chartData.colors,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                    grid: { color: '#334155' }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                    grid: { color: '#334155' }
                }
            }
        }
    });
}

function renderRecentDetectionsTable(detections) {
    const tbody = document.getElementById('dashDetectionsBody');

    if (!detections || detections.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center">No AI scans recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = detections.map(d => `
        <tr>
            <td><img src="${d.image_path}" class="thumb-img" alt="scan"></td>
            <td><strong>${d.category_name}</strong></td>
            <td><span class="type-tag">${d.waste_type}</span></td>
            <td><span class="badge-${d.bin_color.toLowerCase()}">${d.bin_color} Bin</span></td>
            <td>${(d.confidence_score * 100).toFixed(1)}%</td>
            <td class="text-sm text-muted">${d.detected_at}</td>
        </tr>
    `).join('');
}

function renderUrgentBinsList(bins) {
    const container = document.getElementById('urgentBinsList');

    if (!bins || bins.length === 0) {
        container.innerHTML = `<p class="text-muted">All municipal bins are within normal fill levels (<60%).</p>`;
        return;
    }

    container.innerHTML = bins.map(b => `
        <div class="urgent-bin-item">
            <div>
                <strong>${b.location_name}</strong>
                <div class="text-sm text-muted">Priority: ${b.priority}/5 | Weight: ${b.current_weight_kg} kg</div>
            </div>
            <span class="fill-pill fill-${b.current_fill_level >= 90 ? 'red' : 'yellow'}">${b.current_fill_level}% Full</span>
        </div>
    `).join('');
}

function renderLatestRouteSummary(route) {
    const container = document.getElementById('routeSummaryContent');

    if (!route) {
        container.innerHTML = `<p class="text-muted">No collection route calculated yet. Go to <a href="/routes" class="link-sm">Route Optimizer</a> to generate a plan.</p>`;
        return;
    }

    container.innerHTML = `
        <div class="route-metrics-compact">
            <div><span>Distance:</span> <strong>${route.total_distance_km} km</strong></div>
            <div><span>Est. Time:</span> <strong>${route.estimated_time_mins} mins</strong></div>
            <div><span>Est. Fuel:</span> <strong>${route.fuel_used_liters} L</strong></div>
            <div><span>Visited Bins:</span> <strong>${route.visited_bins_count} Stops</strong></div>
        </div>
        <div class="text-sm text-muted" style="margin-top:0.5rem;">Calculated at: ${route.created_at}</div>
    `;
}
