let map = null;
let markers = [];
let routePolyline = null;

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadLocations();
});

function initMap() {
    // Default center: Pune Municipal Depot Coordinates
    const defaultCenter = [18.5204, 73.8567];
    map = L.map('map').setView(defaultCenter, 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Add Depot Marker
    const depotIcon = L.divIcon({
        className: 'custom-depot-marker',
        html: '<div style="background:#ef4444; color:white; border-radius:50%; width:30px; height:30px; display:flex; align-items:center; justify-content:center; font-weight:bold; border:2px solid white; box-shadow:0 2px 6px rgba(0,0,0,0.4);">🚩</div>',
        iconSize: [30, 30]
    });

    L.marker(defaultCenter, { icon: depotIcon })
        .addTo(map)
        .bindPopup('<b>Central Waste Depot</b><br>Starting & Ending Point');
}

async function loadLocations() {
    try {
        const response = await fetch('/api/locations');
        const data = await response.json();

        if (data.success) {
            renderLocationMarkers(data.locations);
            renderLocationsCompactList(data.locations);
        }
    } catch (err) {
        console.error('Error loading locations:', err);
    }
}

function renderLocationMarkers(locations) {
    // Clear existing markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    locations.forEach(loc => {
        let color = '#10b981'; // Green (Normal)
        if (loc.current_fill_level >= 90) {
            color = '#ef4444'; // Red (Overflown)
        } else if (loc.current_fill_level >= 60) {
            color = '#f59e0b'; // Yellow (Needs collection)
        }

        const binIcon = L.divIcon({
            className: 'custom-bin-marker',
            html: `<div style="background:${color}; color:white; border-radius:50%; width:26px; height:26px; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:bold; border:2px solid white; box-shadow:0 2px 5px rgba(0,0,0,0.3);">${loc.id}</div>`,
            iconSize: [26, 26]
        });

        const marker = L.marker([loc.latitude, loc.longitude], { icon: binIcon })
            .addTo(map)
            .bindPopup(`
                <b>${loc.location_name}</b><br>
                Fill Level: <strong>${loc.current_fill_level}%</strong><br>
                Weight: ${loc.current_weight_kg} kg<br>
                Priority: ${loc.priority}/5
            `);

        markers.push(marker);
    });
}

function renderLocationsCompactList(locations) {
    const container = document.getElementById('locationsList');
    if (!locations || locations.length === 0) {
        container.innerHTML = '<p class="text-muted">No collection points defined yet.</p>';
        return;
    }

    container.innerHTML = locations.map(loc => `
        <div class="bin-item-row">
            <div>
                <strong>${loc.location_name}</strong>
                <span class="text-muted text-sm"> (${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)})</span>
            </div>
            <div class="bin-item-meta">
                <span class="fill-pill fill-${getFillClass(loc.current_fill_level)}">${loc.current_fill_level}%</span>
                <button onclick="deleteLocation(${loc.id})" class="btn-delete" title="Delete Point">🗑️</button>
            </div>
        </div>
    `).join('');
}

function getFillClass(fill) {
    if (fill >= 90) return 'red';
    if (fill >= 60) return 'yellow';
    return 'green';
}

async function handleAddLocation(e) {
    e.preventDefault();
    const name = document.getElementById('locName').value;
    const lat = parseFloat(document.getElementById('locLat').value);
    const lng = parseFloat(document.getElementById('locLng').value);
    const fill = parseFloat(document.getElementById('locFill').value);
    const priority = parseInt(document.getElementById('locPriority').value);

    try {
        const response = await fetch('/api/locations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                location_name: name,
                latitude: lat,
                longitude: lng,
                current_fill_level: fill,
                current_weight_kg: fill * 1.2,
                priority: priority
            })
        });

        const data = await response.json();
        if (data.success) {
            document.getElementById('addLocationForm').reset();
            switchTab('sequence');
            loadLocations();
            alert('Collection point added successfully!');
        } else {
            alert('Error adding location: ' + data.message);
        }
    } catch (err) {
        alert('Communication error: ' + err.message);
    }
}

async function deleteLocation(id) {
    if (!confirm('Are you sure you want to delete this collection point?')) return;
    try {
        await fetch(`/api/locations/${id}`, { method: 'DELETE' });
        loadLocations();
    } catch (err) {
        alert('Error deleting location: ' + err.message);
    }
}

async function calculateOptimizedRoute() {
    const listContainer = document.getElementById('routeSequenceList');
    listContainer.innerHTML = '<p class="text-center"><div class="spinner"></div>Computing optimal route sequence...</p>';

    try {
        const response = await fetch('/api/optimize_route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            renderRouteResults(data);
        } else {
            listContainer.innerHTML = `<p class="text-danger text-center">${data.message}</p>`;
        }
    } catch (err) {
        listContainer.innerHTML = `<p class="text-danger text-center">Error calculating route: ${err.message}</p>`;
    }
}

function renderRouteResults(data) {
    // 1. Update Metric Cards
    document.getElementById('metricDistance').textContent = `${data.total_distance_km} km`;
    document.getElementById('metricTime').textContent = `${data.estimated_time_mins} mins`;
    document.getElementById('metricFuel').textContent = `${data.fuel_used_liters} L`;
    document.getElementById('metricBins').textContent = `${data.visited_bins_count} Bins`;

    // 2. Render Sequence List
    const listContainer = document.getElementById('routeSequenceList');
    listContainer.innerHTML = data.stops.map(stop => `
        <div class="seq-step-item">
            <span class="seq-number">${stop.stop_number}</span>
            <div class="seq-info">
                <strong>${stop.name}</strong>
                <span class="seq-dist">+${stop.distance_from_prev_km} km from prev</span>
            </div>
            ${stop.fill_level !== undefined ? `<span class="fill-pill fill-${getFillClass(stop.fill_level)}">${stop.fill_level}%</span>` : ''}
        </div>
    `).join('');

    // 3. Draw Polyline Route on Map
    if (routePolyline) {
        map.removeLayer(routePolyline);
    }

    const latLngs = data.stops.map(s => [s.latitude, s.longitude]);
    routePolyline = L.polyline(latLngs, {
        color: '#3b82f6',
        weight: 4,
        opacity: 0.8,
        dashArray: '8, 6'
    }).addTo(map);

    // Zoom map to fit calculated route bounds
    map.fitBounds(routePolyline.getBounds(), { padding: [30, 30] });
}

function switchTab(tabName) {
    const seqTab = document.getElementById('sequenceTab');
    const addTab = document.getElementById('addLocationTab');
    const seqBtn = document.getElementById('tabSeqBtn');
    const addBtn = document.getElementById('tabAddBtn');

    if (tabName === 'sequence') {
        seqTab.classList.remove('hidden');
        addTab.classList.add('hidden');
        seqBtn.classList.add('active');
        addBtn.classList.remove('active');
    } else {
        seqTab.classList.add('hidden');
        addTab.classList.remove('hidden');
        seqBtn.classList.remove('active');
        addBtn.classList.add('active');
    }
}
